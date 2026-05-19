import asyncio
import logging
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from sqlmodel import Session, select

from .models import Offer, PendingOffer, School

logger = logging.getLogger(__name__)

SCHOLARSHIP_KW = ["scholarship", "bursary", "award", "grant", "financial aid", "học bổng"]
DISCOUNT_KW    = ["discount", "reduction", "off tuition", "early enroll", "sibling", "giảm giá"]
WAIVER_KW      = ["waiver", "fee waiver", "complimentary", "free transport", "miễn"]
DEADLINE_KW    = ["deadline", "before", "by ", "expires", "closing date", "hạn"]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; HanoiSchoolsBot/1.0; "
        "+https://hanoischoolsreview.com/bot)"
    )
}


def refresh_offer_status(engine) -> None:
    """Auto-expire offers past their deadline."""
    with Session(engine) as session:
        offers = session.exec(select(Offer)).all()
        now = datetime.utcnow().date().isoformat()
        for offer in offers:
            offer.active = offer.deadline >= now
            offer.last_verified_at = datetime.utcnow()
            session.add(offer)
        session.commit()


def run_scraper(engine) -> dict:
    """Synchronous wrapper — called from APScheduler."""
    return asyncio.run(_scrape_all(engine))


async def _scrape_all(engine) -> dict:
    with Session(engine) as session:
        schools = session.exec(select(School)).all()

    results = {"scraped": 0, "queued": 0, "errors": 0}
    async with httpx.AsyncClient(
        headers=_HEADERS,
        timeout=20.0,
        follow_redirects=True,
    ) as client:
        tasks = [_scrape_school(school, client) for school in schools if school.website_url]
        all_candidates = await asyncio.gather(*tasks, return_exceptions=True)

    with Session(engine) as session:
        for school, candidates in zip(
            [s for s in schools if s.website_url], all_candidates
        ):
            if isinstance(candidates, Exception):
                logger.warning("[scraper] %s failed: %s", school.name, candidates)
                results["errors"] += 1
                continue
            results["scraped"] += 1
            for c in candidates:
                # Skip if we already have a pending offer from same source
                existing = session.exec(
                    select(PendingOffer).where(
                        PendingOffer.school_id == school.id,
                        PendingOffer.source_url == c["source_url"],
                        PendingOffer.status == "pending",
                    )
                ).first()
                if existing:
                    continue
                pending = PendingOffer(
                    school_id=school.id,
                    title=c["title"],
                    raw_text=c["raw_text"][:1000],
                    source_url=c["source_url"],
                    offer_type=c["offer_type"],
                    confidence=c["confidence"],
                    detail=c["detail"],
                    deadline=c.get("deadline", ""),
                )
                session.add(pending)
                results["queued"] += 1
        session.commit()

    logger.info("[scraper] Done: %s", results)
    return results


async def _scrape_school(school: School, client: httpx.AsyncClient) -> list[dict]:
    candidates = []
    pages_checked: set = set()

    async def _check(url: str, depth: int = 0) -> None:
        if url in pages_checked or depth > 1:
            return
        pages_checked.add(url)
        try:
            resp = await client.get(url)
            resp.raise_for_status()
        except Exception as exc:
            logger.debug("[scraper] %s GET %s: %s", school.name, url, exc)
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        candidates.extend(_extract_candidates(soup, url))

        if depth == 0:
            for a in soup.find_all("a", href=True)[:80]:
                href = a["href"].lower()
                text = a.get_text(" ", strip=True).lower()
                if any(
                    kw in href or kw in text
                    for kw in [
                        "scholarship", "bursary", "promotion", "discount",
                        "offer", "fee", "admissions", "financial",
                    ]
                ):
                    full = urljoin(url, a["href"])
                    if _same_domain(url, full) and full not in pages_checked:
                        await _check(full, depth + 1)

    await _check(school.website_url)
    return candidates


def _extract_candidates(soup: BeautifulSoup, page_url: str) -> list[dict]:
    candidates = []
    all_kw = SCHOLARSHIP_KW + DISCOUNT_KW + WAIVER_KW

    for tag in soup.find_all(["p", "li", "div", "section", "article", "h2", "h3"], recursive=True):
        text = tag.get_text(" ", strip=True)
        if len(text) < 30 or len(text) > 800:
            continue
        text_lower = text.lower()

        matches = sum(1 for kw in all_kw if kw in text_lower)
        if matches == 0:
            continue

        offer_type, type_score = _classify(text_lower)
        confidence = min(1.0, (matches * 0.2 + type_score))

        # Boost for deadline info
        if any(kw in text_lower for kw in DEADLINE_KW):
            confidence = min(1.0, confidence + 0.15)

        # Boost for percentage or currency
        if re.search(r"\d+%|USD|\$|\d{1,3},\d{3}", text):
            confidence = min(1.0, confidence + 0.1)

        if confidence < 0.25:
            continue

        deadline = _extract_deadline(text)
        title = _make_title(text, offer_type)

        candidates.append({
            "title": title,
            "raw_text": text,
            "detail": text[:300],
            "source_url": page_url,
            "offer_type": offer_type,
            "confidence": round(confidence, 2),
            "deadline": deadline,
        })

    # Deduplicate by first 100 chars of text
    seen: set = set()
    unique = []
    for c in candidates:
        key = c["raw_text"][:100]
        if key not in seen:
            seen.add(key)
            unique.append(c)

    # Return top 5 by confidence
    return sorted(unique, key=lambda x: x["confidence"], reverse=True)[:5]


def _classify(text_lower: str) -> tuple[str, float]:
    if any(kw in text_lower for kw in SCHOLARSHIP_KW):
        return "Scholarship", 0.4
    if any(kw in text_lower for kw in DISCOUNT_KW):
        return "Discount", 0.35
    if any(kw in text_lower for kw in WAIVER_KW):
        return "Fee Waiver", 0.35
    return "Promotion", 0.2


def _extract_deadline(text: str) -> str:
    # Look for date patterns: "31 March 2026", "March 31, 2026", "31/03/2026"
    patterns = [
        r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b",
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d{2})\b",
        r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(0)
    return ""


def _make_title(text: str, offer_type: str) -> str:
    first_sentence = re.split(r"[.!?]", text)[0].strip()
    title = first_sentence[:80]
    if len(title) < 10:
        title = f"{offer_type} — see details"
    return title


def _same_domain(base: str, url: str) -> bool:
    try:
        return urlparse(base).netloc == urlparse(url).netloc
    except Exception:
        return False
