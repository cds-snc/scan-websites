import pytest

from sqlalchemy.exc import IntegrityError

from models.TemplateScan import TemplateScan


def test_template_scan_belongs_to_an_template(
    scan_type_fixture, template_fixture, session
):
    template_scan = TemplateScan(
        data={"jsonb": "data"},
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    session.add(template_scan)
    session.commit()
    assert template_fixture.template_scans[0].id == template_scan.id
    session.delete(template_scan)
    session.commit()


def test_template_scan_model(scan_type_fixture, template_fixture):
    template_scan = TemplateScan(
        data={"jsonb": "data"},
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    assert template_scan.data == {"jsonb": "data"}
    assert template_scan.template is not None


def test_template_scan_model_saved(
    assert_new_model_saved, scan_type_fixture, template_fixture, session
):
    template_scan = TemplateScan(
        data={"jsonb": "data"},
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    session.add(template_scan)
    session.commit()
    assert template_scan.data == {"jsonb": "data"}
    assert_new_model_saved(template_scan)
    session.delete(template_scan)
    session.commit()


def test_template_scan_empty_data_fails(scan_type_fixture, template_fixture, session):
    template_scan = TemplateScan(
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    session.add(template_scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_template_scan_empty_template_fails(scan_type_fixture, session):
    template_scan = TemplateScan(
        data={"jsonb": "data"},
        scan_type=scan_type_fixture,
    )
    session.add(template_scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_template_scan_empty_scan_type_fails(template_fixture, session):
    template_scan = TemplateScan(
        data={"jsonb": "data"},
        template=template_fixture,
    )
    session.add(template_scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
