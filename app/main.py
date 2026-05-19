import threading
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, Depends, Form, Query, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, SQLModel, create_engine, select
from apscheduler.schedulers.background import BackgroundScheduler

from .models import School, Offer, Lead, PendingOffer
from .seed import seed_data
from .scraper import refresh_offer_status, run_scraper
from . import auth, email as mailer

DATABASE_URL = "sqlite:///./schools.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

app = FastAPI(title="Hanoi International Schools Review")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_session():
    with Session(engine) as session:
        yield session


def _admin_required(request: Request, admin_token: Optional[str] = Cookie(default=None)):
    if not auth.is_authenticated(admin_token):
        raise HTTPException(status_code=302, headers={"Location": "/admin/login"})
    return admin_token


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_data(session)
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(lambda: refresh_offer_status(engine), "interval", hours=6)
    scheduler.add_job(lambda: run_scraper(engine), "interval", hours=24)
    scheduler.start()


# ── Homepage ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    schools = session.exec(select(School)).all()
    offers = session.exec(select(Offer).where(Offer.active == True)).all()  # noqa: E712
    school_map = {s.id: s for s in schools}
    faqs = [
        ("How do I shortlist international schools in Hanoi?",
         "Start with curriculum (IB, British, AP, French), then filter by budget, district, and age range. Visit 3–4 shortlisted schools and compare total annual costs — not just tuition."),
        ("How often are offers and scholarships updated?",
         "Offers are auto-checked every 6 hours and display a last-verified timestamp. School-confirmed offers have been verified directly with admissions teams."),
        ("What costs matter beyond tuition?",
         "Budget for transport ($800–2,400/yr), uniforms ($300–600), meals ($800–1,200), activity fees, and a one-off enrolment deposit ($1,000–5,000)."),
        ("Which curriculum is best for my child?",
         "IB suits globally mobile families and holistic learners. British / IGCSE is ideal for UK university pathways. AP is best for US-college-bound students. French Bac for French-speaking families."),
    ]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "schools": schools,
        "offers": offers[:4],
        "school_map": school_map,
        "faqs": faqs,
        "year": datetime.utcnow().year,
        "active_page": "home",
    })


# ── City hub ──────────────────────────────────────────────────────────────────

@app.get("/hanoi/", response_class=HTMLResponse)
def hanoi_hub(request: Request, session: Session = Depends(get_session)):
    schools = session.exec(select(School)).all()
    offers = session.exec(select(Offer).where(Offer.active == True)).all()  # noqa: E712
    return templates.TemplateResponse("hanoi_hub.html", {
        "request": request, "schools": schools, "offers": offers,
        "year": datetime.utcnow().year, "active_page": "hanoi",
    })


# ── School directory ──────────────────────────────────────────────────────────

@app.get("/hanoi/schools/", response_class=HTMLResponse)
def school_directory(
    request: Request,
    session: Session = Depends(get_session),
    district: Optional[str] = Query(None),
    curriculum: Optional[str] = Query(None),
):
    all_schools = session.exec(select(School)).all()
    schools = all_schools

    if district:
        schools = [s for s in schools if district.lower() in s.district.lower()]
    if curriculum:
        schools = [s for s in schools if curriculum.lower() in s.curriculum.lower()]

    districts = sorted(set(s.district for s in all_schools))
    curricula = ["IB", "British", "AP", "Canadian", "French", "Australian", "Bilingual"]

    return templates.TemplateResponse("schools.html", {
        "request": request, "schools": schools, "districts": districts,
        "curricula": curricula, "selected_district": district or "",
        "selected_curriculum": curriculum or "",
        "year": datetime.utcnow().year, "active_page": "schools",
    })


# ── School profile ────────────────────────────────────────────────────────────

@app.get("/hanoi/schools/{slug}", response_class=HTMLResponse)
def school_profile(slug: str, request: Request, session: Session = Depends(get_session)):
    school = session.exec(select(School).where(School.slug == slug)).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    offers = session.exec(
        select(Offer).where(Offer.school_id == school.id, Offer.active == True)  # noqa: E712
    ).all()
    other_schools = [s for s in session.exec(select(School)).all() if s.id != school.id][:3]

    def split(val): return [x.strip() for x in val.split("|") if x.strip()]

    faq_qs = split(school.faq_questions)
    faq_as = split(school.faq_answers)
    faqs = list(zip(faq_qs, faq_as))

    return templates.TemplateResponse("school.html", {
        "request": request, "school": school, "offers": offers,
        "other_schools": other_schools, "faqs": faqs,
        "facilities": split(school.facilities),
        "pros": split(school.pros),
        "cons": split(school.cons),
        "timeline": split(school.admissions_timeline),
        "documents": split(school.required_documents),
        "year": datetime.utcnow().year, "active_page": "schools",
    })


