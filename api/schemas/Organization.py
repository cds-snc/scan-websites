from pydantic import BaseModel


class OrganisationFilter(BaseModel):
    name: str


class OrganizationCreate(OrganisationFilter):
    class Config:
        extra = "forbid"

    pass
