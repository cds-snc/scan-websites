from pydantic import BaseModel, AnyHttpUrl
from .common import as_form
from typing import List


class TemplateFilter(BaseModel):
    name: str

    class Config:
        orm_mode = True


@as_form
class TemplateCreate(TemplateFilter):
    class Config:
        extra = "forbid"

    pass


class TemplateScanType(BaseModel):
    scanType: str


class TemplateScanData(BaseModel):
    url: AnyHttpUrl


class TemplateScanCreateList(BaseModel):
    data: List[TemplateScanData]
    scan_types: List[TemplateScanType]
