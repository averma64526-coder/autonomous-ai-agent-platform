import { useState, useEffect } from 'react'

interface Approval {
  id: number
  task_id: number
  action: string
  details: string | null
  status: string
  requested_at: string
  responded_at: string | null
}

const API_URL = 'http://localhost:8000/api/v1'

interface Props {
  onBack: () => void
}

function Approvals({ onBack }: Props) {
  const [approvals, setApprovals] = useState<Approval[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [respondingId, setRespondingId] = useState<number | null>(null)

  const fetchApprovals = async () => {
    try {
      setLoading(true)
      const res = await fetch(`${API_URL}/approvals`)
      if (!res.ok) throw new Error('Failed to fetch approvals')
      const data = await res.json()
      setApprovals(data.approvals || [])
      setError(null)
    } catch (err) {
      setError('Approvals load nahi ho paye')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const respond = async (approvalId: number, status: 'approved' | 'rejected') => {
    try {
      setRespondingId(approvalId)
      const res = await fetch(
        `${API_URL}/approvals/${approvalId}/respond`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status }),
        }
      )

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Failed to respond')
      }

      await fetchApprovals()
    } catch (err: any) {
      alert('Error: ' + err.message)
    } finally {
      setRespondingId(null)
    }
  }

  useEffect(() => {
    fetchApprovals()
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-700'
      case 'approved':
        return 'bg-green-100 text-green-700'
      case 'rejected':
        return 'bg-red-100 text-red-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const formatDate = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const pendingApprovals = approvals.filter((a) => a.status === 'pending')
  const allApprovals = approvals

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={onBack}
          className="mb-6 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition"
        >
          ← Back to Dashboard
        </button>

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">
            👤 Human Approvals
          </h1>
          <p className="text-gray-600 mt-2">
            Review and approve sensitive actions
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm">Total</div>
            <div className="text-2xl font-bold text-blue-600">
              {allApprovals.length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm">Pending</div>
            <div className="text-2xl font-bold text-yellow-600">
              {pendingApprovals.length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm">Resolved</div>
            <div className="text-2xl font-bold text-green-600">
              {allApprovals.length - pendingApprovals.length}
            </div>
          </div>
        </div>

        {/* Pending Approvals */}
        {pendingApprovals.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6 border-2 border-yellow-200">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              ⚠️ Pending Approvals ({pendingApprovals.length})
            </h2>
            <div className="space-y-3">
              {pendingApprovals.map((approval) => {
                const isResponding = respondingId === approval.id
                return (
                  <div
                    key={approval.id}
                    className="border border-yellow-300 bg-yellow-50 rounded-lg p-4"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="bg-yellow-200 text-yellow-800 text-xs px-2 py-1 rounded font-bold">
                            ⚠️ NEEDS APPROVAL
                          </span>
                          <span className="text-xs text-gray-500">
                            Task #{approval.task_id}
                          </span>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-1">
                          {approval.action}
                        </h3>
                        {approval.details && (
                          <p className="text-gray-600 text-sm">
                            {approval.details}
                          </p>
                        )}
                        <div className="text-xs text-gray-400 mt-2">
                          Requested: {formatDate(approval.requested_at)}
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-2 mt-3">
                      <button
                        onClick={() => respond(approval.id, 'approved')}
                        disabled={isResponding}
                        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition disabled:opacity-50 text-sm font-medium"
                      >
                        {isResponding ? '⏳ ...' : '✅ Approve'}
                      </button>
                      <button
                        onClick={() => respond(approval.id, 'rejected')}
                        disabled={isResponding}
                        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition disabled:opacity-50 text-sm font-medium"
                      >
                        {isResponding ? '⏳ ...' : '❌ Reject'}
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* All Approvals */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            📋 All Approvals ({allApprovals.length})
          </h2>

          {loading && (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded">
              {error}
            </div>
          )}

          {!loading && allApprovals.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Abhi koi approval request nahi hai.
            </div>
          )}

          <div className="space-y-2">
            {allApprovals.map((approval) => (
              <div
                key={approval.id}
                className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50"
              >
                <div className="flex justify-between items-center">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs px-2 py-1 rounded ${getStatusColor(approval.status)}`}
                      >
                        {approval.status}
                      </span>
                      <span className="text-xs text-gray-500">
                        Task #{approval.task_id}
                      </span>
                      <span className="text-sm font-medium text-gray-900">
                        {approval.action}
                      </span>
                    </div>
                  </div>
                  <div className="text-xs text-gray-400">
                    {formatDate(approval.requested_at)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Approvals