export interface Person {
  id: string
  name: string
  title: string
  department: string | null
  manager_id: string | null
  manager_name: string | null
  labor_category: string | null
  // The Function their category rolls up into (see backend's FUNCTION_CATEGORIES) — null for
  // anyone with no labor_category (a manager, an admin role like Portfolio Manager).
  function: string | null
  direct_report_count?: number
}

export interface PersonDetail extends Person {
  ancestors: Person[]
  direct_reports: Person[]
  subtree_size: number
}

export interface FunctionRow {
  id: string
  name: string
  categories: string[]
  manager_id: string | null
  manager_name: string | null
  people_count: number
}
