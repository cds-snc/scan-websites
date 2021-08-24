import pytest

from sqlalchemy.exc import IntegrityError

from models.TemplateScanTrigger import TemplateScanTrigger


def test_template_scan_trigger_belongs_to_an_template_scan(
    template_scan_fixture, session
):
    template_scan_trigger = TemplateScanTrigger(
        data={"jsonb": "data"},
        template_scan=template_scan_fixture,
    )
    session.add(template_scan_trigger)
    session.commit()
    assert (
        template_scan_fixture.template_scan_triggers[0].id == template_scan_trigger.id
    )
    session.delete(template_scan_trigger)
    session.commit()


def test_template_scan_trigger_model(template_scan_fixture):
    template_scan_trigger = TemplateScanTrigger(
        data={"jsonb": "data"},
        template_scan=template_scan_fixture,
    )
    assert template_scan_trigger.data == {"jsonb": "data"}
    assert template_scan_trigger.template_scan is not None


def test_template_scan_trigger_model_saved(
    assert_new_model_saved, template_scan_fixture, session
):
    template_scan_trigger = TemplateScanTrigger(
        data={"jsonb": "data"},
        template_scan=template_scan_fixture,
    )
    session.add(template_scan_trigger)
    session.commit()
    assert template_scan_trigger.data == {"jsonb": "data"}
    assert_new_model_saved(template_scan_trigger)
    session.delete(template_scan_trigger)
    session.commit()


def test_template_scan_trigger_empty_data_fails(template_scan_fixture, session):
    template_scan_trigger = TemplateScanTrigger(
        template_scan=template_scan_fixture,
    )
    session.add(template_scan_trigger)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_template_scan_trigger_empty_template_scan_fails(session):
    template_scan_trigger = TemplateScanTrigger(
        data={"jsonb": "data"},
    )
    session.add(template_scan_trigger)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
