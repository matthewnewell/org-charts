import { NavLink } from 'react-router-dom'
import './Nav.css'

export default function Nav() {
  return (
    <nav className="oc-nav">
      <NavLink to="/about" className="oc-nav__brand">
        Org Charts
      </NavLink>
      <div className="oc-nav__links">
        <NavLink
          to="/"
          end
          className={({ isActive }) => `oc-nav__link ${isActive ? 'oc-nav__link--active' : ''}`}
        >
          Chart
        </NavLink>
      </div>
    </nav>
  )
}
