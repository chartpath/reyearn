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

import enum


class ClassTypes(enum.Enum):
    email = "email"


def upgrade():
    op.execute(
        """
        --sql
        --create classtypes enum type
        create type reyearn.classtypes as enum('email');
        """
    )
    op.alter_column(
        "classes",
        "type",
        schema="reyearn",
        type_=sa.Enum(ClassTypes, schema="reyearn"),
        postgresql_using="type::reyearn.classtypes",
        nullable=False,
    )


def downgrade():
    pass
