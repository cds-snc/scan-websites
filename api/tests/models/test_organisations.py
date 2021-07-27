import pytest

from models import organisations


def test_organisation_model():
    organisation = organisations.Organisation(name="foo")
    assert organisation.name == "foo"


def test_organisation_model_saved(db):
    organisation = organisations.Organisation(name="foo")
    db.add(organisation)
    db.commit()
    assert organisation.name == "foo"
    assert organisation.id is not None
    assert organisation.created_at is not None
    assert organisation.updated_at is None
    db.rollback()
