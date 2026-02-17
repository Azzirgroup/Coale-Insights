import { call } from 'frappe-ui'

export async function apiCall<T>(method: string, params?: Record<string, any>): Promise<T> {
  const response = await call(method, params)
  if (response?.status === 'error') throw new Error(response.message)
  return response?.data ?? response
}