"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("company_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("plan", sa.String(), nullable=False),
        sa.Column("stripe_customer_id", sa.String(), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(), nullable=True),
        sa.Column("slack_webhook_url", sa.String(), nullable=True),
        sa.Column("discord_webhook_url", sa.String(), nullable=True),
        sa.Column("notify_email", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customers_email", "customers", ["email"], unique=True)
    op.create_index("ix_customers_stripe_customer_id", "customers", ["stripe_customer_id"])

    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_customer_id", "users", ["customer_id"])

    op.create_table(
        "assets",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assets_customer_id", "assets", ["customer_id"])

    op.create_table(
        "scans",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("scan_type", sa.String(), nullable=False),
        sa.Column("plugin", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=True),
        sa.Column("requires_approval", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scans_asset_id", "scans", ["asset_id"])
    op.create_index("ix_scans_customer_id", "scans", ["customer_id"])

    op.create_table(
        "findings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("scan_id", sa.String(), nullable=False),
        sa.Column("fingerprint", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("finding_type", sa.String(), nullable=False),
        sa.Column("cvss_score", sa.Float(), nullable=True),
        sa.Column("cve_id", sa.String(), nullable=True),
        sa.Column("cwe_id", sa.String(), nullable=True),
        sa.Column("affected_resource", sa.String(), nullable=True),
        sa.Column("proof_of_concept", sa.String(), nullable=True),
        sa.Column("remediation", sa.String(), nullable=True),
        sa.Column("references", sa.JSON(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_by", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id", "fingerprint", name="uq_finding_customer_fingerprint"),
    )
    op.create_index("ix_findings_customer_id", "findings", ["customer_id"])
    op.create_index("ix_findings_asset_id", "findings", ["asset_id"])
    op.create_index("ix_findings_scan_id", "findings", ["scan_id"])
    op.create_index("ix_findings_fingerprint", "findings", ["fingerprint"])

    op.create_table(
        "scan_results",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("scan_id", sa.String(), nullable=False),
        sa.Column("raw_output", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scan_results_scan_id", "scan_results", ["scan_id"])


def downgrade() -> None:
    op.drop_table("scan_results")
    op.drop_table("findings")
    op.drop_table("scans")
    op.drop_table("assets")
    op.drop_table("users")
    op.drop_table("customers")
