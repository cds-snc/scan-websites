from pydantic import BaseModel
from .common import as_form


class TemplateFilter(BaseModel):
    name: str

    class Config:
        orm_mode = True


@as_form
class TemplateCreate(TemplateFilter):
    class Config:
        extra = "forbid"

    pass
