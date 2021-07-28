import pytest

from sqlalchemy.exc import IntegrityError

from models import organisations


def test_organisation_model():
    organisation = organisations.Organisation(name="foo")
    assert organisation.name == "foo"


def test_organisation_model_saved(assert_new_model_saved, session):
    organisation = organisations.Organisation(name="foo")
    session.add(organisation)
    session.commit()
    assert organisation.name == "foo"
    assert_new_model_saved(organisation)
    session.delete(organisation)
    session.commit()


def test_organisation_empty_name_fails(session):
    organisation = organisations.Organisation()
    session.add(organisation)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_organisation_duplicate_name_fails(assert_new_model_saved, session):
    organisation = organisations.Organisation(name="foo")

    session.add(organisation)
    session.commit()

    assert organisation.name == "foo"
    assert_new_model_saved(organisation)

    organisation_two = organisations.Organisation(name="foo")

    session.add(organisation_two)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
    session.delete(organisation)
    session.commit()
