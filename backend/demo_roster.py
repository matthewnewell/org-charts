"""
The labor roster for the demo: who is a machinist, who is a mechanical engineer, and who each of
them reports to. Labor Supply & Demand reads this to know who a functional manager "owns" — a
manager's team is everyone below them who has a labor category — and to name people on the
positions a project requests. Includes the Conway's Depot demo personas (Sam Ortiz, Alex Chen,
Priya Nair, Marcus Webb, Jess Kim) so the same people appear everywhere.

Idempotent by NAME (`apply_demo_roster()`): it creates anyone missing under the named manager and
sets labor category / capacity on people who exist. Run automatically on an empty database
(seed.seed_if_empty) and by hand against a live one (backend/refresh_demo.py). Labor categories
match Reckon's rate table and Good Plan's categories exactly, so a request for a "Machinist" can
only be filled by someone whose category is "Machinist".

Illustrative, not this company's actual roster. In real life the reporting chain would come from
Active Directory and the person key from S4; a person's detail drawer will hold both.
"""

from db import db
from models import FUNCTION_CATEGORIES, Function, Person

# name -> (labor category)  for people the base seed already created
_EXISTING = {
    "Sofia Marchetti": "Systems Engineer", "Grant Ohashi": "Systems Engineer", "Wendy Liu": "Systems Engineer",
    "Derek Pham": "Mechanical Engineer", "Katie Sorensen": "Mechanical Engineer", "Omar Haddad": "Mechanical Engineer",
    "Miguel Torres": "Machinist", "Ashley Brennan": "Machinist", "Dwayne Ferris": "Machinist",
    "Casey Nolan": "Machinist", "Felix Andrade": "Machinist",
    "Bonnie Tran": "Composite Technician", "Hector Salgado": "Composite Technician", "Ines Bauer": "Composite Technician",
    "Nolan Petrov": "Quality Inspector", "Ramona Kessler": "Quality Inspector", "Tariq Osei": "Quality Inspector",
    "Patty O'Malley": "Supply Chain Analyst",
}

