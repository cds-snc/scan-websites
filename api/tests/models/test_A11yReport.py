import pytest

from sqlalchemy.exc import IntegrityError

from factories import (
    OrganisationFactory,
    ScanFactory,
    ScanTypeFactory,
    TemplateFactory,
    TemplateScanFactory,
)

from models.A11yReport import A11yReport
from pub_sub.pub_sub import AvailableScans


def test_a11y_report_belongs_to_an_scan(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.AXE_CORE.value,
        callback={"event": "sns", "topic_env": "AXE_CORE_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    session.commit()

    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=scan,
    )
    session.add(a11y_report)
    session.commit()
    assert scan.a11y_reports[-1].id == a11y_report.id
    session.delete(a11y_report)
    session.commit()


def test_a11y_report_model(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.AXE_CORE.value,
        callback={"event": "sns", "topic_env": "AXE_CORE_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    session.commit()

    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        ci=True,
        summary={"jsonb": "data"},
        scan=scan,
    )
    assert a11y_report.product == "product"
    assert a11y_report.revision == "revision"
    assert a11y_report.url == "url"
    assert a11y_report.ci is True
    assert a11y_report.summary == {"jsonb": "data"}
    assert a11y_report.scan is not None


def test_a11y_report_model_saved(assert_new_model_saved, session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.AXE_CORE.value,
        callback={"event": "sns", "topic_env": "AXE_CORE_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    session.commit()

    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=scan,
    )
    session.add(a11y_report)
    session.commit()
    assert a11y_report.product == "product"
    assert a11y_report.revision == "revision"
    assert a11y_report.url == "url"
    assert_new_model_saved(a11y_report)
    assert a11y_report.ci is False
    assert a11y_report.summary == {"jsonb": "data"}
    session.delete(a11y_report)
    session.commit()


def test_a11y_report_empty_product_fails(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.AXE_CORE.value,
        callback={"event": "sns", "topic_env": "AXE_CORE_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    session.commit()

    a11y_report = A11yReport(
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=scan,
    )
    session.add(a11y_report)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_a11y_report_empty_revision_fails(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.AXE_CORE.value,
        callback={"event": "sns", "topic_env": "AXE_CORE_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    session.commit()

    a11y_report = A11yReport(
        product="product",
        url="url",
        summary={"jsonb": "data"},
        scan=scan,
    )
    session.add(a11y_report)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_a11y_report_empty_url_passes(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.AXE_CORE.value,
        callback={"event": "sns", "topic_env": "AXE_CORE_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    session.commit()

    a11y_report = A11yReport(
        product="product",
        revision="revision",
        summary={"jsonb": "data"},
        scan=scan,
    )
    session.add(a11y_report)
    session.commit()
    assert a11y_report.url is None
    session.delete(a11y_report)
    session.commit()


def test_a11y_report_empty_summary_fails(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.AXE_CORE.value,
        callback={"event": "sns", "topic_env": "AXE_CORE_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    session.commit()

    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        scan=scan,
    )
    session.add(a11y_report)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_a11y_report_empty_scan_fails(session):
    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
    )
    session.add(a11y_report)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
