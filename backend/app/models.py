

from datetime import date
from sqlalchemy import Date, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

class Politician(Base):
    __tablename__ = "politicians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    chamber: Mapped[str] = mapped_column(String) #house or senate
    party: Mapped[str | None] = mapped_column(String, nullable=True)

    trades: Mapped[list["Trade"]] = relationship(back_populates="politician")

class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    politician_id: Mapped[int] = mapped_column(ForeignKey("politicians.id"), index=True)
    transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ticker: Mapped[str] = mapped_column(String)
    min_amount: Mapped[int] = mapped_column(Integer)
    max_amount: Mapped[int] = mapped_column(Integer)
    asset_description: Mapped[str] = mapped_column(String, nullable=True)

    raw_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True) #Fixture

    politician: Mapped[Politician] = relationship(back_populates="trades")
    

