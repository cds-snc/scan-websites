import pytest

from sqlalchemy.exc import IntegrityError

from factories import (
    OrganisationFactory,
    ScanTypeFactory,
    TemplateFactory,
)
from models.TemplateScan import TemplateScan
from pub_sub.pub_sub import AvailableScans


def test_template_scan_belongs_to_a_template_and_a_scan_type(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )

    template_scan = TemplateScan(
        data={"jsonb": "data"},
        scan_type=scan_type,
        template=template,
    )
    session.add(template_scan)
    session.commit()
    assert template.template_scans[-1].id == template_scan.id
    assert scan_type.template_scans[-1].id == template_scan.id
    session.delete(template_scan)
    session.commit()


def test_template_scan_model():
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )

    template_scan = TemplateScan(
        data={"jsonb": "data"},
        scan_type=scan_type,
        template=template,
    )
    assert template_scan.data == {"jsonb": "data"}
    assert template_scan.scan_type is not None
    assert template_scan.template is not None


def test_template_scan_model_saved(assert_new_model_saved, session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )

    template_scan = TemplateScan(
        data={"jsonb": "data"},
        scan_type=scan_type,
        template=template,
    )
    session.add(template_scan)
    session.commit()
    assert template_scan.data == {"jsonb": "data"}
    assert_new_model_saved(template_scan)
    session.delete(template_scan)
    session.commit()


def test_template_scan_empty_data_fails(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )

    template_scan = TemplateScan(
        scan_type=scan_type,
        template=template,
    )
    session.add(template_scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_template_scan_empty_template_fails(session):
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )

    template_scan = TemplateScan(
        data={"jsonb": "data"},
        scan_type=scan_type,
    )
    session.add(template_scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_template_scan_empty_scan_type_fails(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)

    template_scan = TemplateScan(
        data={"jsonb": "data"},
        template=template,
    )
    session.add(template_scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
