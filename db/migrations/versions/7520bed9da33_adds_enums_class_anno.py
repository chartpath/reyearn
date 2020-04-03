"""add type enum

Revision ID: 7520bed9da33
Revises: c5e6204a5d44
Create Date: 2020-04-01 14:52:28.365052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7520bed9da33"
down_revision = "c5e6204a5d44"
branch_labels = None
depends_on = None

base_schema = "reyearn"

import enum


class ClassTypes(enum.Enum):
    email = "email"


class AnnotationStatus(enum.Enum):
    unknown: str = "unknown"
    predicted: str = "predicted"
    confirmed: str = "confirmed"
    rejected: str = "rejected"


def upgrade():
    op.execute(
        f"""
        --sql
        --create classtypes enum type
        create type {base_schema}.classtypes as enum('email');
        --sql
        --create annotationstatus enum type
        create type {base_schema}.annotationstatus 
            as enum('unknown', 'predicted', 'confirmed', 'rejected');
        """
    )
    op.alter_column(
        "classes",
        "type",
        schema=base_schema,
        type_=sa.Enum(ClassTypes, schema=base_schema),
        postgresql_using=f"type::{base_schema}.classtypes",
        nullable=False,
    )
    op.add_column(
        "annotations",
        sa.Column(
            "status",
            sa.Enum(AnnotationStatus, schema=base_schema),
            server_default="unknown",
        ),
        schema=base_schema,
    )


def downgrade():
    pass
