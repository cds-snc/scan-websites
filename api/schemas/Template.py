from pydantic import AnyHttpUrl, BaseModel, validator
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
    exclude: Optional[List[AnyHttpUrl]]
    scanType: str
    url: AnyHttpUrl

    @validator("crawl")
    def set_boolean_crawl(cls, crawl):
        return "true" if crawl == "on" else None

    @validator("exclude", pre=True)
    def convert_to_list(cls, exclude) -> List[AnyHttpUrl]:
        if not isinstance(exclude, list):
            exclude_list = list()
            exclude_list.append(exclude)
            return exclude_list
        return exclude


class TemplateScanConfigData(BaseModel):
    id: str
    key: str
    value: str