# (name, title, department, manager name, labor category or None)
# Managers come before the people who report to them.
_NEW = [
    # Program management
    ("Grace Lindholm", "Director, Program Management", "Program Management", "Priya Nandakumar", None),
    # Categorized Project Engineer, not Program Manager: each works one project start-to-end
    # (see the Good Plan positions they're actually named to), which is the Project Engineer
    # definition, not the program-level Program Manager one. Titles and reporting line (Grace
    # Lindholm) are unchanged — this is a category fix, not a re-org.
    ("Sam Ortiz", "Program Manager", "Program Management", "Grace Lindholm", "Project Engineer"),
    ("Dana Kim", "Program Manager", "Program Management", "Grace Lindholm", "Project Engineer"),
    ("Tobias Ehrlich", "Program Manager", "Program Management", "Grace Lindholm", "Project Engineer"),
    ("Marcus Webb", "Portfolio Manager", "Program Management", "Grace Lindholm", None),
    # Program Engineering — Alex Chen's functional team
    ("Alex Chen", "Engineering Functional Manager", "Engineering", "Marcus Reyes", None),
    ("Victor Hale", "Systems Engineer II", "Engineering", "Alex Chen", "Systems Engineer"),
    ("Mei Ling Tan", "Systems Engineer I", "Engineering", "Alex Chen", "Systems Engineer"),
    ("Anders Holm", "Systems Engineer II", "Engineering", "Alex Chen", "Systems Engineer"),
    ("Bruno Castillo", "Mechanical Engineer II", "Engineering", "Alex Chen", "Mechanical Engineer"),
    ("Ingrid Sjoberg", "Mechanical Engineer II", "Engineering", "Alex Chen", "Mechanical Engineer"),
    ("Tyler Ng", "Mechanical Engineer I", "Engineering", "Alex Chen", "Mechanical Engineer"),
    ("Farah Nasser", "Mechanical Engineer I", "Engineering", "Alex Chen", "Mechanical Engineer"),
    ("Lin Zhao", "Electrical Engineer II", "Engineering", "Alex Chen", "Electrical Engineer"),
    ("Rafael Ortega", "Electrical Engineer I", "Engineering", "Alex Chen", "Electrical Engineer"),
    ("Hannah Berg", "Electrical Engineer II", "Engineering", "Alex Chen", "Electrical Engineer"),
    ("Derek Voss", "Director, Software Engineering", "Engineering", "Marcus Reyes", None),
    ("Arjun Mehta", "Software Engineer III", "Engineering", "Derek Voss", "Software Engineer"),
    ("Chloe Danvers", "Software Engineer II", "Engineering", "Derek Voss", "Software Engineer"),
    ("Yusuf Demir", "Software Engineer II", "Engineering", "Derek Voss", "Software Engineer"),
    ("Keiko Tanaka", "Software Engineer I", "Engineering", "Derek Voss", "Software Engineer"),
    ("Peter Nowak", "Manufacturing Engineer III", "Engineering", "Alex Chen", "Manufacturing Engineer"),
    ("Amara Okonkwo", "Manufacturing Engineer II", "Engineering", "Alex Chen", "Manufacturing Engineer"),
    ("Jonas Lindqvist", "Manufacturing Engineer II", "Engineering", "Alex Chen", "Manufacturing Engineer"),
    ("Rosa Delgado", "Manufacturing Engineer I", "Engineering", "Alex Chen", "Manufacturing Engineer"),
    # Mission assurance (Quality)
    ("Priya Nair", "Mission Assurance Manager", "Quality", "Anita Deshmukh", None),
    ("Devon Whitcomb", "Mission Assurance Engineer II", "Quality", "Priya Nair", "Mission Assurance Engineer"),
    ("Sana Qureshi", "Mission Assurance Engineer II", "Quality", "Priya Nair", "Mission Assurance Engineer"),
    ("Elliot Marsh", "Mission Assurance Engineer I", "Quality", "Priya Nair", "Mission Assurance Engineer"),
    ("Ivy Larkin", "Quality Inspector II", "Quality", "Sheryl Winthrop", "Quality Inspector"),
    ("Marco Silva", "Quality Inspector I", "Quality", "Sheryl Winthrop", "Quality Inspector"),
    # Manufacturing floor
    ("Jorge Alvarez", "Machinist II", "Manufacturing", "Nadia Kowalski", "Machinist"),
    ("Tessa Moore", "Machinist I", "Manufacturing", "Nadia Kowalski", "Machinist"),
    ("Vince Petrakis", "Machinist II", "Manufacturing", "Owen Delacroix", "Machinist"),
    ("Lucia Ferraro", "Machinist I", "Manufacturing", "Owen Delacroix", "Machinist"),
    ("Marlon Beck", "Composite Technician", "Manufacturing", "Owen Delacroix", "Composite Technician"),
    ("Yasmin Rahal", "Composite Technician", "Manufacturing", "Owen Delacroix", "Composite Technician"),
    ("Gordon Fisk", "Test Lab Supervisor", "Manufacturing", "Louis Fontaine", None),
    ("Amelia Cho", "Test Technician", "Manufacturing", "Gordon Fisk", "Test Technician"),
    ("Dev Patel", "Test Technician", "Manufacturing", "Gordon Fisk", "Test Technician"),
    ("Nora Lindgren", "Test Technician", "Manufacturing", "Gordon Fisk", "Test Technician"),
    # Supply chain
    ("Olga Petrova", "Supply Chain Analyst", "Supply Chain", "Ben Ruttiger", "Supply Chain Analyst"),
    ("Reza Farahani", "Supply Chain Analyst", "Supply Chain", "Ben Ruttiger", "Supply Chain Analyst"),
    # Business development (the Depot's BD persona)
    ("Jess Kim", "Business Development Lead", "Business Development", "Colin Ashworth", None),
    # Project Engineer — new function: the project's own start-to-end lead, distinct from a
    # Program Manager (who owns the program, several projects). Reports alongside Program
    # Management since the two roles pair up on the same work.
    ("Renata Silva", "Director, Project Engineering", "Program Management", "Grace Lindholm", None),
    ("Nathan Cole", "Project Engineer II", "Program Management", "Renata Silva", "Project Engineer"),
    ("Priyanka Rao", "Project Engineer I", "Program Management", "Renata Silva", "Project Engineer"),
    # Production Support Engineer — new function: owns the manufacturing material master, S4
    # routings, and MARTI. Sits under Manufacturing's director, closest to the work it supports.
    ("Wesley Nakamura", "Manager, Production Support Engineering", "Manufacturing", "Louis Fontaine", None),
    ("Derrick Yates", "Production Support Engineer II", "Manufacturing", "Wesley Nakamura", "Production Support Engineer"),
    ("Camille Renaud", "Production Support Engineer I", "Manufacturing", "Wesley Nakamura", "Production Support Engineer"),
]

