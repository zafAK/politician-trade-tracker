from sqlalchemy import select

from .models import Politician
def get_or_create_politician(
        session,
        name,
        chamber) -> Politician:
    p = session.scalar(select(Politician).where(Politician.name == name))
    if p is None:
        p = Politician(name = name, chamber=chamber)
        session.add(p)
        session.flush()
    return p
    