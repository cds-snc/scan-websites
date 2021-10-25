import pytest

from sqlalchemy.exc import IntegrityError

from models.TemplateScanTrigger import TemplateScanTrigger


def test_template_scan_trigger_model():
    template_scan_trigger = TemplateScanTrigger(
        name="name",
        callback={"jsonb": "data"},
    )
    assert template_scan_trigger.callback == {"jsonb": "data"}


def test_template_scan_trigger_model_saved(assert_new_model_saved, session):
    template_scan_trigger = TemplateScanTrigger(name="name", callback={"jsonb": "data"})
    session.add(template_scan_trigger)
    session.commit()
    assert template_scan_trigger.callback == {"jsonb": "data"}
    assert_new_model_saved(template_scan_trigger)
    session.delete(template_scan_trigger)
    session.commit()


def test_template_scan_trigger_empty_data_fails(session):
    template_scan_trigger = TemplateScanTrigger()
    session.add(template_scan_trigger)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
