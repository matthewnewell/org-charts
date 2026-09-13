import { useState } from 'react'
import { Link } from 'react-router-dom'
import { usePersonReports } from '../api/hooks'
import type { Person } from '../api/types'

/** One node in the drill-down tree — a card for the person, plus (when expanded) a nested
 * `<ul>` of their direct reports, each rendered the same way. The nested-list + ::before/::after
 * border trick in OrgChartPage.css is what actually draws the connecting lines; this component
 * only worries about what's expanded and what data it needs to show that. */
export default function OrgNode({ person, defaultExpanded = false }: { person: Person; defaultExpanded?: boolean }) {
  const [expanded, setExpanded] = useState(defaultExpanded)
  const hasReports = (person.direct_report_count ?? 0) > 0
  const { data: reports, isLoading } = usePersonReports(expanded ? person.id : null)

  return (
    <li className="org-tree__item">
      <div className="org-card">
        <Link className="org-card__link" to={`/people/${person.id}`}>
          <span className="org-card__name">{person.name}</span>
          <span className="org-card__title">{person.title}</span>
          {person.department && <span className="org-card__dept">{person.department}</span>}
        </Link>
        {hasReports && (
          <button
            className="org-card__toggle"
            onClick={() => setExpanded((v) => !v)}
            aria-expanded={expanded}
            title={expanded ? 'Collapse' : 'Expand'}
          >
            <span className="org-card__toggle-arrow">{expanded ? '▾' : '▸'}</span>
            {person.direct_report_count}
          </button>
        )}
      </div>

      {expanded && (
        <ul className="org-tree">
          {isLoading && (
            <li className="org-tree__item">
              <div className="org-card org-card--loading">Loading…</div>
            </li>
          )}
          {!isLoading &&
            (reports ?? []).map((r) => <OrgNode key={r.id} person={r} />)}
        </ul>
      )}
    </li>
  )
}
