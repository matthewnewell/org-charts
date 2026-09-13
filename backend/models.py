"""
Org Charts: the company's reporting structure, from the CEO down to the person on the shop
floor — one tree, drawn as a tree, drilled into instead of dumped on screen all at once.

**Owned by the organization**, not by any one project — this is the actual org, the same way
this ecosystem's other org-scoped apps (Big Plan, QMS, Portfolio Manager) serve every project at
once rather than belonging to one. It has nothing to do with a project's own team roster — see
Conway's Depot's Identity & Project Membership territory for that; this is "who reports to
whom," company-wide.

The whole model is one self-referential table: a Person has a `manager_id` pointing at another
Person, or `None` at the root (the CEO — there can be more than one root if the seed ever needs
co-CEOs or an interim gap, but the app doesn't assume exactly one). No department table, no
org-unit hierarchy separate from the people themselves — `department` is a plain free-text label
per person (same "plain string, not a foreign-keyed taxonomy" convention as `project`/`portfolio`
labels everywhere else in this ecosystem), used for a color/filter hint, not a second hierarchy
to keep in sync with the real one.

**Why drill-down, not one big chart**: a real company's reporting tree is wide at the bottom (a
lot more machinists than VPs) — rendering the whole thing at once is neither "simple and clean"
nor actually readable past a couple hundred people. Every node loads its own direct reports on
demand (`GET /api/people/<id>/reports`), so the chart starts at the CEO, one node, and only grows
as far as someone actually clicks.
"""

from datetime import datetime, timezone

from db import _uuid, db


def _now():
    return datetime.now(timezone.utc)


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    # Free-text label, same convention as project/portfolio elsewhere — not a second hierarchy.
    department = db.Column(db.String(120), nullable=True)
    manager_id = db.Column(db.String(36), db.ForeignKey("person.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    manager = db.relationship("Person", remote_side=[id], backref="direct_reports")

    def to_dict(self, include_counts: bool = True) -> dict:
        d = {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "department": self.department,
            "manager_id": self.manager_id,
            "manager_name": self.manager.name if self.manager else None,
        }
        if include_counts:
            d["direct_report_count"] = len(self.direct_reports)
        return d


def ancestor_chain(person: Person) -> list[Person]:
    """Root-to-self chain — the breadcrumb above a drilled-into node. Guards against a cyclic
    manager_id (shouldn't happen, but a person accidentally set as their own manager's manager
    should never hang the app)."""
    chain: list[Person] = []
    seen: set[str] = set()
    node: Person | None = person
    while node is not None and node.id not in seen:
        chain.append(node)
        seen.add(node.id)
        node = node.manager
    chain.reverse()
    return chain


def subtree_size(person: Person) -> int:
    """Total headcount under this person, every level down — used for the "N people" hint on a
    collapsed node so drilling in isn't a total guess."""
    total = 0
    stack = list(person.direct_reports)
    while stack:
        node = stack.pop()
        total += 1
        stack.extend(node.direct_reports)
    return total
