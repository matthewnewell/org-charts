import os
import sys

os.environ["DATA_DIR"] = os.path.join(os.path.dirname(__file__), "_tmp_data")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import shutil

import pytest

from app import create_app
from db import db


@pytest.fixture()
def client():
    shutil.rmtree(os.environ["DATA_DIR"], ignore_errors=True)
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    with app.app_context():
        db.session.remove()
    shutil.rmtree(os.environ["DATA_DIR"], ignore_errors=True)


def test_root_lists_only_top_level_people(client):
    res = client.get("/api/people?root=true")
    assert res.status_code == 200
    roots = res.get_json()
    assert len(roots) == 1
    assert roots[0]["name"] == "Dana Whitfield"
    assert roots[0]["manager_id"] is None
    assert roots[0]["direct_report_count"] == 5


def test_get_person_includes_ancestors_and_reports(client):
    roots = client.get("/api/people?root=true").get_json()
    ceo_id = roots[0]["id"]
    reports = client.get(f"/api/people/{ceo_id}/reports").get_json()
    vp_ops = next(r for r in reports if r["title"] == "VP, Operations")

    detail = client.get(f"/api/people/{vp_ops['id']}").get_json()
    assert detail["ancestors"] == [{"id": ceo_id, "name": "Dana Whitfield", "title": "Chief Executive Officer", "department": "Executive", "manager_id": None, "manager_name": None}]
    assert any(r["title"].startswith("Director, Manufacturing") for r in detail["direct_reports"])
    assert detail["subtree_size"] > 20  # the whole manufacturing branch hangs under here


def test_create_update_delete_round_trip(client):
    roots = client.get("/api/people?root=true").get_json()
    ceo_id = roots[0]["id"]

    created = client.post("/api/people", json={"name": "Test Person", "title": "Test Title", "manager_id": ceo_id})
    assert created.status_code == 201
    person_id = created.get_json()["id"]

    updated = client.put(f"/api/people/{person_id}", json={"title": "Updated Title"})
    assert updated.status_code == 200
    assert updated.get_json()["title"] == "Updated Title"

    deleted = client.delete(f"/api/people/{person_id}")
    assert deleted.status_code == 204


def test_cannot_delete_a_person_with_direct_reports(client):
    roots = client.get("/api/people?root=true").get_json()
    ceo_id = roots[0]["id"]
    res = client.delete(f"/api/people/{ceo_id}")
    assert res.status_code == 400
    assert "direct report" in res.get_json()["error"]


def test_cannot_make_a_person_report_to_their_own_descendant(client):
    roots = client.get("/api/people?root=true").get_json()
    ceo_id = roots[0]["id"]
    vp = next(r for r in client.get(f"/api/people/{ceo_id}/reports").get_json())

    res = client.put(f"/api/people/{ceo_id}", json={"manager_id": vp["id"]})
    assert res.status_code == 400
    assert "themselves" in res.get_json()["error"]


def test_create_requires_name_and_title(client):
    res = client.post("/api/people", json={"name": "No Title"})
    assert res.status_code == 400
