
import sqlahelper
import sqlalchemy as sa

Base = sqlahelper.get_base()

class A10TenantBinding(Base):
    __tablename__ = "a10_tenant_bindings"

    id = sa.Column(sa.Integer, primary_key=True)
    project_id = sa.Column(sa.String(36), nullable=False)
    device_name = sa.Column(sa.String(1024), nullable=False)
