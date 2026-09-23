import type { FunctionRow, Person } from '../api/types'

export interface RoleBadge {
  kind: 'fm' | 'ic' | 'portfolio'
  label: string
  // The tree's cards are narrow (168px) — a manager of Manufacturing plus a headcount doesn't
  // fit. The detail page has room for `label` in full; the tree uses this instead.
  shortLabel: string
}

/** What role badge, if any, belongs on this person's card — the one place this ecosystem's
 * Function/Functional Manager model (see Labor Supply & Demand and Good Plan, which both read
 * it live) actually shows up in the org chart itself. Checked in this order: managing a
 * Function outranks having one (a manager can also carry a labor_category in odd demo data,
 * but "Functional Manager" is the more useful fact to lead with); an individual contributor's
 * own Function is next; Portfolio Manager is a title match, since it isn't a staffing Function
 * at all — cross-portfolio oversight, not a supply-side discipline. */
export function roleBadgeFor(person: Person, functions: FunctionRow[]): RoleBadge | null {
  const managed = functions.find((f) => f.manager_id === person.id)
  if (managed) {
    return {
      kind: 'fm',
      label: `Functional Manager — ${managed.name} · ${managed.people_count} ${managed.people_count === 1 ? 'person' : 'people'}`,
      shortLabel: `FM · ${managed.name}`,
    }
  }
  if (person.function) {
    return { kind: 'ic', label: person.function, shortLabel: person.function }
  }
  if (person.title === 'Portfolio Manager') {
    return { kind: 'portfolio', label: 'Portfolio Manager', shortLabel: 'Portfolio Manager' }
  }
  return null
}
