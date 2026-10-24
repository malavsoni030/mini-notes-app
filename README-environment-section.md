## Frontend environment variables

Create `frontend/.env` from `frontend/.env.example` and fill in your own values.
Do not commit real environment files or secrets.

| Variable | Description |
| --- | --- |
| `VITE_API_BASE_URL` | Base URL for the existing backend API |
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Supabase publishable key used by the frontend |

Install the Supabase JavaScript client in `frontend/` if it is not already installed:

```bash
npm install @supabase/supabase-js
```
