import { useEffect, useRef, useState } from 'react'
import { createNote, deleteNote, getNotes, updateNote } from './api'
import './App.css'

function App() {
  // --- React State ---
  // List of all notes fetched from the backend database
  const [notes, setNotes] = useState([])
  // Form input states
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')

  // Client-side validation error for the title field
  const [errorMessage, setErrorMessage] = useState('')
  // ID of the note currently being edited (null = create mode)
  const [editingNoteId, setEditingNoteId] = useState(null)

  // Asynchronous status states for user feedback
  const [isLoading, setIsLoading] = useState(true)
  const [apiError, setApiError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  // Disables buttons during API calls to prevent duplicate submissions
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Reference for managing the success message auto-dismiss timer
  const successTimeoutRef = useRef(null)

  // Display a temporary success alert that clears after 3.5 seconds
  const showSuccess = (msg) => {
    setSuccessMessage(msg)
    if (successTimeoutRef.current) {
      clearTimeout(successTimeoutRef.current)
    }
    successTimeoutRef.current = setTimeout(() => {
      setSuccessMessage('')
    }, 3500)
  }

  // Fetch all notes from the backend API
  const loadNotes = async () => {
    try {
      setIsLoading(true)
      setApiError('')
      const data = await getNotes()
      setNotes(data)
    } catch (err) {
      setApiError(err.message || 'Failed to load notes. Please ensure the backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  // Load notes once when the component mounts
  useEffect(() => {
    loadNotes()
    return () => {
      if (successTimeoutRef.current) {
        clearTimeout(successTimeoutRef.current)
      }
    }
  }, [])

  // Clear client validation error when user begins typing a valid title
  const handleTitleChange = (e) => {
    setTitle(e.target.value)
    if (errorMessage && e.target.value.trim() !== '') {
      setErrorMessage('')
    }
  }

  // Handle form submission for creating or updating a note
  const handleSubmit = async (e) => {
    e.preventDefault()

    // Client-side validation: title cannot be empty or only whitespace
    const trimmedTitle = title.trim()
    if (!trimmedTitle) {
      setErrorMessage('Title is required.')
      return
    }

    setIsSubmitting(true)
    setApiError('')

    try {
      if (editingNoteId !== null) {
        // Update existing note
        await updateNote(editingNoteId, { title: trimmedTitle, content })
        showSuccess('Note updated successfully!')
        setEditingNoteId(null)
      } else {
        // Create new note
        await createNote({ title: trimmedTitle, content })
        showSuccess('Note created successfully!')
      }

      // Reset form fields
      setTitle('')
      setContent('')
      setErrorMessage('')

      // Reload notes so the UI strictly matches the backend database
      await loadNotes()
    } catch (err) {
      setApiError(err.message || 'Failed to save note. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Populate form with existing note data to start editing
  const handleEdit = (note) => {
    setEditingNoteId(note.id)
    setTitle(note.title)
    setContent(note.content || '')
    setErrorMessage('')
    setApiError('')
  }

  // Exit edit mode and reset the form
  const handleCancel = () => {
    setEditingNoteId(null)
    setTitle('')
    setContent('')
    setErrorMessage('')
  }

  // Delete a note by its ID
  const handleDelete = async (id) => {
    setIsSubmitting(true)
    setApiError('')

    try {
      await deleteNote(id)
      showSuccess('Note deleted successfully!')

      // If the deleted note was currently loaded in the form, reset edit mode
      if (editingNoteId === id) {
        handleCancel()
      }

      // Reload notes from the backend
      await loadNotes()
    } catch (err) {
      setApiError(err.message || 'Failed to delete note. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Notes App</h1>
        <p className="app-subtitle">Capture and organize your thoughts</p>
      </header>

      {/* Global API Feedback Banners */}
      {apiError && (
        <div className="status-banner banner-error" role="alert">
          <span>{apiError}</span>
          <button
            type="button"
            className="banner-close"
            onClick={() => setApiError('')}
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      {successMessage && (
        <div className="status-banner banner-success" role="status">
          <span>{successMessage}</span>
        </div>
      )}

      {/* Note Creation / Editing Form */}
      <section className="form-card">
        <h2>{editingNoteId !== null ? 'Edit Note' : 'Create a New Note'}</h2>
        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="note-title">
              Title <span className="required-star">*</span>
            </label>
            <input
              id="note-title"
              type="text"
              placeholder="Enter note title..."
              value={title}
              onChange={handleTitleChange}
              className={errorMessage ? 'input-error' : ''}
              disabled={isSubmitting}
            />
            {/* Inline validation error */}
            {errorMessage && (
              <span className="error-text" role="alert">
                {errorMessage}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="note-content">Content</label>
            <textarea
              id="note-content"
              placeholder="Enter note content (optional)..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={4}
              disabled={isSubmitting}
            />
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {editingNoteId !== null ? 'Update Note' : 'Create Note'}
            </button>
            {/* Cancel button only shows when in edit mode */}
            {editingNoteId !== null && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleCancel}
                disabled={isSubmitting}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </section>

      {/* Notes List Section */}
      <section className="notes-section">
        <h2>All Notes ({notes.length})</h2>

        {/* Loading state while notes are fetching */}
        {isLoading ? (
          <div className="loading-state">
            <p className="loading-message">Loading notes...</p>
          </div>
        ) : notes.length === 0 ? (
          /* Empty state when no notes exist */
          <div className="empty-state">
            <p className="empty-message">
              No notes yet. Create your first note above.
            </p>
          </div>
        ) : (
          /* Note cards grid */
          <div className="notes-grid">
            {notes.map((note) => (
              <article key={note.id} className="note-card">
                <div className="note-body">
                  <h3 className="note-title">{note.title}</h3>
                  {note.content ? (
                    <p className="note-content">{note.content}</p>
                  ) : (
                    <p className="note-content-empty">No content provided.</p>
                  )}
                </div>

                <div className="note-actions">
                  <button
                    type="button"
                    className="btn btn-sm btn-outline"
                    onClick={() => handleEdit(note)}
                    disabled={isSubmitting}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="btn btn-sm btn-danger"
                    onClick={() => handleDelete(note.id)}
                    disabled={isSubmitting}
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

export default App
