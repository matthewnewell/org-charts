"""
A representative company hierarchy — an aerospace/defense manufacturer, matching this shop's own
context — from the CEO down through Operations/Manufacturing to the machinists and assemblers on
the floor. Illustrative, not this company's actual roster.
"""

from db import db
from models import Person


def _add(name: str, title: str, department: str | None, manager: Person | None) -> Person:
    p = Person(name=name, title=title, department=department, manager_id=manager.id if manager else None)
    db.session.add(p)
    db.session.flush()
    return p


def seed_if_empty():
    if Person.query.first() is not None:
        return

    ceo = _add("Dana Whitfield", "Chief Executive Officer", "Executive", None)

    # ── VP layer ──────────────────────────────────────────────────────────────
    vp_eng = _add("Marcus Reyes", "VP, Engineering", "Engineering", ceo)
    vp_ops = _add("Priya Nandakumar", "VP, Operations", "Operations", ceo)
    vp_bd = _add("Colin Ashworth", "VP, Business Development", "Business Development", ceo)
    vp_fin = _add("Renee Castellanos", "VP, Finance & Contracts", "Finance", ceo)
    vp_people = _add("Tomas Okafor", "VP, People & Culture", "People & Culture", ceo)

    # ── Engineering ───────────────────────────────────────────────────────────
    dir_sys_eng = _add("Helena Vogt", "Director, Systems Engineering", "Engineering", vp_eng)
    dir_mech_eng = _add("Aiden Brooks", "Director, Mechanical Engineering", "Engineering", vp_eng)
    _add("Sofia Marchetti", "Systems Engineer II", "Engineering", dir_sys_eng)
    _add("Grant Ohashi", "Systems Engineer I", "Engineering", dir_sys_eng)
    _add("Wendy Liu", "Requirements Engineer", "Engineering", dir_sys_eng)
    _add("Derek Pham", "Mechanical Engineer II", "Engineering", dir_mech_eng)
    _add("Katie Sorensen", "Mechanical Engineer I", "Engineering", dir_mech_eng)
    _add("Omar Haddad", "Design Engineer", "Engineering", dir_mech_eng)

    # ── Operations / Manufacturing — the deep branch, CEO to shop floor ─────────
    dir_mfg = _add("Louis Fontaine", "Director, Manufacturing", "Manufacturing", vp_ops)
    dir_quality = _add("Anita Deshmukh", "Director, Quality", "Quality", vp_ops)
    dir_supply = _add("Ben Ruttiger", "Director, Supply Chain", "Supply Chain", vp_ops)

    mgr_bracket = _add("Carla Jimenez", "Production Manager, Bracket Assembly", "Manufacturing", dir_mfg)
    mgr_nacelle = _add("Trevor Mackay", "Production Manager, Nacelle Fairing", "Manufacturing", dir_mfg)

    sup_bracket_a = _add("Ray Higgins", "Shift Supervisor, A Shift", "Manufacturing", mgr_bracket)
    sup_bracket_b = _add("Nadia Kowalski", "Shift Supervisor, B Shift", "Manufacturing", mgr_bracket)
    sup_nacelle_a = _add("Owen Delacroix", "Shift Supervisor, A Shift", "Manufacturing", mgr_nacelle)

    for n, title in [
        ("Miguel Torres", "Machinist II"),
        ("Ashley Brennan", "Machinist I"),
        ("Dwayne Ferris", "Machinist I"),
        ("Latoya Simmons", "Assembler"),
    ]:
        _add(n, title, "Manufacturing", sup_bracket_a)

    for n, title in [
        ("Casey Nolan", "Machinist II"),
        ("Ibrahim Yusuf", "Assembler"),
        ("Grace Whitman", "Assembler"),
    ]:
        _add(n, title, "Manufacturing", sup_bracket_b)

    for n, title in [
        ("Felix Andrade", "Machinist I"),
        ("Bonnie Tran", "Assembler"),
        ("Hector Salgado", "Assembler"),
        ("Ines Bauer", "Assembler"),
    ]:
        _add(n, title, "Manufacturing", sup_nacelle_a)

    mgr_inspection = _add("Sheryl Winthrop", "Quality Manager, Inspection", "Quality", dir_quality)
    _add("Nolan Petrov", "Quality Inspector II", "Quality", mgr_inspection)
    _add("Ramona Kessler", "Quality Inspector I", "Quality", mgr_inspection)
    _add("Tariq Osei", "Quality Inspector I", "Quality", mgr_inspection)

    mgr_receiving = _add("Jules Fairweather", "Supply Chain Manager, Receiving", "Supply Chain", dir_supply)
    _add("Patty O'Malley", "Buyer", "Supply Chain", mgr_receiving)
    _add("Dominic Russo", "Receiving Inspector", "Supply Chain", mgr_receiving)

    # ── Business Development ─────────────────────────────────────────────────
    dir_capture = _add("Yvonne Achterberg", "Director, Capture Management", "Business Development", vp_bd)
    _add("Simone Laurent", "Proposal Manager", "Business Development", dir_capture)
    _add("Kwame Boateng", "Capture Analyst", "Business Development", dir_capture)

    # ── Finance & Contracts ───────────────────────────────────────────────────
    dir_contracts = _add("Marjorie Aldana", "Director, Contracts", "Finance", vp_fin)
    _add("Ellis Warburton", "Contracts Administrator", "Finance", dir_contracts)
    _add("Vicky Thackeray", "Financial Analyst", "Finance", vp_fin)

    # ── People & Culture ──────────────────────────────────────────────────────
    _add("Naomi Krantz", "HR Business Partner", "People & Culture", vp_people)
    _add("Chris Bellamy", "Recruiter", "People & Culture", vp_people)

    db.session.commit()
