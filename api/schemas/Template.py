from pydantic import BaseModel, AnyHttpUrl
from typing import List, Optional


class TemplateFilter(BaseModel):
    name: str

    class Config:
        orm_mode = True


class TemplateCreate(TemplateFilter):
    class Config:
        extra = "forbid"


class TemplateScanType(BaseModel):
    scanType: str


class TemplateScanData(BaseModel):
    crawl: Optional[str] = None
    url: AnyHttpUrl


class TemplateScanCreateList(BaseModel):
    data: TemplateScanData
    scan_types: List[TemplateScanType]


class TemplateScanConfigData(BaseModel):
    id: str
    key: str
    value: str
