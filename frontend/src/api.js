// Read the backend API base URL from Vite's environment variables and strip any trailing slash.
// Notice: No hardcoded host/port is present in this code.
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')

// Helper to extract a readable error message from API error responses
async function handleError(res) {
  let message = `Request failed (${res.status} ${res.statusText})`
  try {
    const errorData = await res.json()
    if (errorData) {
      if (typeof errorData.detail === 'string') {
        message = errorData.detail
      } else if (Array.isArray(errorData.detail)) {
        // Pydantic 422 validation errors are an array of error objects
        message = errorData.detail.map((err) => err.msg).join(', ')
      } else if (errorData.message) {
        message = errorData.message
      }
    }
  } catch {
    // If response body cannot be parsed as JSON, keep the default status text
  }
  throw new Error(message)
}

// GET /api/notes: Retrieve all notes from the backend
export async function getNotes() {
  const res = await fetch(`${BASE_URL}/api/notes`)
  if (!res.ok) {
    await handleError(res)
  }
  return await res.json()
}

// POST /api/notes: Create a new note with title and optional content
export async function createNote(noteData) {
  const res = await fetch(`${BASE_URL}/api/notes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(noteData),
  })
  if (!res.ok) {
    await handleError(res)
  }
  return await res.json()
}

// PUT /api/notes/{id}: Update title and content of an existing note
export async function updateNote(id, noteData) {
  const res = await fetch(`${BASE_URL}/api/notes/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(noteData),
  })
  if (!res.ok) {
    await handleError(res)
  }
  return await res.json()
}

// DELETE /api/notes/{id}: Delete a note by ID.
// Note: HTTP 204 No Content has no body, so we never call res.json() on it.
export async function deleteNote(id) {
  const res = await fetch(`${BASE_URL}/api/notes/${id}`, {
    method: 'DELETE',
  })
  if (!res.ok) {
    await handleError(res)
  }
  return true
}
