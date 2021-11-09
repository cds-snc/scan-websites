import pytest

from sqlalchemy.exc import IntegrityError

from factories import (
    OrganisationFactory,
)
from models.Template import Template


def test_template_belongs_to_an_organisation(session):
    organisation = OrganisationFactory()

    template = Template(
        name="name",
        organisation=organisation,
    )
    session.add(template)
    session.commit()
    assert organisation.templates[-1].id == template.id
    session.delete(template)
    session.commit()


def test_template_model():
    organisation = OrganisationFactory()

    template = Template(
        name="name",
        organisation=organisation,
    )
    assert template.name == "name"
    assert template.organisation is not None


def test_template_model_saved(assert_new_model_saved, session):
    organisation = OrganisationFactory()

    template = Template(
        name="name",
        organisation=organisation,
    )
    session.add(template)
    session.commit()
    assert template.name == "name"
    assert_new_model_saved(template)
    assert template.token is not None
    session.delete(template)
    session.commit()


def test_template_empty_name_fails(session):
    organisation = OrganisationFactory()

    template = Template(
        organisation=organisation,
    )
    session.add(template)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_template_empty_organisation_fails(session):
    template = Template(
        name="name",
    )
    session.add(template)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