# Function -> the person with assign authority over it (see models.Function). Doesn't have to be
# everyone's literal reporting-line manager — Louis Fontaine, for instance, is Manufacturing's
# functional manager even though Quality Inspectors and Supply Chain Analysts report elsewhere;
# he's the best-fit owner for staffing decisions across that function today. One manager per
# function, no exceptions — a manager covering two unrelated disciplines was a placeholder while
# Software Engineering had no director of its own; Derek Voss now owns it outright.
_FUNCTION_MANAGERS = {
    "Program Management": "Grace Lindholm",
    "Project Engineer": "Renata Silva",
    "Production Support Engineer": "Wesley Nakamura",
    "Systems Engineer": "Helena Vogt",
    "Mechanical Engineer": "Aiden Brooks",
    "Electrical Engineer": "Alex Chen",
    "Software Engineer": "Derek Voss",
    "Mission Assurance": "Priya Nair",
    "Manufacturing": "Louis Fontaine",
}

# A few part-timers, so capacity isn't a flat 40 everywhere.
_CAPACITY = {"Wendy Liu": 32.0, "Keiko Tanaka": 32.0, "Tessa Moore": 36.0}


def apply_demo_roster() -> dict:
    by_name = {p.name: p for p in Person.query.all()}
    made = 0
    for name, category in _EXISTING.items():
        if name in by_name:
            by_name[name].labor_category = category
    for name, title, department, manager, category in _NEW:
        person = by_name.get(name)
        boss = by_name.get(manager)
        if person is None:
            person = Person(name=name, title=title, department=department, manager_id=boss.id if boss else None)
            db.session.add(person)
            db.session.flush()
            by_name[name] = person
            made += 1
        elif boss:
            # Re-apply the intended reporting line too, not just category — a demo person who
            # moved under a new director (see Derek Voss) should actually move on a reseed, not
            # stay parented to whoever they used to report to.
            person.manager_id = boss.id
        person.labor_category = category
    for name, hours in _CAPACITY.items():
        if name in by_name:
            by_name[name].capacity_hours = hours
    db.session.commit()

    functions_set = apply_demo_functions(by_name)

    return {
        "people_added": made,
        "with_category": sum(1 for p in by_name.values() if p.labor_category),
        "functions_set": functions_set,
    }


def apply_demo_functions(by_name: dict[str, Person] | None = None) -> int:
    """Idempotent by function name: creates the 9 Function rows (see models.FUNCTION_CATEGORIES)
    if missing, and points each at its demo manager (see _FUNCTION_MANAGERS above)."""
    if by_name is None:
        by_name = {p.name: p for p in Person.query.all()}
    existing = {f.name: f for f in Function.query.all()}
    made = 0
    for name in FUNCTION_CATEGORIES:
        f = existing.get(name)
        if f is None:
            f = Function(name=name)
            db.session.add(f)
            made += 1
        manager = by_name.get(_FUNCTION_MANAGERS.get(name, ""))
        f.manager_id = manager.id if manager else f.manager_id
    db.session.commit()
    return made
