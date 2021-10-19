import pytest

from sqlalchemy.exc import IntegrityError

from models.ScanIgnore import ScanIgnore


def test_scan_ignore_belongs_to_a_scan(scan_fixture, session):
    scan_ignore = ScanIgnore(
        violation="violation",
        ignore_condition="ignore_condition",
        scan=scan_fixture,
    )
    session.add(scan_ignore)
    session.commit()
    assert scan_fixture.scan_ignores[-1].id == scan_ignore.id
    session.delete(scan_ignore)
    session.commit()


def test_scan_model(scan_fixture):
    scan_ignore = ScanIgnore(
        violation="violation",
        ignore_condition="ignore_condition",
        scan=scan_fixture,
    )
    assert scan_ignore.scan is not None


def test_scan_model_saved(
    assert_new_model_saved,
    scan_fixture,
    session,
):
    scan_ignore = ScanIgnore(
        violation="violation",
        ignore_condition="ignore_condition",
        scan=scan_fixture,
    )
    session.add(scan_ignore)
    session.commit()
    assert_new_model_saved(scan_ignore)
    session.delete(scan_ignore)
    session.commit()


def test_scan_empty_scan_fails(session):
    scan_ignore = ScanIgnore(
        violation="violation",
        ignore_condition="ignore_condition",
    )
    session.add(scan_ignore)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_scan_empty_violation(scan_fixture, session):
    scan_ignore = ScanIgnore(
        ignore_condition="ignore_condition",
        scan=scan_fixture,
    )
    session.add(scan_ignore)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_scan_empty_ignore_condition_fails(scan_fixture, session):
    scan_ignore = ScanIgnore(
        violation="violation",
        scan=scan_fixture,
    )
    session.add(scan_ignore)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
