"""API cases from tests/test.txt. Each test starts with an empty course file."""

import pytest

from tests.conftest import (
    FLASK_COURSE,
    REST_COURSE,
    assert_error,
    stored_course,
)

STATUS_ERROR = (
    "Invalid status. Status must be one of: "
    "Completed, In Progress, Not Started"
)

UPDATED_REST_COURSE = {
    **REST_COURSE,
    "description": "Learn HTTP methods, status codes, API design, and testing.",
    "status": "In Progress",
}

DOCKER_COURSE = {
    "name": "Docker Basics",
    "description": "Learn the basics of Docker.",
    "target_date": "2026-12-15",
    "status": "Not Started",
}


def test_get_courses_is_empty(client):
    response = client.get("/api/courses")

    assert response.status_code == 200
    assert response.get_json() == []


def test_get_courses_returns_saved_courses(client, timestamps):
    created = client.post("/api/courses", json=REST_COURSE)

    response = client.get("/api/courses")

    assert created.status_code == 201
    assert response.status_code == 200
    assert response.get_json() == [
        stored_course(1, REST_COURSE, timestamps[0])
    ]


def test_post_course_starts_ids_at_one(client, timestamps):
    response = client.post("/api/courses", json=REST_COURSE)

    assert response.status_code == 201
    assert response.get_json() == stored_course(1, REST_COURSE, timestamps[0])


def test_post_second_course_uses_the_next_id(client, timestamps):
    client.post("/api/courses", json=REST_COURSE)

    response = client.post("/api/courses", json=FLASK_COURSE)

    assert response.status_code == 201
    assert response.get_json() == stored_course(2, FLASK_COURSE, timestamps[1])


def test_get_one_course(client, timestamps):
    client.post("/api/courses", json=REST_COURSE)

    response = client.get("/api/courses/1")

    assert response.status_code == 200
    assert response.get_json() == stored_course(1, REST_COURSE, timestamps[0])


def test_put_course_updates_fields_and_keeps_id_and_time(client, timestamps):
    client.post("/api/courses", json=REST_COURSE)

    response = client.put("/api/courses/1", json=UPDATED_REST_COURSE)

    assert response.status_code == 200
    assert response.get_json() == stored_course(
        1,
        UPDATED_REST_COURSE,
        timestamps[0],
    )


def test_put_course_can_mark_it_completed(client, timestamps):
    client.post("/api/courses", json=REST_COURSE)
    completed = {**UPDATED_REST_COURSE, "status": "Completed"}

    response = client.put("/api/courses/1", json=completed)

    assert response.status_code == 200
    assert response.get_json() == stored_course(1, completed, timestamps[0])


def test_delete_course_returns_the_deleted_course(client, timestamps):
    client.post("/api/courses", json=REST_COURSE)
    client.post("/api/courses", json=FLASK_COURSE)
    deleted_course = stored_course(2, FLASK_COURSE, timestamps[1])

    response = client.delete("/api/courses/2")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Course deleted successfully",
        "course": deleted_course,
    }
    confirm = client.get("/api/courses/2")
    assert_error(confirm, 404, "Course with ID 2 not found")
    assert client.get("/api/courses").get_json() == [
        stored_course(1, REST_COURSE, timestamps[0])
    ]


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (
            {
                "name": "Python Basics",
                "target_date": "2026-12-01",
                "status": "Not Started",
            },
            "Missing required fields: description",
        ),
        (
            {"name": "Python Basics"},
            "Missing required fields: description, target_date, status",
        ),
        (
            {
                "name": "",
                "description": "Learn Python programming.",
                "target_date": "2026-12-01",
                "status": "Not Started",
            },
            "name must be a non-empty string",
        ),
        (
            {
                "name": "Python Basics",
                "description": "",
                "target_date": "2026-12-01",
                "status": "Not Started",
            },
            "description must be a non-empty string",
        ),
        (
            {**DOCKER_COURSE, "status": "Started"},
            STATUS_ERROR,
        ),
        (
            {**DOCKER_COURSE, "status": "completed"},
            STATUS_ERROR,
        ),
        (
            {**DOCKER_COURSE, "target_date": "15-12-2026"},
            "target_date must use YYYY-MM-DD format",
        ),
        (
            {**DOCKER_COURSE, "target_date": "2026-02-30"},
            "target_date must be a valid calendar date",
        ),
        (
            {**DOCKER_COURSE, "target_date": "2026-2-5"},
            "target_date must use YYYY-MM-DD format",
        ),
    ],
)
def test_post_rejects_invalid_course_data(client, payload, message):
    response = client.post("/api/courses", json=payload)

    assert_error(response, 400, message)
    assert client.get("/api/courses").get_json() == []


def test_post_rejects_invalid_json(client):
    response = client.post(
        "/api/courses",
        data='{"name": "Python Basics",',
        content_type="application/json",
    )

    assert_error(response, 400, "Request body must contain valid JSON")


def test_post_rejects_a_missing_body(client):
    response = client.post("/api/courses")

    assert_error(response, 400, "Request body must contain valid JSON")


def test_post_rejects_a_json_array(client):
    response = client.post(
        "/api/courses",
        json=[{"name": "Python Basics"}],
    )

    assert_error(response, 400, "Request body must be a JSON object")


def test_get_missing_course(client):
    response = client.get("/api/courses/9999")

    assert_error(response, 404, "Course with ID 9999 not found")


def test_put_missing_course(client):
    response = client.put(
        "/api/courses/9999",
        json={
            "name": "Nonexistent Course",
            "description": "This course does not exist.",
            "target_date": "2026-12-31",
            "status": "Not Started",
        },
    )

    assert_error(response, 404, "Course with ID 9999 not found")


def test_delete_missing_course(client):
    response = client.delete("/api/courses/9999")

    assert_error(response, 404, "Course with ID 9999 not found")


def test_put_rejects_missing_fields_and_keeps_the_course(client, timestamps):
    client.post("/api/courses", json=REST_COURSE)

    response = client.put("/api/courses/1", json={"status": "Completed"})

    assert_error(
        response,
        400,
        "Missing required fields: name, description, target_date",
    )
    assert client.get("/api/courses/1").get_json() == stored_course(
        1,
        REST_COURSE,
        timestamps[0],
    )


def test_put_rejects_an_invalid_status(client, timestamps):
    client.post("/api/courses", json=REST_COURSE)

    response = client.put(
        "/api/courses/1",
        json={
            "name": "REST API Fundamentals",
            "description": "Updated REST API course.",
            "target_date": "2026-12-31",
            "status": "Finished",
        },
    )

    assert_error(response, 400, STATUS_ERROR)
    assert client.get("/api/courses/1").get_json() == stored_course(
        1,
        REST_COURSE,
        timestamps[0],
    )


def test_put_rejects_an_invalid_date(client, timestamps):
    client.post("/api/courses", json=REST_COURSE)

    response = client.put(
        "/api/courses/1",
        json={
            "name": "REST API Fundamentals",
            "description": "Updated REST API course.",
            "target_date": "December 31, 2026",
            "status": "In Progress",
        },
    )

    assert_error(response, 400, "target_date must use YYYY-MM-DD format")
    assert client.get("/api/courses/1").get_json() == stored_course(
        1,
        REST_COURSE,
        timestamps[0],
    )


def test_unknown_url(client):
    response = client.get("/api/unknown")

    assert_error(response, 404, "Endpoint not found")
