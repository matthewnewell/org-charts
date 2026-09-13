import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type { Person, PersonDetail } from './types'

export function useRootPeople() {
  return useQuery({
    queryKey: ['people', 'root'],
    queryFn: () => api.get<Person[]>('/people?root=true'),
  })
}

export function usePersonReports(personId: string | null) {
  return useQuery({
    queryKey: ['people', personId, 'reports'],
    queryFn: () => api.get<Person[]>(`/people/${personId}/reports`),
    enabled: !!personId,
  })
}

export function usePerson(personId: string | undefined) {
  return useQuery({
    queryKey: ['people', personId],
    queryFn: () => api.get<PersonDetail>(`/people/${personId}`),
    enabled: !!personId,
  })
}

export function useDepartments() {
  return useQuery({
    queryKey: ['departments'],
    queryFn: () => api.get<string[]>('/people/departments'),
  })
}

function useInvalidatePeople() {
  const qc = useQueryClient()
  return () => qc.invalidateQueries({ queryKey: ['people'] })
}

export function useCreatePerson() {
  const invalidate = useInvalidatePeople()
  return useMutation({
    mutationFn: (data: { name: string; title: string; department?: string; manager_id?: string }) =>
      api.post<Person>('/people', data),
    onSuccess: invalidate,
  })
}

export function useUpdatePerson() {
  const invalidate = useInvalidatePeople()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Pick<Person, 'name' | 'title' | 'department' | 'manager_id'>> }) =>
      api.put<Person>(`/people/${id}`, data),
    onSuccess: invalidate,
  })
}

export function useDeletePerson() {
  const invalidate = useInvalidatePeople()
  return useMutation({
    mutationFn: (id: string) => api.del(`/people/${id}`),
    onSuccess: invalidate,
  })
}
