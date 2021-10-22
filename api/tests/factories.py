import factory

from models.Organisation import Organisation
from models.SecurityReport import SecurityReport
from models.SecurityViolation import SecurityViolation
from models.Scan import Scan
from models.ScanType import ScanType
from models.Template import Template
from models.TemplateScan import TemplateScan
from models.User import User


class OrganisationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Organisation
        sqlalchemy_get_or_create = ("name",)

    id = factory.Faker("uuid4")
    name = factory.Faker("name")


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    name = factory.Faker("name")
    email_address = factory.Faker("email")
    password_hash = factory.Faker("uuid4")
    access_token = factory.Faker("uuid4")
    organisation_id = OrganisationFactory.id
    organisation = factory.SubFactory(OrganisationFactory)


class TemplateFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Template
        sqlalchemy_get_or_create = ("name",)

    id = factory.Faker("uuid4")
    token = factory.Faker("uuid4")
    name = factory.Faker("name")

    organisation_id = OrganisationFactory.id
    organisation = factory.SubFactory(OrganisationFactory)


class ScanTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ScanType
        sqlalchemy_get_or_create = ("name",)

    id = factory.Faker("uuid4")
    name = factory.Faker("name")
    callback = factory.Faker("json")


class TemplateScanFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TemplateScan

    id = factory.Faker("uuid4")
    data = {"jsonb": "data"}

    template_id = TemplateFactory.id
    template = factory.SubFactory(TemplateFactory)

    scan_type_id = ScanTypeFactory.id
    scan_type = factory.SubFactory(ScanTypeFactory)


class ScanFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Scan

    id = factory.Faker("uuid4")

    organisation_id = OrganisationFactory.id
    organisation = factory.SubFactory(OrganisationFactory)

    template_id = TemplateFactory.id
    template = factory.SubFactory(TemplateFactory)

    scan_type_id = ScanTypeFactory.id
    scan_type = factory.SubFactory(ScanTypeFactory)


class SecurityReportFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SecurityReport

    id = factory.Faker("uuid4")
    product = factory.Faker("text")
    revision = factory.Faker("text")
    url = factory.Faker("url")
    ci = factory.Faker("boolean")
    summary = factory.Faker("json")

    scan_id = ScanFactory.id
    scan = factory.SubFactory(ScanFactory)


class SecurityViolationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SecurityViolation

    id = factory.Faker("uuid4")
    violation = factory.Faker("text")
    risk = factory.Faker("text")
    confidence = factory.Faker("text")
    solution = factory.Faker("text")
    reference = factory.Faker("text")
    target = factory.Faker("text")
    data = factory.Faker("json")
    tags = factory.Faker("json")
    message = factory.Faker("text")
    url = factory.Faker("text")

    security_report_id = SecurityReportFactory.id
    security_report = factory.SubFactory(SecurityReportFactory)
