from datetime import datetime
from fastapi import FastAPI, Request, Depends, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, SQLModel, create_engine, select
from apscheduler.schedulers.background import BackgroundScheduler

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


@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    schools = session.exec(select(School)).all()
    offers = session.exec(select(Offer).where(Offer.active == True)).all()  # noqa: E712
    faqs = [
        ("How do I shortlist schools in Hanoi?", "Start with curriculum, budget, and commute constraints, then compare 3-4 schools."),
        ("How often are offers updated?", "Offers are auto-checked every 6 hours and show a last-verified timestamp."),
        ("What costs matter beyond tuition?", "Include transport, uniforms, meals, enrollment, and activity fees."),
    ]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "schools": schools,
            "offers": offers,
            "faqs": faqs,
            "year": datetime.utcnow().year,
        },
    )


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, session: Session = Depends(get_session)):
    offers = session.exec(select(Offer)).all()
    return templates.TemplateResponse("admin.html", {"request": request, "offers": offers})


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


@app.post("/leads")
def capture_lead(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    child_age: str = Form(...),
    session: Session = Depends(get_session),
):
    lead = Lead(name=name, email=email, child_age=child_age)
    session.add(lead)
    session.commit()
    background_tasks.add_task(lambda: None)
    return RedirectResponse("/?success=1#lead", status_code=303)
