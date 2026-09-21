from flask import Blueprint, jsonify, request

from db import db
from models import Person, ancestor_chain, subtree_size

bp = Blueprint("people", __name__, url_prefix="/api/people")


@bp.get("")
def list_people():
    """Flat list by default; `?root=true` returns only top-level people (no manager) — the
    chart's starting point(s). `?manager_id=` filters to one person's direct reports, same data
    the dedicated /<id>/reports route returns, kept here too for a plain flat query."""
    query = Person.query
    if request.args.get("root") == "true":
        query = query.filter(Person.manager_id.is_(None))
    manager_id = request.args.get("manager_id")
    if manager_id:
        query = query.filter(Person.manager_id == manager_id)
    people = query.order_by(Person.name).all()
    return jsonify([p.to_dict() for p in people])


def _descendants(person: Person) -> list[Person]:
    """Everyone below a person in the tree (any depth). Guards against a cycle."""
    out, seen, stack = [], {person.id}, list(person.direct_reports)
    while stack:
        node = stack.pop()
        if node.id in seen:
            continue
        seen.add(node.id)
        out.append(node)
        stack.extend(node.direct_reports)
    return out


@bp.get("/roster")
def roster():
    """The labor supply: everyone with a labor category, with who they report to. `?manager_id=`
    narrows to that manager's team (everyone below them, at any depth) — the people a functional
    manager owns and allocates. `?category=` filters to one labor category."""
    manager_id = request.args.get("manager_id")
    if manager_id:
        boss = Person.query.get_or_404(manager_id)
        people = [p for p in _descendants(boss) if p.labor_category]
    else:
        people = Person.query.filter(Person.labor_category.isnot(None)).all()
    if category := request.args.get("category"):
        people = [p for p in people if p.labor_category == category]
    people.sort(key=lambda p: (p.labor_category or "", p.name))
    return jsonify([p.to_dict(include_counts=False) for p in people])


@bp.get("/managers")
def managers():
    """Functional managers: anyone with at least one person below them who has a labor category,
    and whose OWN direct reports include such people (the immediate owner of a team) — with the
    size of that team. What Labor Supply & Demand's "whose team" picker lists."""
    out = []
    for p in Person.query.order_by(Person.name).all():
        team = [d for d in _descendants(p) if d.labor_category]
        direct = [r for r in p.direct_reports if r.labor_category]
        if direct:
            out.append({**p.to_dict(include_counts=False), "team_size": len(team), "direct_supply": len(direct)})
    return jsonify(out)


@bp.get("/<person_id>")
def get_person(person_id):
    p = Person.query.get_or_404(person_id)
    reports = sorted(p.direct_reports, key=lambda r: r.name)
    return jsonify({
        **p.to_dict(),
        "ancestors": [a.to_dict(include_counts=False) for a in ancestor_chain(p)[:-1]],
        "direct_reports": [r.to_dict() for r in reports],
        "subtree_size": subtree_size(p),
    })


@bp.get("/<person_id>/reports")
def get_reports(person_id):
    """Just the direct reports, sorted — the lazy-expand endpoint a collapsed node calls when
    it's clicked open. Deliberately light: no ancestor chain, no subtree totals."""
    p = Person.query.get_or_404(person_id)
    reports = sorted(p.direct_reports, key=lambda r: r.name)
    return jsonify([r.to_dict() for r in reports])


@bp.get("/departments")
def list_departments():
    rows = db.session.query(Person.department).filter(Person.department.isnot(None)).distinct().all()
    return jsonify(sorted({r[0] for r in rows if r[0]}))


def _validate(body: dict) -> tuple[dict, int] | None:
    if not (body.get("name") or "").strip():
        return {"error": "name is required"}, 400
    if not (body.get("title") or "").strip():
        return {"error": "title is required"}, 400
    manager_id = body.get("manager_id")
    if manager_id:
        if Person.query.get(manager_id) is None:
            return {"error": "manager_id does not refer to a real person"}, 400
    return None


@bp.post("")
def create_person():
    body = request.get_json(force=True) or {}
    err = _validate(body)
    if err:
        return jsonify(err[0]), err[1]

    p = Person(
        name=body["name"].strip(),
        title=body["title"].strip(),
        department=(body.get("department") or "").strip() or None,
        manager_id=body.get("manager_id") or None,
        labor_category=(body.get("labor_category") or "").strip() or None,
        capacity_hours=float(body.get("capacity_hours") or 40.0),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


@bp.put("/<person_id>")
def update_person(person_id):
    p = Person.query.get_or_404(person_id)
    body = request.get_json(force=True) or {}
    err = _validate({**p.to_dict(), **body})
    if err:
        return jsonify(err[0]), err[1]

    new_manager_id = body.get("manager_id", p.manager_id) or None
    if new_manager_id:
        # A person can't become their own manager, directly or by way of one of their own
        # reports — that would turn the tree into a loop with no root.
        node = Person.query.get(new_manager_id)
        seen = set()
        while node is not None and node.id not in seen:
            if node.id == person_id:
                return jsonify({"error": "a person can't report, even indirectly, to themselves"}), 400
            seen.add(node.id)
            node = node.manager

    if "name" in body:
        p.name = body["name"].strip()
    if "title" in body:
        p.title = body["title"].strip()
    if "department" in body:
        p.department = (body.get("department") or "").strip() or None
    if "manager_id" in body:
        p.manager_id = new_manager_id
    if "labor_category" in body:
        p.labor_category = (body.get("labor_category") or "").strip() or None
    if "capacity_hours" in body:
        try:
            hours = float(body["capacity_hours"])
        except (TypeError, ValueError):
            return jsonify({"error": "capacity_hours must be a number"}), 400
        if hours <= 0 or hours > 80:
            return jsonify({"error": "capacity_hours must be between 0 and 80"}), 400
        p.capacity_hours = hours

    db.session.commit()
    return jsonify(p.to_dict())


@bp.delete("/<person_id>")
def delete_person(person_id):
    p = Person.query.get_or_404(person_id)
    if p.direct_reports:
        return jsonify({
            "error": f"{p.name} has {len(p.direct_reports)} direct report(s) — reassign them first.",
        }), 400
    db.session.delete(p)
    db.session.commit()
    return "", 204
