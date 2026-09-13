import { useRootPeople } from '../api/hooks'
import OrgNode from '../components/OrgNode'
import './OrgChartPage.css'

/** The whole app: the company's reporting tree, starting at the CEO. Nothing below a node
 * loads until you click it open — simple and clean at rest, as deep as you actually drill. */
export default function OrgChartPage() {
  const { data: roots, isLoading } = useRootPeople()

  return (
    <div className="org-chart-page">
      <header className="org-chart-page__header">
        <h1 className="org-chart-page__title">Org Chart</h1>
        <p className="org-chart-page__hint">Click a name to see their profile. Click the arrow to expand.</p>
      </header>

      {isLoading && <p className="org-chart-page__loading">Loading…</p>}

      {!isLoading && (
        <div className="org-tree-scroll">
          <ul className="org-tree org-tree--root">
            {(roots ?? []).map((r) => (
              <OrgNode key={r.id} person={r} defaultExpanded />
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
