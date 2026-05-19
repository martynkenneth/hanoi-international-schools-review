from datetime import datetime
from fastapi import FastAPI, Request, Depends, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, SQLModel, create_engine, select
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Optional

from .models import School, Offer, Lead
from .seed import seed_data
from .scraper import refresh_offer_status

DATABASE_URL = "sqlite:///./schools.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

app = FastAPI(title="Hanoi International Schools Review")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_data(session)
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(lambda: refresh_offer_status(engine), "interval", hours=6)
    scheduler.start()


# ── Homepage ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    schools = session.exec(select(School)).all()
    offers = session.exec(select(Offer).where(Offer.active == True)).all()  # noqa: E712
    school_map = {s.id: s for s in schools}
    faqs = [
        ("How do I shortlist schools in Hanoi?", "Start with curriculum, budget, and commute. Narrow to 3–4 schools, visit each, and compare total annual costs — not just tuition."),
        ("How often are offers updated?", "Offers are auto-checked every 6 hours and show a last-verified timestamp. School-confirmed offers are verified directly with admissions teams."),
        ("What costs matter beyond tuition?", "Budget for transport (up to $2,400/yr), uniforms ($300–600), meals ($800–1,200), activity/materials fees, and the one-off enrollment deposit."),
        ("Which curriculum is best for my child?", "IB suits globally mobile families and holistic learning. British/IGCSE is ideal for UK university pathways. AP is best for US college-bound students. French Bac for French-speaking families."),
    ]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "schools": schools,
            "offers": offers[:4],
            "school_map": school_map,
            "faqs": faqs,
            "year": datetime.utcnow().year,
            "active_page": "home",
        },
    )


# ── City hub ──────────────────────────────────────────────────────────────────

@app.get("/hanoi/", response_class=HTMLResponse)
def hanoi_hub(request: Request, session: Session = Depends(get_session)):
    schools = session.exec(select(School)).all()
    offers = session.exec(select(Offer).where(Offer.active == True)).all()  # noqa: E712
    return templates.TemplateResponse(
        "hanoi_hub.html",
        {
            "request": request,
            "schools": schools,
            "offers": offers,
            "year": datetime.utcnow().year,
            "active_page": "hanoi",
        },
    )


# ── School directory ──────────────────────────────────────────────────────────

@app.get("/hanoi/schools/", response_class=HTMLResponse)
def school_directory(
    request: Request,
    session: Session = Depends(get_session),
    district: Optional[str] = Query(None),
    curriculum: Optional[str] = Query(None),
):
    query = select(School)
    schools = session.exec(query).all()

    if district:
        schools = [s for s in schools if district.lower() in s.district.lower()]
    if curriculum:
        schools = [s for s in schools if curriculum.lower() in s.curriculum.lower()]

    districts = sorted(set(s.district for s in session.exec(select(School)).all()))
    curricula = ["IB", "British", "AP", "French"]

    return templates.TemplateResponse(
        "schools.html",
        {
            "request": request,
            "schools": schools,
            "districts": districts,
            "curricula": curricula,
            "selected_district": district or "",
            "selected_curriculum": curriculum or "",
            "year": datetime.utcnow().year,
            "active_page": "schools",
        },
    )


# ── School profile ────────────────────────────────────────────────────────────

@app.get("/hanoi/schools/{slug}", response_class=HTMLResponse)
def school_profile(slug: str, request: Request, session: Session = Depends(get_session)):
    school = session.exec(select(School).where(School.slug == slug)).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    offers = session.exec(
        select(Offer).where(Offer.school_id == school.id, Offer.active == True)  # noqa: E712
    ).all()
    all_schools = session.exec(select(School)).all()
    other_schools = [s for s in all_schools if s.id != school.id]

    facilities = [f.strip() for f in school.facilities.split("|") if f.strip()]
    pros = [p.strip() for p in school.pros.split("|") if p.strip()]
    cons = [c.strip() for c in school.cons.split("|") if c.strip()]
    timeline = [t.strip() for t in school.admissions_timeline.split("|") if t.strip()]
    documents = [d.strip() for d in school.required_documents.split("|") if d.strip()]

    faq_qs = [q.strip() for q in school.faq_questions.split("|") if q.strip()]
    faq_as = [a.strip() for a in school.faq_answers.split("|") if a.strip()]
    faqs = list(zip(faq_qs, faq_as))

    return templates.TemplateResponse(
        "school.html",
        {
            "request": request,
            "school": school,
            "offers": offers,
            "other_schools": other_schools[:3],
            "facilities": facilities,
            "pros": pros,
            "cons": cons,
            "timeline": timeline,
            "documents": documents,
            "faqs": faqs,
            "year": datetime.utcnow().year,
            "active_page": "schools",
        },
    )


