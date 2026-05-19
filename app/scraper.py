from datetime import datetime
from sqlmodel import Session, select
from .models import Offer


def refresh_offer_status(engine):
    with Session(engine) as session:
        offers = session.exec(select(Offer)).all()
        now = datetime.utcnow().date().isoformat()
        for offer in offers:
            offer.active = offer.deadline >= now
            offer.last_verified_at = datetime.utcnow()
            session.add(offer)
        session.commit()
