import uuid

from pydantic import BaseModel, Field


class AuthorityCreate(BaseModel):
    name: str
    department: str
    level: str
    boundary_id: uuid.UUID | None = None
    contact_email: str | None = None
    contact_phone: str | None = None


class AuthorityOut(BaseModel):
    id: uuid.UUID
    name: str
    department: str
    level: str
    boundary_id: uuid.UUID | None
    contact_email: str | None
    contact_phone: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class ResponsibilityMapCreate(BaseModel):
    category_code: str
    boundary_level: str | None = None
    authority_id: uuid.UUID
    priority: int = 0


class ResponsibilityMapOut(ResponsibilityMapCreate):
    id: uuid.UUID

    model_config = {"from_attributes": True}


class BoundaryCreate(BaseModel):
    name: str
    level: str
    district: str = "Tirunelveli"
    parent_id: uuid.UUID | None = None
    geojson: dict = Field(description="GeoJSON Polygon or MultiPolygon geometry")


class BoundaryOut(BaseModel):
    id: uuid.UUID
    name: str
    level: str
    district: str
    parent_id: uuid.UUID | None

    model_config = {"from_attributes": True}
