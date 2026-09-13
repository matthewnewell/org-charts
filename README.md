# Org Charts

The company's whole reporting chain, from the CEO down to the shop floor — one clean chart you
drill into, not a slide deck that goes stale the week after it's exported.

## The idea

**Owned by the organization**, not by any one project — this is the real reporting structure,
the same one every department and project sits inside. It has nothing to do with a project's own
team roster (that's Conway's Depot's Identity & Project Membership territory); this is "who
reports to whom," company-wide.

The whole model is one self-referential tree: a person has a manager, or they're the root (the
CEO). No separate org-unit hierarchy to keep in sync — `department` is a plain label per person,
same convention as `project`/`portfolio` labels everywhere else in this ecosystem.

**Simple and clean, but expandable when needed**: a real company's tree is wide at the bottom —
a lot more machinists than VPs. Nothing loads below a node until you click it open, so the chart
starts at the CEO, one card, and only grows as deep as someone actually drills. No fixed depth
limit — it goes exactly as far down as the data does.

## Stack

Same as the rest of this ecosystem — Flask + SQLAlchemy + SQLite backend, React + TypeScript +
Vite frontend, no shared database, tied in only by Conway's Depot's registry entry.

## Running locally

```bash
# backend
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py            # :8095, seeds a representative company tree on first run

# frontend (separate terminal)
cd frontend
npm install
npm run dev                        # :5181, proxies /api to :8095
```

## Data model

- **Person** — `name`, `title`, an optional free-text `department`, and `manager_id` pointing
  at another Person (null at the root). `GET /api/people/<id>` returns the ancestor chain (the
  breadcrumb) and direct reports; `GET /api/people/<id>/reports` is the lighter lazy-expand
  endpoint a collapsed card calls when it's clicked open.
- A person can't be deleted while they still have direct reports (reassign them first), and
  can't be reassigned to report to their own descendant — the tree can't become a loop.

## Status

v1 — the drill-down chart, a profile page with basic add/edit/remove, no photos, no org-unit
filtering beyond the department label. Seeded with a representative aerospace/manufacturing
hierarchy (~50 people), not anyone's real roster.
