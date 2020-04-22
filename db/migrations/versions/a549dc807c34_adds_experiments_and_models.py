"""adds experiments and models

Revision ID: a549dc807c34
Revises: a16ca4c20de8
Create Date: 2020-04-02 01:03:06.734885

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = "a549dc807c34"
down_revision = "a16ca4c20de8"
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "experiments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("class_type", sa.Enum("email", name="classtypes"), nullable=False),
        sa.Column(
            "label_root", sqlalchemy_utils.types.ltree.LtreeType(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.Column(
            "time_created", sa.DateTime(timezone=True), server_default=func.now()
        ),
        sa.Column("time_updated", sa.DateTime(timezone=True), onupdate=func.now()),
        schema="reyearn",
    )
    op.create_table(
        "models",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(length=30), nullable=False),
        sa.Column("accuracy", sa.DECIMAL(precision=6, scale=5), nullable=True),
        sa.Column("precision", sa.DECIMAL(precision=6, scale=5), nullable=True),
        sa.Column("recall", sa.DECIMAL(precision=6, scale=5), nullable=True),
        sa.Column("f1", sa.DECIMAL(precision=6, scale=5), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("version"),
        sa.Column(
            "time_created", sa.DateTime(timezone=True), server_default=func.now()
        ),
        sa.Column("time_updated", sa.DateTime(timezone=True), onupdate=func.now()),
        schema="reyearn",
    )


def downgrade():
    pass
