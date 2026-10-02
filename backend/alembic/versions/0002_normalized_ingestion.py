"""v0.4 normalized ingestion schema.

Adds seasons and a non-null point key so NULL Asian/total points can participate
in deterministic uniqueness constraints.
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_normalized_ingestion"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("competition_id", sa.Integer(), sa.ForeignKey("competitions.id"), nullable=False),
        sa.Column("provider_key", sa.String(160), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.UniqueConstraint("competition_id", "provider_key", name="uq_season_competition_provider"),
    )
    op.create_index("ix_seasons_competition_id", "seasons", ["competition_id"])
    op.create_index("ix_seasons_provider_key", "seasons", ["provider_key"])

    op.add_column("matches", sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=True))
    op.create_index("ix_matches_season_id", "matches", ["season_id"])
    op.create_index("ix_matches_status", "matches", ["status"])

    op.add_column("odds_snapshots", sa.Column("point_key", sa.String(64), nullable=True))
    op.execute("UPDATE odds_snapshots SET point_key = CASE WHEN point IS NULL THEN 'NULL' ELSE to_char(point, 'FM999999990.000000') END")
    op.alter_column("odds_snapshots", "point_key", nullable=False, server_default="NULL")
    op.drop_constraint("uq_odds_observation", "odds_snapshots", type_="unique")
    op.create_unique_constraint(
        "uq_odds_observation",
        "odds_snapshots",
        ["match_id", "bookmaker_key", "market_key", "selection", "point_key", "observed_at"],
    )
    op.create_index("ix_odds_snapshots_point_key", "odds_snapshots", ["point_key"])


def downgrade():
    op.drop_index("ix_odds_snapshots_point_key", table_name="odds_snapshots")
    op.drop_constraint("uq_odds_observation", "odds_snapshots", type_="unique")
    op.create_unique_constraint(
        "uq_odds_observation", "odds_snapshots",
        ["match_id", "bookmaker_key", "market_key", "selection", "point", "observed_at"],
    )
    op.drop_column("odds_snapshots", "point_key")
    op.drop_index("ix_matches_status", table_name="matches")
    op.drop_index("ix_matches_season_id", table_name="matches")
    op.drop_column("matches", "season_id")
    op.drop_index("ix_seasons_provider_key", table_name="seasons")
    op.drop_index("ix_seasons_competition_id", table_name="seasons")
    op.drop_table("seasons")
