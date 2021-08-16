import pytest

from sqlalchemy.exc import IntegrityError

from models.Organisation import Organisation


def test_organisation_model():
    organisation = Organisation(name="name")
    assert organisation.name == "name"


def test_organisation_model_saved(assert_new_model_saved, session):
    organisation = Organisation(name="name")
    session.add(organisation)
    session.commit()
    assert organisation.name == "name"
    assert_new_model_saved(organisation)
    session.delete(organisation)
    session.commit()


def test_organisation_empty_name_fails(session):
    organisation = Organisation()
    session.add(organisation)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_organisation_duplicate_name_fails(assert_new_model_saved, session):
    organisation = Organisation(name="name")

    session.add(organisation)
    session.commit()

    assert organisation.name == "name"
    assert_new_model_saved(organisation)

    organisation_two = Organisation(name="name")

    session.add(organisation_two)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
    session.delete(organisation)
    session.commit()
