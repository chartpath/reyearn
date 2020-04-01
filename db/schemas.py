import enum
import sqlalchemy as sa
from sqlalchemy_utils import LtreeType


metadata = sa.MetaData()


class ClassTypes(enum.Enum):
    email = "email"  # e.g. RFC 2822


classes = sa.Table(
    "classes",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("type", sa.Enum(ClassTypes)),
    sa.Column("label", LtreeType),
)

annotations = sa.Table(
    "annotations",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    # sa.Column("class_id", sa.ForeignKey())
)

observations = sa.Table(
    "observations",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("text", sa.Text()),
)
