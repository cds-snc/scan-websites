from pydantic import BaseModel


class ScanIgnoreFilter(BaseModel):
    violation: str
    location: str
    condition: str

    class Config:
        orm_mode = True


class ScanIgnoreCreate(ScanIgnoreFilter):
    class Config:
        extra = "forbid"