# ── Promotions hub ────────────────────────────────────────────────────────────

@app.get("/hanoi/promotions/", response_class=HTMLResponse)
def promotions(
    request: Request, session: Session = Depends(get_session),
    offer_type: Optional[str] = Query(None),
    school_id: Optional[int] = Query(None),
):
    all_active = session.exec(select(Offer).where(Offer.active == True)).all()  # noqa: E712
    schools = session.exec(select(School)).all()
    school_map = {s.id: s for s in schools}

    offers = all_active
    if offer_type:
        offers = [o for o in offers if o.offer_type == offer_type]
    if school_id:
        offers = [o for o in offers if o.school_id == school_id]

    offer_types = sorted(set(o.offer_type for o in all_active))

    return templates.TemplateResponse("promotions.html", {
        "request": request, "offers": offers, "schools": schools,
        "school_map": school_map, "offer_types": offer_types,
        "selected_type": offer_type or "", "selected_school": school_id or 0,
        "year": datetime.utcnow().year, "active_page": "promotions",
    })


# ── Compare ───────────────────────────────────────────────────────────────────

@app.get("/hanoi/compare/", response_class=HTMLResponse)
def compare(
    request: Request, session: Session = Depends(get_session),
    schools: Optional[str] = Query(None),
    s0: Optional[str] = Query(None), s1: Optional[str] = Query(None),
    s2: Optional[str] = Query(None), s3: Optional[str] = Query(None),
):
    all_schools = session.exec(select(School)).all()

    slugs_str = schools or ""
    if not slugs_str:
        parts = [p for p in [s0, s1, s2, s3] if p]
        slugs_str = ",".join(parts)

    compared = []
    if slugs_str:
        slugs = [s.strip() for s in slugs_str.split(",") if s.strip()][:4]
        slug_map = {s.slug: s for s in all_schools}
        compared = [slug_map[slug] for slug in slugs if slug in slug_map]

    return templates.TemplateResponse("compare.html", {
        "request": request, "all_schools": all_schools, "compared": compared,
        "selected_slugs": slugs_str,
        "year": datetime.utcnow().year, "active_page": "compare",
    })


# ── Guides ────────────────────────────────────────────────────────────────────

@app.get("/hanoi/guides/", response_class=HTMLResponse)
def guides_index(request: Request, session: Session = Depends(get_session)):
    return templates.TemplateResponse("guides/index.html", {
        "request": request, "year": datetime.utcnow().year, "active_page": "guides",
    })


@app.get("/hanoi/guides/ib-vs-british-vs-ap", response_class=HTMLResponse)
def guide_curriculum(request: Request):
    return templates.TemplateResponse("guides/curriculum.html", {
        "request": request, "year": datetime.utcnow().year, "active_page": "guides",
    })


@app.get("/hanoi/guides/total-cost-of-international-school-hanoi", response_class=HTMLResponse)
def guide_total_cost(request: Request):
    return templates.TemplateResponse("guides/total_cost.html", {
        "request": request, "year": datetime.utcnow().year, "active_page": "guides",
    })


@app.get("/hanoi/guides/admissions-checklist", response_class=HTMLResponse)
def guide_admissions(request: Request):
    return templates.TemplateResponse("guides/admissions_checklist.html", {
        "request": request, "year": datetime.utcnow().year, "active_page": "guides",
    })


@app.get("/hanoi/guides/schools-by-district", response_class=HTMLResponse)
def guide_districts(request: Request, session: Session = Depends(get_session)):
    schools = session.exec(select(School)).all()
    by_district: dict = {}
    for s in schools:
        by_district.setdefault(s.district, []).append(s)
    return templates.TemplateResponse("guides/districts.html", {
        "request": request, "by_district": by_district,
        "year": datetime.utcnow().year, "active_page": "guides",
    })


# ── Lead capture ──────────────────────────────────────────────────────────────

