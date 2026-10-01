"""Create FleetOps vehicle and maintenance job tables."""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("registration", sa.String(length=32), nullable=False),
        sa.Column("make", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.UniqueConstraint("registration"),
    )
    op.create_index("ix_vehicles_registration", "vehicles", ["registration"], unique=True)
    op.create_table(
        "maintenance_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
    )
    op.create_index("ix_maintenance_jobs_vehicle_id", "maintenance_jobs", ["vehicle_id"])
    op.create_index("ix_maintenance_jobs_status", "maintenance_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_maintenance_jobs_status", table_name="maintenance_jobs")
    op.drop_index("ix_maintenance_jobs_vehicle_id", table_name="maintenance_jobs")
    op.drop_table("maintenance_jobs")
    op.drop_index("ix_vehicles_registration", table_name="vehicles")
    op.drop_table("vehicles")
