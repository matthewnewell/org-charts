"""
The functional taxonomy: one Function per named discipline, each with a designated Functional
Manager (see models.Function / FUNCTION_CATEGORIES). Good Plan reads this live to build its
"pick a role" picker (a Function, then a category inside it); Labor Supply & Demand reads it to
scope its Staffing screen to one function at a time and to limit who can be named to a position.
"""

from flask import Blueprint, jsonify, request

from db import db
from models import FUNCTION_CATEGORIES, Function, Person

bp = Blueprint("functions", __name__, url_prefix="/api/functions")


@bp.get("")
def list_functions():
    rows = {f.name: f for f in Function.query.all()}
    out = []
    for name in FUNCTION_CATEGORIES:
        f = rows.get(name) or Function(name=name)
        out.append(f.to_dict())
    return jsonify(out)


@bp.get("/<function_id>")
def get_function(function_id):
    f = Function.query.get_or_404(function_id)
    return jsonify(f.to_dict())


@bp.put("/<function_id>")
def set_manager(function_id):
    """Change who has assign authority over a function. Doesn't touch anyone's reporting line —
    see Function's own doc comment."""
    f = Function.query.get_or_404(function_id)
    body = request.get_json(force=True) or {}
    manager_id = body.get("manager_id")
    if manager_id and Person.query.get(manager_id) is None:
        return jsonify({"error": "manager_id does not refer to a real person"}), 400
    f.manager_id = manager_id or None
    db.session.commit()
    return jsonify(f.to_dict())
