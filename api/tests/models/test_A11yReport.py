import pytest

from sqlalchemy.exc import IntegrityError


from models.A11yReport import A11yReport


def test_a11y_report_belongs_to_an_scan(scan_fixture, session):
    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=scan_fixture,
    )
    session.add(a11y_report)
    session.commit()
    assert scan_fixture.a11y_reports[-1].id == a11y_report.id
    session.delete(a11y_report)
    session.commit()


def test_a11y_report_model(scan_fixture):
    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        ci=True,
        summary={"jsonb": "data"},
        scan=scan_fixture,
    )
    assert a11y_report.product == "product"
    assert a11y_report.revision == "revision"
    assert a11y_report.url == "url"
    assert a11y_report.ci is True
    assert a11y_report.summary == {"jsonb": "data"}
    assert a11y_report.scan is not None


def test_a11y_report_model_saved(assert_new_model_saved, scan_fixture, session):
    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=scan_fixture,
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


def test_a11y_report_empty_productfails(scan_fixture, session):
    a11y_report = A11yReport(
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=scan_fixture,
    )
    session.add(a11y_report)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_a11y_report_empty_revision_fails(scan_fixture, session):
    a11y_report = A11yReport(
        product="product",
        url="url",
        summary={"jsonb": "data"},
        scan=scan_fixture,
    )
    session.add(a11y_report)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_a11y_report_empty_url_passes(scan_fixture, session):
    a11y_report = A11yReport(
        product="product",
        revision="revision",
        summary={"jsonb": "data"},
        scan=scan_fixture,
    )
    session.add(a11y_report)
    session.commit()
    assert a11y_report.url is None
    session.delete(a11y_report)
    session.commit()


def test_a11y_report_empty_summary_fails(scan_fixture, session):
    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        scan=scan_fixture,
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
