import enum
import sqlalchemy as sa
from sqlalchemy_utils import LtreeType

base_schema = "reyearn"
tenant_id = 0
default_tenant_schema = f"{base_schema}_tenant_{tenant_id}"

metadata = sa.MetaData()


class ClassTypes(enum.Enum):
    email: str = "email"  # e.g. RFC 2822


classes = sa.Table(
    "classes",
    metadata,
    sa.Column("type", sa.Enum(ClassTypes), nullable=False),
    sa.Column("label", LtreeType, unique=True, nullable=False),
    sa.PrimaryKeyConstraint("type", "label"),
    schema=base_schema,
)


class AnnotationStatus(enum.Enum):
    unknown: str = "unknown"
    predicted: str = "predicted"
    confirmed: str = "confirmed"
    rejected: str = "rejected"


annotations = sa.Table(
    "annotations",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column(
        "observation_hash",
        sa.String,
        sa.ForeignKey(f"{default_tenant_schema}.observations.hash", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "class_label",
        LtreeType,
        sa.ForeignKey(f"{base_schema}.classes.label", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "status", sa.Enum(AnnotationStatus), server_default="unknown", nullable=False
    ),
    sa.UniqueConstraint("observation_hash", "class_label"),
    schema=base_schema,
)

observations = sa.Table(
    "observations",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("text", sa.Text(), nullable=False),
    sa.Column("hash", sa.String(), unique=True, nullable=False),
    schema=default_tenant_schema,
)

experiments = sa.Table(
    "experiments",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(length=100), nullable=False),
    sa.Column("class_type", sa.Enum(ClassTypes), nullable=False),
    sa.Column("label_root", LtreeType, nullable=False),
    schema=base_schema,
)

models = sa.Table(
    "models",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("version", sa.String(length=30), nullable=False, unique=True),
    sa.Column("accuracy", sa.DECIMAL(precision=6, scale=5)),
    sa.Column("precision", sa.DECIMAL(precision=6, scale=5)),
    sa.Column("recall", sa.DECIMAL(precision=6, scale=5)),
    sa.Column("f1", sa.DECIMAL(precision=6, scale=5)),
    schema=base_schema,
)
