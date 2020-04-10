"""hooks up annotations

Revision ID: a16ca4c20de8
Revises: 7520bed9da33
Create Date: 2020-04-01 22:02:19.596433

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import LtreeType


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
                "observation_hash",
                sa.String,
                sa.ForeignKey(
                    f"{default_tenant_schema}.observations.hash", ondelete="CASCADE",
                ),
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "class_label",
                LtreeType,
                sa.ForeignKey(f"{base_schema}.classes.label", ondelete="CASCADE",),
                nullable=False,
            )
        )
        batch_op.create_unique_constraint(None, ["observation_hash", "class_label"])


def downgrade():
    pass