@app.post("/leads")
def capture_lead(
    name: str = Form(...), email: str = Form(...), child_age: str = Form(...),
    session: Session = Depends(get_session),
):
    lead = Lead(name=name, email=email, child_age=child_age)
    session.add(lead)
    session.commit()
    # Send emails in background thread so response is immediate
    threading.Thread(target=mailer.send_lead_welcome, args=(name, email, child_age), daemon=True).start()
    threading.Thread(target=mailer.send_admin_new_lead, args=(name, email, child_age), daemon=True).start()
    return RedirectResponse("/?success=1#lead", status_code=303)


# ── Admin auth ────────────────────────────────────────────────────────────────

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request, error: Optional[str] = Query(None)):
    return templates.TemplateResponse("admin_login.html", {
        "request": request, "error": error, "year": datetime.utcnow().year,
    })


@app.post("/admin/login")
def admin_login(
    username: str = Form(...), password: str = Form(...),
):
    token = auth.login(username, password)
    if not token:
        return RedirectResponse("/admin/login?error=1", status_code=303)
    response = RedirectResponse("/admin", status_code=303)
    response.set_cookie("admin_token", token, httponly=True, samesite="lax", max_age=86400)
    return response


@app.get("/admin/logout")
def admin_logout(admin_token: Optional[str] = Cookie(default=None)):
    auth.logout(admin_token)
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie("admin_token")
    return response


# ── Admin dashboard ───────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
def admin(
    request: Request, session: Session = Depends(get_session),
    admin_token: Optional[str] = Cookie(default=None),
):
    if not auth.is_authenticated(admin_token):
        return RedirectResponse("/admin/login", status_code=303)

    offers = session.exec(select(Offer)).all()
    schools = session.exec(select(School)).all()
    school_map = {s.id: s for s in schools}
    leads = session.exec(select(Lead).order_by(Lead.created_at.desc()).limit(20)).all()
    pending = session.exec(
        select(PendingOffer).where(PendingOffer.status == "pending")
        .order_by(PendingOffer.confidence.desc())
    ).all()

    return templates.TemplateResponse("admin.html", {
        "request": request, "offers": offers, "school_map": school_map,
        "leads": leads, "pending": pending,
        "year": datetime.utcnow().year,
    })


@app.post("/admin/offers/{offer_id}/verify")
def verify_offer(
    offer_id: int, session: Session = Depends(get_session),
    admin_token: Optional[str] = Cookie(default=None),
):
    if not auth.is_authenticated(admin_token):
        return RedirectResponse("/admin/login", status_code=303)
    offer = session.get(Offer, offer_id)
    if offer:
        offer.verification_status = "School-confirmed"
        offer.last_verified_at = datetime.utcnow()
        offer.active = True
        session.add(offer)
        session.commit()
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/offers/{offer_id}/deactivate")
def deactivate_offer(
    offer_id: int, session: Session = Depends(get_session),
    admin_token: Optional[str] = Cookie(default=None),
):
    if not auth.is_authenticated(admin_token):
        return RedirectResponse("/admin/login", status_code=303)
    offer = session.get(Offer, offer_id)
    if offer:
        offer.active = False
        session.add(offer)
        session.commit()
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/pending/{pending_id}/approve")
def approve_pending(
    pending_id: int, session: Session = Depends(get_session),
    admin_token: Optional[str] = Cookie(default=None),
):
    if not auth.is_authenticated(admin_token):
        return RedirectResponse("/admin/login", status_code=303)
    pending = session.get(PendingOffer, pending_id)
    if pending:
        offer = Offer(
            school_id=pending.school_id,
            title=pending.title,
            offer_type=pending.offer_type,
            detail=pending.detail or pending.raw_text[:300],
            deadline=pending.deadline or "2026-12-31",
            source_url=pending.source_url,
            verification_status="Source-verified",
        )
        session.add(offer)
        pending.status = "approved"
        session.add(pending)
        session.commit()
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/pending/{pending_id}/reject")
def reject_pending(
    pending_id: int, session: Session = Depends(get_session),
    admin_token: Optional[str] = Cookie(default=None),
):
    if not auth.is_authenticated(admin_token):
        return RedirectResponse("/admin/login", status_code=303)
    pending = session.get(PendingOffer, pending_id)
    if pending:
        pending.status = "rejected"
        session.add(pending)
        session.commit()
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/scraper/run")
def trigger_scraper(admin_token: Optional[str] = Cookie(default=None)):
    if not auth.is_authenticated(admin_token):
        return RedirectResponse("/admin/login", status_code=303)
    threading.Thread(target=run_scraper, args=(engine,), daemon=True).start()
    return RedirectResponse("/admin?scraped=1", status_code=303)
