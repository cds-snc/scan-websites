from pydantic import BaseModel

class OrganizationBase(BaseModel):
  name: str

class OrganizationCreate(OrganizationBase):
    pass