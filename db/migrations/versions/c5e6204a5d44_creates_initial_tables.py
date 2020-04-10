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

base_schema = "reyearn"
tenant_id = 0
default_tenant_schma = f"{base_schema}_tenant_{tenant_id}"


def upgrade():

    op.execute(
        f"""
        --sql --add main schma
        create schema if not exists {base_schema};
        --sql --add default tenant schema
        create schema if not exists {default_tenant_schma};
        --sql --add LTREE data type
        create extension if not exists ltree;
        """
    )

    op.create_table(
        "classes",
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("label", LtreeType, unique=True, nullable=False,),
        sa.PrimaryKeyConstraint("type", "label"),
        schema=base_schema,
    )

    op.create_table(
        "annotations",
        sa.Column("id", sa.Integer, primary_key=True),
        schema=base_schema,
    )

    op.create_table(
        "observations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("hash", sa.String(), unique=True, nullable=False),
        schema=default_tenant_schma,
    )


def downgrade():
    pass
