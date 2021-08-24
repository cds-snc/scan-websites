import pytest

from sqlalchemy.exc import IntegrityError

from models.Scan import Scan


def test_scan_belongs_to_a_template_a_scan_type_and_an_organisation(
    scan_type_fixture, template_fixture, organisation_fixture, session
):
    scan = Scan(
        organisation=organisation_fixture,
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    session.add(scan)
    session.commit()
    assert organisation_fixture.scans[-1].id == scan.id
    assert scan_type_fixture.scans[-1].id == scan.id
    assert template_fixture.scans[-1].id == scan.id
    session.delete(scan)
    session.commit()


def test_scan_model(scan_type_fixture, template_fixture, organisation_fixture):
    scan = Scan(
        organisation=organisation_fixture,
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    assert scan.scan_type is not None
    assert scan.template is not None


def test_scan_model_saved(
    assert_new_model_saved,
    scan_type_fixture,
    template_fixture,
    organisation_fixture,
    session,
):
    scan = Scan(
        organisation=organisation_fixture,
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    session.add(scan)
    session.commit()
    assert_new_model_saved(scan)
    session.delete(scan)
    session.commit()


def test_scan_empty_template_fails(scan_type_fixture, organisation_fixture, session):
    scan = Scan(
        organisation=organisation_fixture,
        scan_type=scan_type_fixture,
    )
    session.add(scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_scan_empty_scan_type_fails(template_fixture, organisation_fixture, session):
    scan = Scan(
        organisation=organisation_fixture,
        template=template_fixture,
    )
    session.add(scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_scan_empty_organisation_fails(template_fixture, scan_type_fixture, session):
    scan = Scan(
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    session.add(scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
