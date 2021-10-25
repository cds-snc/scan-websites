import pytest

from sqlalchemy.exc import IntegrityError

from factories import (
    OrganisationFactory,
    ScanTypeFactory,
    TemplateFactory,
    TemplateScanFactory,
)

from models.Scan import Scan
from pub_sub.pub_sub import AvailableScans


def test_scan_belongs_to_a_template_a_scan_type_and_an_organisation(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )

    scan = Scan(
        organisation=organisation,
        scan_type=scan_type,
        template=template,
    )
    session.add(scan)
    session.commit()
    assert organisation.scans[-1].id == scan.id
    assert scan_type.scans[-1].id == scan.id
    assert template.scans[-1].id == scan.id
    session.delete(scan)
    session.commit()


def test_scan_model():
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )

    scan = Scan(
        organisation=organisation,
        scan_type=scan_type,
        template=template,
    )
    assert scan.scan_type is not None
    assert scan.template is not None


def test_scan_model_saved(
    assert_new_model_saved,
    session,
):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )

    scan = Scan(
        organisation=organisation,
        scan_type=scan_type,
        template=template,
    )
    session.add(scan)
    session.commit()
    assert_new_model_saved(scan)
    session.delete(scan)
    session.commit()


def test_scan_empty_template_fails(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )

    scan = Scan(
        organisation=organisation,
        scan_type=scan_type,
    )
    session.add(scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_scan_empty_scan_type_fails(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )

    scan = Scan(
        organisation=organisation,
        template=template,
    )
    session.add(scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_scan_empty_organisation_fails(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )

    scan = Scan(
        scan_type=scan_type,
        template=template,
    )
    session.add(scan)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
