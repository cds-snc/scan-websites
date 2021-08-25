from pydantic import BaseModel


class OrganisationFilter(BaseModel):
    name: str


class OrganizationCreate(OrganisationFilter):
    pass
