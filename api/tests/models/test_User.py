import pytest

from sqlalchemy.exc import IntegrityError


from models.User import User


def test_user_belongs_to_an_organisation(organisation_fixture, session):
    user = User(
        name="name",
        email_address="email",
        password="password",
        organisation=organisation_fixture,
    )
    session.add(user)
    session.commit()
    assert organisation_fixture.users[-1].id == user.id
    session.delete(user)
    session.commit()


def test_user_model(organisation_fixture):
    user = User(
        name="name",
        email_address="email_address",
        password="password",
        organisation=organisation_fixture,
    )
    assert user.name == "name"
    assert user.email_address == "email_address"
    assert user.password_hash is not None
    assert user.organisation is not None
    with pytest.raises(AttributeError):
        user.password


def test_user_model_saved(assert_new_model_saved, organisation_fixture, session):
    user = User(
        name="name",
        email_address="email",
        password="password",
        organisation=organisation_fixture,
    )
    session.add(user)
    session.commit()
    assert user.name == "name"
    assert_new_model_saved(user)
    assert user.access_token is not None
    session.delete(user)
    session.commit()


def test_user_empty_name_fails(organisation_fixture, session):
    user = User(
        email_address="email",
        password="password",
        organisation=organisation_fixture,
    )
    session.add(user)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_user_empty_email_address_fails(organisation_fixture, session):
    user = User(
        name="name",
        password="password",
        organisation=organisation_fixture,
    )
    session.add(user)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_user_empty_organisation_fails(session):
    user = User(
        name="name",
        email_address="email",
        password="password",
    )
    session.add(user)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_user_duplicate_email_fails(
    assert_new_model_saved, organisation_fixture, session
):
    user = User(
        name="name",
        email_address="email",
        password="password",
        organisation=organisation_fixture,
    )

    session.add(user)
    session.commit()

    assert user.name == "name"
    assert_new_model_saved(user)

    user_two = User(
        name="name_two",
        email_address="email",
        password="password",
        organisation=organisation_fixture,
    )

    session.add(user_two)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
    session.delete(user)
    session.commit()
