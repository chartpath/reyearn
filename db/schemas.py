import enum
import sqlalchemy as sa
from sqlalchemy_utils import LtreeType

base_schema = "reyearn"
tenant_id = 0
default_tenant_schema = f"{base_schema}_tenant_{tenant_id}"

metadata = sa.MetaData()


class ClassTypes(enum.Enum):
    email = "email"  # e.g. RFC 2822


classes = sa.Table(
    "classes",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("type", sa.Enum(ClassTypes)),
    sa.Column("label", LtreeType),
    schema=base_schema,
)

annotations = sa.Table(
    "annotations",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column(
        "observation_id",
        sa.Integer,
        sa.ForeignKey(f"{default_tenant_schema}.observations.id"),
        nullable=False,
    ),
    sa.Column(
        "class_id",
        sa.Integer,
        sa.ForeignKey(f"{base_schema}.classes.id"),
        nullable=False,
    ),
    schema=base_schema,
)

observations = sa.Table(
    "observations",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("text", sa.Text()),
    schema=default_tenant_schema,
)
