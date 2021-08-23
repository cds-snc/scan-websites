import pytest

from sqlalchemy.exc import IntegrityError

from models.ScanType import ScanType


def test_scan_type_model():
    scan_type = ScanType(name="name")
    assert scan_type.name == "name"


def test_scan_type_model_saved(assert_new_model_saved, session):
    scan_type = ScanType(name="name")
    session.add(scan_type)
    session.commit()
    assert scan_type.name == "name"
    assert_new_model_saved(scan_type)
    session.delete(scan_type)
    session.commit()


def test_scan_type_empty_name_fails(session):
    scan_type = ScanType()
    session.add(scan_type)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_scan_type_duplicate_name_fails(assert_new_model_saved, session):
    scan_type = ScanType(name="name")

    session.add(scan_type)
    session.commit()

    assert scan_type.name == "name"
    assert_new_model_saved(scan_type)

    scan_type_two = ScanType(name="name")

    session.add(scan_type_two)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
    session.delete(scan_type)
    session.commit()
