"""create initial tables

Revision ID: c5e6204a5d44
Revises: 
Create Date: 2020-03-31 22:10:16.707479

"""
from alembic import op
import sqlalchemy as sqla
from sqlalchemy_utils import LtreeType


# revision identifiers, used by Alembic.
revision = "c5e6204a5d44"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.execute(
        """
        --sql
        --add LTREE data type
        create extension if not exists ltree;
        """
    )

    op.create_table(
        "classes",
        sqla.Column("id", sqla.Integer, primary_key=True),
        sqla.Column("type", sqla.String(length=100)),
        sqla.Column("label", LtreeType),
    )

    op.create_table(
        "annotations", sqla.Column("id", sqla.Integer, primary_key=True),
    )

    op.create_table(
        "observations",
        sqla.Column("id", sqla.Integer, primary_key=True),
        sqla.Column("id", sqla.Integer, primary_key=True),
        sqla.Column("text", sqla.Text()),
    )


def downgrade():
    pass
