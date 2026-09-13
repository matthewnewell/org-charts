export interface Person {
  id: string
  name: string
  title: string
  department: string | null
  manager_id: string | null
  manager_name: string | null
  direct_report_count?: number
}

export interface PersonDetail extends Person {
  ancestors: Person[]
  direct_reports: Person[]
  subtree_size: number
}
