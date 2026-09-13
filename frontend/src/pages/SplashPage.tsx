import { Link } from 'react-router-dom'
import Nav from '../components/Nav'
import './SplashPage.css'

const FEATURES = [
  {
    title: 'One tree, top to bottom',
    body: 'The CEO down through every director, manager, and supervisor to the person on the shop floor — one reporting chain, not a slide that goes stale the week after it’s exported.',
  },
  {
    title: 'Simple at rest, deep on demand',
    body: 'Nothing loads below a node until you click it open. A company of thousands stays a clean, readable chart instead of one giant page nobody can actually read.',
  },
  {
    title: 'Owned by the organization',
    body: 'Not one project’s roster — the real reporting structure, the same one every department and project sits inside.',
  },
]

export default function SplashPage() {
  return (
    <div className="splash-page">
      <Nav />
      <div className="splash-page__scroll">
        <div className="splash-page__content">
          <header className="splash-hero">
            <h1 className="splash-hero__title">Org Charts</h1>
            <p className="splash-hero__sub">
              The whole company, from the CEO to the shop floor — one clean chart you drill
              into, not a stale org-chart PDF.
            </p>
            <div className="splash-hero__actions">
              <Link className="oc-btn oc-btn--primary" to="/">
                Open the chart
              </Link>
            </div>
          </header>

          <figure className="splash-figure">
            <svg viewBox="0 0 360 170" role="img" aria-labelledby="oc-figure-title">
              <title id="oc-figure-title">
                A small org chart: one CEO box at the top, connected down to three manager boxes,
                one of which expands further to two more boxes below it.
              </title>

              <line x1="180" y1="34" x2="180" y2="54" stroke="var(--color-border-strong)" />
              <line x1="70" y1="54" x2="290" y2="54" stroke="var(--color-border-strong)" />
              <line x1="70" y1="54" x2="70" y2="66" stroke="var(--color-border-strong)" />
              <line x1="180" y1="54" x2="180" y2="66" stroke="var(--color-border-strong)" />
              <line x1="290" y1="54" x2="290" y2="66" stroke="var(--color-border-strong)" />

              <rect x="130" y="10" width="100" height="24" rx="6" fill="var(--color-accent-soft)" stroke="var(--color-accent)" strokeWidth="1.5" />
              <text x="180" y="26" textAnchor="middle" className="splash-figure__label">CEO</text>

              <rect x="20" y="66" width="100" height="24" rx="6" fill="var(--color-surface)" stroke="var(--color-border-strong)" strokeWidth="1.5" />
              <text x="70" y="82" textAnchor="middle" className="splash-figure__label">VP Engineering</text>

              <rect x="130" y="66" width="100" height="24" rx="6" fill="var(--color-surface)" stroke="var(--color-accent)" strokeWidth="1.5" />
              <text x="180" y="82" textAnchor="middle" className="splash-figure__label">VP Operations</text>

              <rect x="240" y="66" width="100" height="24" rx="6" fill="var(--color-surface)" stroke="var(--color-border-strong)" strokeWidth="1.5" />
              <text x="290" y="82" textAnchor="middle" className="splash-figure__label">VP Finance</text>

              <line x1="180" y1="90" x2="180" y2="110" stroke="var(--color-accent)" />
              <line x1="120" y1="110" x2="240" y2="110" stroke="var(--color-accent)" />
              <line x1="120" y1="110" x2="120" y2="122" stroke="var(--color-accent)" />
              <line x1="240" y1="110" x2="240" y2="122" stroke="var(--color-accent)" />

              <rect x="70" y="122" width="100" height="24" rx="6" fill="var(--color-surface)" stroke="var(--color-accent)" strokeWidth="1.5" />
              <text x="120" y="138" textAnchor="middle" className="splash-figure__label">Production Mgr</text>

              <rect x="190" y="122" width="100" height="24" rx="6" fill="var(--color-surface)" stroke="var(--color-border-strong)" strokeWidth="1.5" />
              <text x="240" y="138" textAnchor="middle" className="splash-figure__label">Quality Director</text>

              <text x="180" y="164" textAnchor="middle" className="splash-figure__caption">
                …down to the machinists and assemblers
              </text>
            </svg>
          </figure>

          <div className="splash-grid">
            {FEATURES.map((f) => (
              <div key={f.title} className="splash-card">
                <div className="splash-card__heading">{f.title}</div>
                <p className="splash-card__body">{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
