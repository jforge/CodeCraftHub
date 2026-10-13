"""Fixtures for the API tests. They never write the project courses.json."""

from pathlib import Path

import pytest

import app as course_app

REPO_COURSES = Path(__file__).resolve().parents[1] / "courses.json"

REST_COURSE = {
    "name": "REST API Fundamentals",
    "description": "Learn HTTP methods, status codes, and API design.",
    "target_date": "2026-12-31",
    "status": "Not Started",
}

FLASK_COURSE = {
    "name": "Flask Web Development",
    "description": "Build web applications and APIs using Flask.",
    "target_date": "2027-01-15",
    "status": "In Progress",
}

TIMESTAMPS = (
    "2026-10-13T10:30:00+00:00",
    "2026-10-13T10:35:00+00:00",
)


@pytest.fixture
def data_file(tmp_path, monkeypatch):
    """Point the app at an empty temporary course file."""
    path = tmp_path / "courses.json"
    monkeypatch.setattr(course_app, "DATA_FILE", path)
    return path


@pytest.fixture
def client(data_file):
    """Return a Flask test client for the temporary course file."""
    course_app.app.config.update(TESTING=True)
    return course_app.app.test_client()


@pytest.fixture
def timestamps(monkeypatch):
    """Return the sample timestamps used in tests/test.txt."""
    pending = iter(TIMESTAMPS)
    monkeypatch.setattr(course_app, "get_current_timestamp", lambda: next(pending))
    return TIMESTAMPS


@pytest.fixture(autouse=True)
def protect_project_courses_file():
    """Fail the test if the example courses.json file changes."""
    before = REPO_COURSES.read_bytes() if REPO_COURSES.exists() else None
    yield
    after = REPO_COURSES.read_bytes() if REPO_COURSES.exists() else None
    assert after == before


def stored_course(course_id, fields, created_at):
    """Build the course object the API stores."""
    return {
        "id": course_id,
        "name": fields["name"],
        "description": fields["description"],
        "target_date": fields["target_date"],
        "status": fields["status"],
        "created_at": created_at,
    }


def assert_error(response, status_code, message):
    """Check a JSON error response."""
    assert response.status_code == status_code
    assert response.get_json() == {"error": message}
