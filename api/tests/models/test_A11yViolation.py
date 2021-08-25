import pytest

from sqlalchemy.exc import IntegrityError


from models.A11yViolation import A11yViolation


def test_a11y_violation_belongs_to_an_a11y_report(a11y_report_fixture, session):
    a11y_violation = A11yViolation(
        violation="violation",
        impact="impact",
        target="target",
        html="html",
        data={"jsonb": "data"},
        tags={"jsonb": "tags"},
        message="message",
        url="url",
        a11y_report=a11y_report_fixture,
    )
    session.add(a11y_violation)
    session.commit()
    assert a11y_report_fixture.a11y_violations[-1].id == a11y_violation.id
    session.delete(a11y_violation)
    session.commit()


def test_a11y_violation_model(a11y_report_fixture):
    a11y_violation = A11yViolation(
        violation="violation",
        impact="impact",
        target="target",
        html="html",
        data={"jsonb": "data"},
        tags={"jsonb": "tags"},
        message="message",
        url="url",
        a11y_report=a11y_report_fixture,
    )
    assert a11y_violation.violation == "violation"
    assert a11y_violation.impact == "impact"
    assert a11y_violation.target == "target"
    assert a11y_violation.html == "html"
    assert a11y_violation.data == {"jsonb": "data"}
    assert a11y_violation.tags == {"jsonb": "tags"}
    assert a11y_violation.message == "message"
    assert a11y_violation.url == "url"
    assert a11y_violation.a11y_report is not None


def test_a11y_violation_model_saved(
    assert_new_model_saved, a11y_report_fixture, session
):
    a11y_violation = A11yViolation(
        violation="violation",
        impact="impact",
        target="target",
        html="html",
        data={"jsonb": "data"},
        tags={"jsonb": "tags"},
        message="message",
        url="url",
        a11y_report=a11y_report_fixture,
    )
    session.add(a11y_violation)
    session.commit()
    assert a11y_violation.violation == "violation"
    assert a11y_violation.impact == "impact"
    assert a11y_violation.target == "target"
    assert a11y_violation.html == "html"
    assert_new_model_saved(a11y_violation)
    assert a11y_violation.data == {"jsonb": "data"}
    assert a11y_violation.tags == {"jsonb": "tags"}
    assert a11y_violation.message == "message"
    assert a11y_violation.url == "url"
    session.delete(a11y_violation)
    session.commit()


def test_a11y_violation_empty_violation_fails(a11y_report_fixture, session):
    a11y_violation = A11yViolation(
        impact="impact",
        target="target",
        html="html",
        data={"jsonb": "data"},
        tags={"jsonb": "tags"},
        message="message",
        url="url",
        a11y_report=a11y_report_fixture,
    )
    session.add(a11y_violation)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_a11y_violation_empty_impact_fails(a11y_report_fixture, session):
    a11y_violation = A11yViolation(
        violation="violation",
        data={"jsonb": "data"},
        tags={"jsonb": "tags"},
        message="message",
        url="url",
        a11y_report=a11y_report_fixture,
    )
    session.add(a11y_violation)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_a11y_violation_empty_data_fails(a11y_report_fixture, session):
    a11y_violation = A11yViolation(
        violation="violation",
        impact="impact",
        target="target",
        tags={"jsonb": "tags"},
        a11y_report=a11y_report_fixture,
    )
    session.add(a11y_violation)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_a11y_violation_empty_tags_fails(a11y_report_fixture, session):
    a11y_violation = A11yViolation(
        violation="violation",
        impact="impact",
        target="target",
        data={"jsonb": "data"},
        a11y_report=a11y_report_fixture,
    )
    session.add(a11y_violation)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_a11y_violation_empty_a11y_report_fails(session):
    a11y_violation = A11yViolation(
        violation="violation",
        impact="impact",
        target="target",
        html="html",
        data={"jsonb": "data"},
        tags={"jsonb": "tags"},
        message="message",
        url="url",
    )
    session.add(a11y_violation)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
