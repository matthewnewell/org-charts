import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useCreatePerson, useDeletePerson, usePerson, useUpdatePerson } from '../api/hooks'
import './PersonDetailPage.css'

export default function PersonDetailPage() {
  const { personId } = useParams<{ personId: string }>()
  const navigate = useNavigate()
  const { data: person, isLoading } = usePerson(personId)
  const update = useUpdatePerson()
  const create = useCreatePerson()
  const del = useDeletePerson()

  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ name: '', title: '', department: '' })
  const [addingReport, setAddingReport] = useState(false)
  const [reportForm, setReportForm] = useState({ name: '', title: '', department: '' })

  if (isLoading || !person) return <div className="person-page__loading">Loading…</div>

  function startEdit() {
    setForm({ name: person!.name, title: person!.title, department: person!.department ?? '' })
    setEditing(true)
  }

  function saveEdit() {
    update.mutate(
      { id: person!.id, data: { name: form.name, title: form.title, department: form.department || undefined } },
      { onSuccess: () => setEditing(false) },
    )
  }

  function addReport(e: React.FormEvent) {
    e.preventDefault()
    if (!reportForm.name.trim() || !reportForm.title.trim()) return
    create.mutate(
      { name: reportForm.name, title: reportForm.title, department: reportForm.department || undefined, manager_id: person!.id },
      {
        onSuccess: () => {
          setReportForm({ name: '', title: '', department: '' })
          setAddingReport(false)
        },
      },
    )
  }

  function handleDelete() {
    if (person!.direct_reports.length > 0) return
    if (!confirm(`Remove ${person!.name} from the chart?`)) return
    del.mutate(person!.id, { onSuccess: () => navigate(person!.manager_id ? `/people/${person!.manager_id}` : '/') })
  }

  return (
    <div className="person-page">
      <div className="person-page__content">
        <Link to="/" className="person-page__back">← Org Chart</Link>

        {person.ancestors.length > 0 && (
          <nav className="person-page__breadcrumb">
            {person.ancestors.map((a) => (
              <span key={a.id}>
                <Link to={`/people/${a.id}`}>{a.name}</Link>
                <span className="person-page__breadcrumb-sep">/</span>
              </span>
            ))}
          </nav>
        )}

        <header className="person-page__header">
          {!editing ? (
            <>
              <div>
                <h1 className="person-page__name">{person.name}</h1>
                <p className="person-page__title">{person.title}</p>
                {person.department && <span className="person-page__dept">{person.department}</span>}
                {person.manager_name && (
                  <p className="person-page__reports-to">
                    Reports to{' '}
                    <Link to={`/people/${person.manager_id}`}>{person.manager_name}</Link>
                  </p>
                )}
              </div>
              <button className="oc-btn oc-btn--ghost" onClick={startEdit}>
                Edit
              </button>
            </>
          ) : (
            <form
              className="person-page__edit-form"
              onSubmit={(e) => {
                e.preventDefault()
                saveEdit()
              }}
            >
              <label>
                Name
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </label>
              <label>
                Title
                <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
              </label>
              <label>
                Department
                <input value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
              </label>
              <div className="person-page__edit-actions">
                <button className="oc-btn oc-btn--primary" type="submit" disabled={update.isPending}>
                  {update.isPending ? 'Saving…' : 'Save'}
                </button>
                <button className="oc-btn oc-btn--ghost" type="button" onClick={() => setEditing(false)}>
                  Cancel
                </button>
              </div>
            </form>
          )}
        </header>

        <section className="person-page__section">
          <div className="person-page__section-header">
            <h2>
              Direct reports
              {person.direct_reports.length > 0 && ` (${person.direct_reports.length})`}
              {person.subtree_size > person.direct_reports.length && (
                <span className="person-page__subtree-hint"> · {person.subtree_size} people in total below</span>
              )}
            </h2>
            <button className="oc-btn oc-btn--ghost" onClick={() => setAddingReport((v) => !v)}>
              {addingReport ? 'Cancel' : '+ Add direct report'}
            </button>
          </div>

          {addingReport && (
            <form className="person-page__add-form" onSubmit={addReport}>
              <input
                placeholder="Name"
                value={reportForm.name}
                onChange={(e) => setReportForm({ ...reportForm, name: e.target.value })}
                required
              />
              <input
                placeholder="Title"
                value={reportForm.title}
                onChange={(e) => setReportForm({ ...reportForm, title: e.target.value })}
                required
              />
              <input
                placeholder="Department (optional)"
                value={reportForm.department}
                onChange={(e) => setReportForm({ ...reportForm, department: e.target.value })}
              />
              <button className="oc-btn oc-btn--primary" type="submit" disabled={create.isPending}>
                {create.isPending ? 'Adding…' : 'Add'}
              </button>
            </form>
          )}

          {person.direct_reports.length === 0 ? (
            <p className="person-page__muted">No direct reports.</p>
          ) : (
            <ul className="person-page__reports-list">
              {person.direct_reports.map((r) => (
                <li key={r.id}>
                  <Link to={`/people/${r.id}`} className="person-page__report-chip">
                    <span className="person-page__report-name">{r.name}</span>
                    <span className="person-page__report-title">{r.title}</span>
                    {(r.direct_report_count ?? 0) > 0 && (
                      <span className="person-page__report-count">{r.direct_report_count}</span>
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>

        <button
          className="person-page__delete"
          onClick={handleDelete}
          disabled={person.direct_reports.length > 0 || del.isPending}
          title={
            person.direct_reports.length > 0
              ? 'Reassign their direct reports first'
              : 'Remove this person from the chart'
          }
        >
          {del.isPending ? 'Removing…' : 'Remove from chart'}
        </button>
      </div>
    </div>
  )
}
