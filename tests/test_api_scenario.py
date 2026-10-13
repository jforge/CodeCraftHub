"""The same steps as test_api.sh, run against a copy of courses.json."""

import json

import app as course_app
from tests.conftest import REPO_COURSES, REST_COURSE, stored_course

NEW_DESCRIPTION = (
    "Learn HTTP methods, status codes, API design, and testing."
)


def _stats(courses):
    counts = {status: 0 for status in course_app.VALID_STATUSES}
    for course in courses:
        status = course.get("status")
        if status in counts:
            counts[status] += 1
    return {"total": len(courses), "by_status": counts}


def test_script_scenario_uses_a_copy(client, data_file, timestamps):
    """Create, update, and delete on a copy, then read the statistics."""
    original = json.loads(REPO_COURSES.read_text(encoding="utf-8"))
    data_file.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")
    original_course = next(course for course in original if course["id"] == 1)
    next_id = max(course["id"] for course in original) + 1

    listed = client.get("/api/courses")
    assert listed.status_code == 200
    assert listed.get_json() == original

    created = client.post("/api/courses", json=REST_COURSE)
    assert created.status_code == 201
    new_course = stored_course(next_id, REST_COURSE, timestamps[0])
    assert created.get_json() == new_course

    after_create = original + [new_course]
    stats = client.get("/api/courses/stats")
    assert stats.status_code == 200
    assert stats.get_json() == _stats(after_create)

    fetched = client.get("/api/courses/1")
    assert fetched.status_code == 200
    assert fetched.get_json() == original_course

    updated_fields = {
        **REST_COURSE,
        "description": NEW_DESCRIPTION,
        "status": "In Progress",
    }
    updated = client.put("/api/courses/1", json=updated_fields)
    assert updated.status_code == 200
    updated_course = {
        **original_course,
        "name": updated_fields["name"],
        "description": NEW_DESCRIPTION,
        "target_date": updated_fields["target_date"],
        "status": "In Progress",
    }
    assert updated.get_json() == updated_course
    assert updated.get_json()["created_at"] == original_course["created_at"]

    after_update = [
        updated_course if course["id"] == 1 else course
        for course in original
    ] + [new_course]
    stats = client.get("/api/courses/stats")
    assert stats.status_code == 200
    assert stats.get_json() == _stats(after_update)

    listed_again = client.get("/api/courses")
    assert listed_again.status_code == 200
    assert listed_again.get_json() == after_update

    deleted = client.delete("/api/courses/1")
    assert deleted.status_code == 200
    assert deleted.get_json() == {
        "message": "Course deleted successfully",
        "course": updated_course,
    }

    after_delete = after_update[1:]
    stats = client.get("/api/courses/stats")
    assert stats.status_code == 200
    assert stats.get_json() == _stats(after_delete)

    missing = client.get("/api/courses/1")
    assert missing.status_code == 404
    assert missing.get_json() == {"error": "Course with ID 1 not found"}
