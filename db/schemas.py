import enum
import sqlalchemy as sa
from sqlalchemy_utils import LtreeType

base_schema = "reyearn"
tenant_id = 0

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
    schema=base_schema,
)

observations = sa.Table(
    "observations",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("text", sa.Text()),
    schema=f"{base_schema}_tenant_{tenant_id}",
)