# ── Promotions hub ────────────────────────────────────────────────────────────

@app.get("/hanoi/promotions/", response_class=HTMLResponse)
def promotions(
    request: Request,
    session: Session = Depends(get_session),
    offer_type: Optional[str] = Query(None),
    school_id: Optional[int] = Query(None),
):
    query = select(Offer).where(Offer.active == True)  # noqa: E712
    offers = session.exec(query).all()
    schools = session.exec(select(School)).all()
    school_map = {s.id: s for s in schools}

    if offer_type:
        offers = [o for o in offers if o.offer_type == offer_type]
    if school_id:
        offers = [o for o in offers if o.school_id == school_id]

    offer_types = sorted(set(
        o.offer_type for o in session.exec(select(Offer).where(Offer.active == True)).all()  # noqa: E712
    ))

    return templates.TemplateResponse(
        "promotions.html",
        {
            "request": request,
            "offers": offers,
            "schools": schools,
            "school_map": school_map,
            "offer_types": offer_types,
            "selected_type": offer_type or "",
            "selected_school": school_id or 0,
            "year": datetime.utcnow().year,
            "active_page": "promotions",
        },
    )


# ── Compare tool ──────────────────────────────────────────────────────────────

@app.get("/hanoi/compare/", response_class=HTMLResponse)
def compare(
    request: Request,
    session: Session = Depends(get_session),
    schools: Optional[str] = Query(None),
    s0: Optional[str] = Query(None),
    s1: Optional[str] = Query(None),
    s2: Optional[str] = Query(None),
    s3: Optional[str] = Query(None),
):
    all_schools = session.exec(select(School)).all()
    compared = []

    # Support both ?schools=a,b,c and ?s0=a&s1=b forms
    slugs_str = schools or ""
    if not slugs_str:
        parts = [p for p in [s0, s1, s2, s3] if p]
        slugs_str = ",".join(parts)

    if slugs_str:
        slugs = [s.strip() for s in slugs_str.split(",") if s.strip()][:4]
        slug_map = {s.slug: s for s in all_schools}
        compared = [slug_map[slug] for slug in slugs if slug in slug_map]

    return templates.TemplateResponse(
        "compare.html",
        {
            "request": request,
            "all_schools": all_schools,
            "compared": compared,
            "selected_slugs": slugs_str,
            "year": datetime.utcnow().year,
            "active_page": "compare",
        },
    )


# ── Lead capture ──────────────────────────────────────────────────────────────

@app.post("/leads")
def capture_lead(
    name: str = Form(...),
    email: str = Form(...),
    child_age: str = Form(...),
    session: Session = Depends(get_session),
):
    lead = Lead(name=name, email=email, child_age=child_age)
    session.add(lead)
    session.commit()
    return RedirectResponse("/?success=1#lead", status_code=303)


# ── Admin ─────────────────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, session: Session = Depends(get_session)):
    offers = session.exec(select(Offer)).all()
    schools = session.exec(select(School)).all()
    school_map = {s.id: s for s in schools}
    leads = session.exec(select(Lead).order_by(Lead.created_at.desc()).limit(20)).all()
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "offers": offers,
            "school_map": school_map,
            "leads": leads,
            "year": datetime.utcnow().year,
        },
    )


@app.post("/admin/offers/{offer_id}/verify")
def verify_offer(offer_id: int, session: Session = Depends(get_session)):
    offer = session.get(Offer, offer_id)
    if offer:
        offer.verification_status = "School-confirmed"
        offer.last_verified_at = datetime.utcnow()
        offer.active = True
        session.add(offer)
        session.commit()
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/offers/{offer_id}/deactivate")
def deactivate_offer(offer_id: int, session: Session = Depends(get_session)):
    offer = session.get(Offer, offer_id)
    if offer:
        offer.active = False
        session.add(offer)
        session.commit()
    return RedirectResponse("/admin", status_code=303)
