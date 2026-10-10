import { useState, useEffect } from 'react'

interface Task {
  id: number
  goal_id: number
  title: string
  description: string | null
  status: string
  order: number
  result: string | null
  error: string | null
  created_at: string
}

interface Goal {
  id: number
  title: string
  description: string | null
  status: string
  created_at: string
}

interface LogEntry {
  id: number
  agent_type: string
  level: string
  message: string
  details: string | null
  created_at: string
}

const API_URL = 'http://localhost:8000/api/v1'

interface Props {
  goalId: number
  onBack: () => void
}

function GoalDetail({ goalId, onBack }: Props) {
  const [goal, setGoal] = useState<Goal | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [decomposing, setDecomposing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [decomposeError, setDecomposeError] = useState<string | null>(null)
  const [executingTaskId, setExecutingTaskId] = useState<number | null>(null)
  const [expandedTaskId, setExpandedTaskId] = useState<number | null>(null)
  const [showLogs, setShowLogs] = useState(true)

  const fetchData = async () => {
    try {
      setLoading(true)
      const goalRes = await fetch(`${API_URL}/goals/${goalId}`)
      if (!goalRes.ok) throw new Error('Goal not found')
      const goalData = await goalRes.json()
      setGoal(goalData)

      const tasksRes = await fetch(`${API_URL}/tasks/by-goal/${goalId}`)
      let allTasks: Task[] = []
      if (tasksRes.ok) {
        allTasks = await tasksRes.json()
        setTasks(allTasks || [])
      }

      const allLogs: LogEntry[] = []
      for (const task of allTasks) {
        const logsRes = await fetch(`${API_URL}/tasks/${task.id}/logs`)
        if (logsRes.ok) {
          const taskLogs = await logsRes.json()
          allLogs.push(...taskLogs)
        }
      }
      allLogs.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      setLogs(allLogs)

      setError(null)
    } catch (err) {
      setError('Data load nahi ho paya')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const decomposeGoal = async () => {
    setDecomposeError(null)
    try {
      setDecomposing(true)
      const res = await fetch(`${API_URL}/goals/${goalId}/decompose`, {
        method: 'POST',
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Decompose failed')
      }

      await fetchData()
    } catch (err: any) {
      setDecomposeError(err.message || 'AI decompose nahi kar paya')
    } finally {
      setDecomposing(false)
    }
  }

  const executeTask = async (taskId: number) => {
    try {
      setExecutingTaskId(taskId)
      const res = await fetch(`${API_URL}/tasks/${taskId}/execute`, {
        method: 'POST',
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Execution failed')
      }

      await fetchData()
      setExpandedTaskId(taskId)
    } catch (err: any) {
      alert('Execution error: ' + err.message)
    } finally {
      setExecutingTaskId(null)
    }
  }

  useEffect(() => {
    fetchData()
  }, [goalId])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-700'
      case 'running':
        return 'bg-blue-100 text-blue-700'
      case 'completed':
        return 'bg-green-100 text-green-700'
      case 'failed':
        return 'bg-red-100 text-red-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const getLogColor = (level: string) => {
    switch (level) {
      case 'info':
        return 'text-blue-600'
      case 'success':
        return 'text-green-600'
      case 'warning':
        return 'text-yellow-600'
      case 'error':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'info':
        return 'ℹ️'
      case 'success':
        return '✅'
      case 'warning':
        return '⚠️'
      case 'error':
        return '❌'
      default:
        return '📝'
    }
  }

  const formatTime = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (error || !goal) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={onBack}
            className="mb-4 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            ← Back to Dashboard
          </button>
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded">
            {error || 'Goal not found'}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={onBack}
          className="mb-6 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition"
        >
          ← Back to Dashboard
        </button>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center gap-3 mb-3">
            <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
              #{goal.id}
            </span>
            <span
              className={`text-xs px-2 py-1 rounded ${getStatusColor(goal.status)}`}
            >
              {goal.status}
            </span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {goal.title}
          </h1>
          {goal.description && (
            <p className="text-gray-600">{goal.description}</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                🤖 AI Task Decomposition
              </h2>
              <p className="text-gray-600 text-sm mt-1">
                Let AI break this goal into actionable tasks
              </p>
            </div>
            <button
              onClick={decomposeGoal}
              disabled={decomposing || tasks.length > 0}
              className="px-5 py-2.5 bg-purple-600 text-white rounded hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {decomposing
                ? '⏳ AI thinking...'
                : tasks.length > 0
                ? '✓ Tasks created'
                : '✨ Decompose with AI'}
            </button>
          </div>

          {decomposeError && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 p-3 rounded text-sm">
              {decomposeError}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            📋 Tasks ({tasks.length})
          </h2>

          {tasks.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Abhi koi task nahi hai. Upar "Decompose with AI" button dabao!
            </div>
          )}

          <div className="space-y-3">
            {tasks.map((task) => {
              const isExecuting = executingTaskId === task.id
              const isExpanded = expandedTaskId === task.id
              const canExecute = task.status === 'pending'

              return (
                <div
                  key={task.id}
                  className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition"
                >
                  <div className="p-4">
                    <div className="flex items-start gap-3">
                      <span className="bg-gray-100 text-gray-600 text-xs font-bold px-2 py-1 rounded flex-shrink-0">
                        {task.order}
                      </span>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1">
                          {task.title}
                        </h3>
                        {task.description && (
                          <p className="text-gray-600 text-sm mb-2">
                            {task.description}
                          </p>
                        )}
                        <div className="flex items-center gap-2 flex-wrap">
                          <span
                            className={`inline-block text-xs px-2 py-1 rounded ${getStatusColor(task.status)}`}
                          >
                            {task.status}
                          </span>

                          {canExecute && (
                            <button
                              onClick={() => executeTask(task.id)}
                              disabled={isExecuting}
                              className="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition disabled:opacity-50"
                            >
                              {isExecuting ? '⏳ Executing...' : '⚡ Execute'}
                            </button>
                          )}

                          {task.result && (
                            <button
                              onClick={() =>
                                setExpandedTaskId(isExpanded ? null : task.id)
                              }
                              className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition"
                            >
                              {isExpanded ? '▲ Hide result' : '▼ View result'}
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {isExpanded && task.result && (
                    <div className="bg-gray-50 border-t border-gray-200 p-4">
                      <div className="text-sm">
                        <div className="font-semibold text-gray-700 mb-2">
                          🎯 Result:
                        </div>
                        <div className="text-gray-600 whitespace-pre-wrap mb-3">
                          {task.result}
                        </div>
                        {task.error && (
                          <div className="text-red-600 text-xs">
                            Error: {task.error}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Activity Feed */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              📊 Agent Activity Feed ({logs.length})
            </h2>
            <button
              onClick={() => setShowLogs(!showLogs)}
              className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              {showLogs ? 'Hide' : 'Show'}
            </button>
          </div>

          {showLogs && logs.length === 0 && (
            <div className="text-center py-6 text-gray-500 text-sm">
              Abhi koi activity nahi. Task execute karo to logs aayenge!
            </div>
          )}

          {showLogs && logs.length > 0 && (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className="flex items-start gap-3 p-2 hover:bg-gray-50 rounded text-sm border-l-2 border-gray-200 pl-3"
                >
                  <span className="text-lg flex-shrink-0">
                    {getLogIcon(log.level)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                        {log.agent_type}
                      </span>
                      <span className="text-xs text-gray-400">
                        {formatTime(log.created_at)}
                      </span>
                    </div>
                    <div className={`${getLogColor(log.level)} break-words`}>
                      {log.message}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default GoalDetail