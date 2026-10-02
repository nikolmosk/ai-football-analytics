from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Competition(Base):
    __tablename__ = "competitions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    sport: Mapped[str] = mapped_column(String(32), default="football")
    seasons: Mapped[list["Season"]] = relationship(back_populates="competition", cascade="all, delete-orphan")
    matches: Mapped[list["Match"]] = relationship(back_populates="competition")


class Season(Base):
    __tablename__ = "seasons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"), index=True)
    provider_key: Mapped[str] = mapped_column(String(160), index=True)
    name: Mapped[str] = mapped_column(String(120))
    competition: Mapped[Competition] = relationship(back_populates="seasons")
    matches: Mapped[list["Match"]] = relationship(back_populates="season")
    __table_args__ = (UniqueConstraint("competition_id", "provider_key", name="uq_season_competition_provider"),)


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_key: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    home_matches: Mapped[list["Match"]] = relationship(back_populates="home_team", foreign_keys="Match.home_team_id")
    away_matches: Mapped[list["Match"]] = relationship(back_populates="away_team", foreign_keys="Match.away_team_id")
    match_stats: Mapped[list["TeamMatchStats"]] = relationship(back_populates="team")


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("provider", "provider_event_id", name="uq_match_provider_event"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(80), index=True)
    provider_event_id: Mapped[str] = mapped_column(String(160), index=True)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"), index=True)
    season_id: Mapped[int | None] = mapped_column(ForeignKey("seasons.id"), index=True, nullable=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    start_time_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(40), default="scheduled", index=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    competition: Mapped[Competition] = relationship(back_populates="matches")
    season: Mapped[Season | None] = relationship(back_populates="matches")
    home_team: Mapped[Team] = relationship(foreign_keys=[home_team_id], back_populates="home_matches")
    away_team: Mapped[Team] = relationship(foreign_keys=[away_team_id], back_populates="away_matches")
    odds: Mapped[list["OddsSnapshot"]] = relationship(back_populates="match", cascade="all, delete-orphan")
    team_stats: Mapped[list["TeamMatchStats"]] = relationship(back_populates="match", cascade="all, delete-orphan")


class OddsSnapshot(Base):
    __tablename__ = "odds_snapshots"
    __table_args__ = (
        UniqueConstraint("match_id", "bookmaker_key", "market_key", "selection", "point_key", "observed_at", name="uq_odds_observation"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    bookmaker_key: Mapped[str] = mapped_column(String(120), index=True)
    bookmaker_name: Mapped[str] = mapped_column(String(200))
    market_key: Mapped[str] = mapped_column(String(80), index=True)
    selection: Mapped[str] = mapped_column(String(200))
    point: Mapped[float | None] = mapped_column(Float, nullable=True)
    point_key: Mapped[str] = mapped_column(String(64), default="NULL", index=True)
    decimal_odds: Mapped[float] = mapped_column(Float)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw: Mapped[dict] = mapped_column(JSONB, default=dict)
    match: Mapped[Match] = relationship(back_populates="odds")


class TeamMatchStats(Base):
    __tablename__ = "team_match_stats"
    __table_args__ = (
        UniqueConstraint("match_id", "team_id", "source", name="uq_team_match_stats_source"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    source: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), default="VERIFIED", index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    goals_for: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goals_against: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shots: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shots_on_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    possession_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    corners: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fouls: Mapped[int | None] = mapped_column(Integer, nullable=True)
    yellow_cards: Mapped[int | None] = mapped_column(Integer, nullable=True)
    red_cards: Mapped[int | None] = mapped_column(Integer, nullable=True)
    xg: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw: Mapped[dict] = mapped_column(JSONB, default=dict)
    match: Mapped[Match] = relationship(back_populates="team_stats")
    team: Mapped[Team] = relationship(back_populates="match_stats")
