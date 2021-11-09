import pytest

from sqlalchemy.exc import IntegrityError

from factories import (
    OrganisationFactory,
    ScanFactory,
    ScanTypeFactory,
    TemplateFactory,
    TemplateScanFactory,
)

from models.ScanIgnore import ScanIgnore
from pub_sub.pub_sub import AvailableScans


def test_scan_ignore_belongs_to_a_scan(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )

    scan_ignore = ScanIgnore(
        violation="violation",
        location="location",
        condition="condition",
        scan=scan,
    )
    session.add(scan_ignore)
    session.commit()
    assert scan.scan_ignores[-1].id == scan_ignore.id
    session.delete(scan_ignore)
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
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )

    scan_ignore = ScanIgnore(
        violation="violation",
        location="location",
        condition="condition",
        scan=scan,
    )
    assert scan_ignore.scan is not None


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
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )

    scan_ignore = ScanIgnore(
        violation="violation",
        location="location",
        condition="condition",
        scan=scan,
    )
    session.add(scan_ignore)
    session.commit()
    assert_new_model_saved(scan_ignore)
    session.delete(scan_ignore)
    session.commit()


def test_scan_empty_scan_fails(session):
    scan_ignore = ScanIgnore(
        violation="violation",
        location="location",
        condition="condition",
    )
    session.add(scan_ignore)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_scan_empty_violation(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )

    scan_ignore = ScanIgnore(
        location="location",
        condition="condition",
        scan=scan,
    )
    session.add(scan_ignore)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_scan_empty_ignore_location_fails(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )

    scan_ignore = ScanIgnore(
        violation="violation",
        condition="condition",
        scan=scan,
    )
    session.add(scan_ignore)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_scan_empty_ignore_condition_fails(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )

    scan_ignore = ScanIgnore(
        violation="violation",
        location="location",
        scan=scan,
    )
    session.add(scan_ignore)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
