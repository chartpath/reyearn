"""create initial tables

Revision ID: c5e6204a5d44
Revises: 
Create Date: 2020-03-31 22:10:16.707479

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import LtreeType

print(op.get_context())

# revision identifiers, used by Alembic.
revision = "c5e6204a5d44"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.execute(
        f"""
        --sql --add schma
        create schema if not exists reyearn;
        --sql --add LTREE data type
        create extension if not exists ltree;
        """
    )

    op.create_table(
        "classes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type", sa.String(length=100)),
        sa.Column("label", LtreeType),
        schema="reyearn",
    )

    op.create_table(
        "annotations", sa.Column("id", sa.Integer, primary_key=True), schema="reyearn",
    )

    op.create_table(
        "observations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("text", sa.Text()),
        schema="reyearn",
    )


def downgrade():
    pass
