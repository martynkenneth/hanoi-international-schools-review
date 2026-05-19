from sqlmodel import Session, select
from .models import School, Offer


def seed_data(session: Session):
    if session.exec(select(School)).first():
        return

    schools = [
        School(name="UNIS Hanoi", slug="unis-hanoi", curriculum="IB PYP/MYP/DP", tuition_range="$15,000-$35,000", district="Tay Ho", image_url="https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1200&q=60", summary="Best for full IB continuity and global mobility families."),
        School(name="BIS Hanoi", slug="bis-hanoi", curriculum="British + IGCSE + IB", tuition_range="$18,000-$32,000", district="Long Bien", image_url="https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=1200&q=60", summary="Strong UK pathway with IB option in senior years."),
    ]
    for s in schools:
        session.add(s)
    session.commit()

    loaded = session.exec(select(School)).all()
    offers = [
        Offer(school_id=loaded[0].id, title="Merit scholarship 2026", offer_type="Scholarship", detail="Partial scholarship for Grade 9 entry.", deadline="2026-07-15", source_url="https://example.com/unis"),
        Offer(school_id=loaded[1].id, title="Early enrollment discount", offer_type="Discount", detail="5% tuition reduction before June 30, 2026.", deadline="2026-06-30", source_url="https://example.com/bis"),
    ]
    for o in offers:
        session.add(o)
    session.commit()
