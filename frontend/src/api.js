import { supabase } from './supabaseClient'

// Read the latest session before each request so the token stays current.
async function authorizedFetch(url, options = {}) {
  const { data: { session } } = await supabase.auth.getSession()
  const headers = new Headers(options.headers || {})
  if (session?.access_token) {
    headers.set('Authorization', `Bearer ${session.access_token}`)
  }

  const res = await fetch(url, { ...options, headers })
  if (res.status === 401) {
    // An expired/invalid API session should return the app to the login screen.
    await supabase.auth.signOut()
    const error = new Error('Your session expired. Please log in again.')
    error.status = 401
    throw error
  }
  return res
}

// Keep the API URL configurable and avoid trailing-slash issues.
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')

// Turn API error responses into readable messages.
async function handleError(res) {
  let message = `Request failed (${res.status} ${res.statusText})`
  try {
    const errorData = await res.json()
    if (typeof errorData?.detail === 'string') {
      message = errorData.detail
    } else if (Array.isArray(errorData?.detail)) {
      message = errorData.detail.map((err) => err.msg).join(', ')
    } else if (errorData?.message) {
      message = errorData.message
    }
  } catch {
    // Keep the default message when the response isn't JSON.
  }
  const error = new Error(message)
  error.status = res.status
  throw error
}

// GET /api/notes: retrieve notes for the signed-in user.
export async function getNotes() {
  const res = await authorizedFetch(`${BASE_URL}/api/notes`)
  if (!res.ok) await handleError(res)
  return res.json()
}

// POST /api/notes: create a note.
export async function createNote(noteData) {
  const res = await authorizedFetch(`${BASE_URL}/api/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(noteData),
  })
  if (!res.ok) await handleError(res)
  return res.json()
}

// PUT /api/notes/{id}: update a note.
export async function updateNote(id, noteData) {
  const res = await authorizedFetch(`${BASE_URL}/api/notes/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(noteData),
  })
  if (!res.ok) await handleError(res)
  return res.json()
}

// DELETE /api/notes/{id}: delete a note.
export async function deleteNote(id) {
  const res = await authorizedFetch(`${BASE_URL}/api/notes/${id}`, { method: 'DELETE' })
  if (!res.ok) await handleError(res)
  return true
}
