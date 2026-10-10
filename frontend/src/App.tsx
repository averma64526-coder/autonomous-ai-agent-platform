import { useState, useEffect } from 'react'

interface Goal {
  id: number
  title: string
  description: string | null
  status: string
  created_at: string
}

const API_URL = 'http://localhost:8000/api/v1'

function App() {
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  // Fetch goals from backend
  const fetchGoals = async () => {
    try {
      setLoading(true)
      const res = await fetch(`${API_URL}/goals`)
      if (!res.ok) throw new Error('Failed to fetch goals')
      const data = await res.json()
      setGoals(data.goals || [])
      setError(null)
    } catch (err) {
      setError('Backend se connect nahi ho pa raha. Check karo backend chal raha hai.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Create new goal
  const createGoal = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError(null)

    if (!title.trim()) {
      setFormError('Title zaroori hai')
      return
    }

    try {
      setCreating(true)
      const res = await fetch(`${API_URL}/goals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim() || null,
        }),
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Failed to create goal')
      }

      // Success - reset form and refresh list
      setTitle('')
      setDescription('')
      setShowForm(false)
      await fetchGoals()
    } catch (err: any) {
      setFormError(err.message || 'Kuch galat ho gaya')
    } finally {
      setCreating(false)
    }
  }

  useEffect(() => {
    fetchGoals()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">
            🤖 Autonomous AI Agent Platform
          </h1>
          <p className="text-gray-600 mt-2">
            AI-powered autonomous agent system
          </p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm">Total Goals</div>
            <div className="text-3xl font-bold text-blue-600">{goals.length}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm">Backend</div>
            <div className="text-lg font-semibold text-green-600">
              {error ? '❌ Offline' : '✅ Online'}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm">Port</div>
            <div className="text-lg font-semibold text-gray-700">8000</div>
          </div>
        </div>

        {/* Goals Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">📋 Your Goals</h2>
            <div className="flex gap-2">
              <button
                onClick={fetchGoals}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition"
              >
                🔄 Refresh
              </button>
              <button
                onClick={() => setShowForm(!showForm)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
              >
                {showForm ? '✕ Cancel' : '+ New Goal'}
              </button>
            </div>
          </div>

          {/* Create Goal Form */}
          {showForm && (
            <form
              onSubmit={createGoal}
              className="mb-6 p-4 border-2 border-blue-200 rounded-lg bg-blue-50"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                ✨ Create New Goal
              </h3>

              {formError && (
                <div className="mb-4 bg-red-100 border border-red-300 text-red-700 p-3 rounded text-sm">
                  {formError}
                </div>
              )}

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Build a personal blog"
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={creating}
                  maxLength={255}
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (optional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="What do you want to achieve?"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  disabled={creating}
                />
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {creating ? '⏳ Creating...' : '🚀 Create Goal'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  disabled={creating}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* Goals List */}
          {loading && (
            <div className="text-center py-8 text-gray-500">
              Loading goals...
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded">
              {error}
            </div>
          )}

          {!loading && !error && goals.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Abhi koi goal nahi hai. Upar "+ New Goal" button dabao!
            </div>
          )}

          <div className="space-y-4">
            {goals.map((goal) => (
              <div
                key={goal.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                        #{goal.id}
                      </span>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {goal.title}
                      </h3>
                    </div>
                    {goal.description && (
                      <p className="text-gray-600 text-sm mb-3">
                        {goal.description}
                      </p>
                    )}
                    <span
                      className={`inline-block text-xs px-2 py-1 rounded ${
                        goal.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-700'
                          : goal.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}
                    >
                      {goal.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          Backend:{' '}
          <a
            href="http://localhost:8000/docs"
            className="text-blue-600 hover:underline"
          >
            http://localhost:8000/docs
          </a>
        </div>
      </div>
    </div>
  )
}

export default App