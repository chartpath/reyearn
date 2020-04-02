"""hooks up annotations

Revision ID: a16ca4c20de8
Revises: 7520bed9da33
Create Date: 2020-04-01 22:02:19.596433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a16ca4c20de8"
down_revision = "7520bed9da33"
branch_labels = None
depends_on = None

base_schema = "reyearn"
default_tenant_schema = f"{base_schema}_tenant_0"


def upgrade():

    with op.batch_alter_table("annotations", schema=base_schema) as batch_op:
        batch_op.add_column(
            sa.Column(
                "observation_id",
                sa.Integer,
                sa.ForeignKey(f"{default_tenant_schema}.observations.id"),
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "class_id",
                sa.Integer,
                sa.ForeignKey(f"{base_schema}.classes.id"),
                nullable=False,
            )
        )


def downgrade():
    pass
