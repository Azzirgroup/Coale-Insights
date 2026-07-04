import { call } from 'frappe-ui'

/**
 * Thin wrapper around frappe-ui's `call` that normalises errors into readable,
 * user-facing messages.
 *
 * frappe-ui's request handler crashes with
 *   "Cannot read properties of undefined (reading 'exc_type')"
 * whenever the server returns a non-OK response whose body is NOT valid JSON
 * (e.g. a gateway timeout / 502 / 504 HTML page, an empty body, or a proxy
 * error). The heavy ML endpoints (Customer Intelligence, Executive Dashboard)
 * are the most likely to hit that path. We catch it here so the UI shows a
 * graceful message instead of the raw TypeError.
 */
export async function apiCall<T>(method: string, params?: Record<string, any>): Promise<T> {
  let response: any
  try {
    response = await call(method, params)
  } catch (e: any) {
    throw new Error(normaliseError(e))
  }
  if (response?.status === 'error') {
    throw new Error(response.message || 'Something went wrong')
  }
  const payload = response?.data ?? response
  // Some endpoints wrap a "no data" / error signal inside the payload while the
  // outer status is "success" (e.g. {status:'success', data:{status:'error', message:'No ... data found'}}).
  // Surface it so the page shows a clear message instead of blank widgets.
  if (payload && typeof payload === 'object' && (payload as any).status === 'error') {
    throw new Error((payload as any).message || 'No data available')
  }
  return payload as T
}

function normaliseError(e: any): string {
  // frappe-ui failed while parsing a non-JSON error body -> its own TypeError.
  if (e instanceof TypeError && /exc_type/.test(e?.message || '')) {
    return 'The server took too long or returned an unexpected response. Please try again in a moment.'
  }
  // frappe-ui attaches parsed server messages / exception info when the body is JSON.
  if (Array.isArray(e?.messages) && e.messages.length) {
    return e.messages.join('\n')
  }
  if (e?.exc_type) {
    return e._error_message || e.message || e.exc_type
  }
  const msg = (e?.message || '').trim()
  if (!msg || /exc_type/.test(msg)) {
    return 'Unable to load data. Please try again.'
  }
  return msg
}
