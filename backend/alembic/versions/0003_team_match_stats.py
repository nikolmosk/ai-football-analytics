"""v0.6 normalized team-match statistics.

Stores only provider-supplied observations. Missing metrics remain NULL.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_team_match_stats"
down_revision = "0002_normalized_ingestion"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "team_match_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("source", sa.String(120), nullable=False),
        sa.Column("status", sa.String(40), nullable=False, server_default="VERIFIED"),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("goals_for", sa.Integer(), nullable=True),
        sa.Column("goals_against", sa.Integer(), nullable=True),
        sa.Column("shots", sa.Integer(), nullable=True),
        sa.Column("shots_on_target", sa.Integer(), nullable=True),
        sa.Column("possession_pct", sa.Float(), nullable=True),
        sa.Column("corners", sa.Integer(), nullable=True),
        sa.Column("fouls", sa.Integer(), nullable=True),
        sa.Column("yellow_cards", sa.Integer(), nullable=True),
        sa.Column("red_cards", sa.Integer(), nullable=True),
        sa.Column("xg", sa.Float(), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("match_id", "team_id", "source", name="uq_team_match_stats_source"),
    )
    op.create_index("ix_team_match_stats_match_id", "team_match_stats", ["match_id"])
    op.create_index("ix_team_match_stats_team_id", "team_match_stats", ["team_id"])
    op.create_index("ix_team_match_stats_source", "team_match_stats", ["source"])
    op.create_index("ix_team_match_stats_status", "team_match_stats", ["status"])
    op.create_index("ix_team_match_stats_observed_at", "team_match_stats", ["observed_at"])


def downgrade():
    op.drop_index("ix_team_match_stats_observed_at", table_name="team_match_stats")
    op.drop_index("ix_team_match_stats_status", table_name="team_match_stats")
    op.drop_index("ix_team_match_stats_source", table_name="team_match_stats")
    op.drop_index("ix_team_match_stats_team_id", table_name="team_match_stats")
    op.drop_index("ix_team_match_stats_match_id", table_name="team_match_stats")
    op.drop_table("team_match_stats")
