import React, { useState, useEffect, useCallback } from 'react';
import { http } from '@tauri-apps/api';
import { socket } from '../socket';

const DeadEndShelf = () => {
  const [deadEndTasks, setDeadEndTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState('default-session');
  const [retryingTasks, setRetryingTasks] = useState(new Set());

  // Fetch dead-end tasks from backend
  const fetchDeadEndTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await http.fetch(`http://localhost:8000/api/dead-ends?session_id=${sessionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setDeadEndTasks(response.data || []);
    } catch (e) {
      console.error("Failed to fetch dead-end tasks:", e);
      setError(`Failed to load dead-end tasks: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Initial data fetch
  useEffect(() => {
    fetchDeadEndTasks();
  }, [fetchDeadEndTasks]);

  // WebSocket listeners for real-time updates
  useEffect(() => {
    const handleDeadEndAdded = (data) => {
      console.log('Dead-end task added:', data);
      setDeadEndTasks(current => [...current, data]);
    };

    const handleDeadEndRetry = (data) => {
      console.log('Dead-end task retry:', data);
      setDeadEndTasks(current => 
        current.filter(task => task.task_id !== data.task_id)
      );
      setRetryingTasks(current => {
        const newSet = new Set(current);
        newSet.delete(data.task_id);
        return newSet;
      });
    };

    // Register WebSocket event listeners
    socket.on('dead_end_added', handleDeadEndAdded);
    socket.on('dead_end_retry', handleDeadEndRetry);

    // Cleanup listeners on unmount
    return () => {
      socket.off('dead_end_added', handleDeadEndAdded);
      socket.off('dead_end_retry', handleDeadEndRetry);
    };
  }, []);

  // Retry a dead-end task
  const handleRetryTask = useCallback(async (taskId) => {
    try {
      setRetryingTasks(current => new Set([...current, taskId]));
      
      const response = await http.fetch(`http://localhost:8000/api/dead-ends/${taskId}/retry`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Task will be removed from list via WebSocket event
    } catch (e) {
      console.error("Failed to retry task:", e);
      setRetryingTasks(current => {
        const newSet = new Set(current);
        newSet.delete(taskId);
        return newSet;
      });
      // Show error message to user
      alert(`Failed to retry task: ${e.message}`);
    }
  }, []);

  // Mark task as permanently failed (remove from shelf)
  const handleMarkComplete = useCallback(async (taskId) => {
    try {
      // For now, just remove from local state
      // In a real implementation, you might want to call an API endpoint
      setDeadEndTasks(current => 
        current.filter(task => task.id !== taskId)
      );
    } catch (e) {
      console.error("Failed to mark task as complete:", e);
    }
  }, []);

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (e) {
      return timestamp;
    }
  };

  // Get task priority based on retry attempts
  const getTaskPriority = (task) => {
    const attempts = task.attempted_solutions?.length || 0;
    if (attempts === 0) return 'high';
    if (attempts < 3) return 'medium';
    return 'low';
  };

  return (
    <div className="pane dead-end-shelf">
      <div className="pane-header">
        <h2>💀 Dead-End Shelf</h2>
        <div className="shelf-controls">
          <button onClick={fetchDeadEndTasks} className="btn-refresh" disabled={loading}>
            {loading ? '⟳' : '🔄'} Refresh
          </button>
          <div className="task-count">
            {deadEndTasks.length} task{deadEndTasks.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>

      <div className="pane-content">
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
            <button onClick={fetchDeadEndTasks} className="btn-retry">
              Try Again
            </button>
          </div>
        )}

        {loading && !error && (
          <div className="loading-message">
            <span className="loading-spinner">⟳</span>
            <span>Loading dead-end tasks...</span>
          </div>
        )}

        {!loading && !error && deadEndTasks.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🎉</div>
            <h3>No Dead-End Tasks</h3>
            <p>All tasks are progressing smoothly! Dead-end tasks will appear here when they need attention.</p>
          </div>
        )}

        {!loading && !error && deadEndTasks.length > 0 && (
          <div className="dead-end-list">
            {deadEndTasks.map((task) => (
              <div key={task.id} className={`dead-end-item priority-${getTaskPriority(task)}`}>
                <div className="task-header">
                  <div className="task-title">
                    <span className="task-id">#{task.task_id}</span>
                    <span className={`priority-badge priority-${getTaskPriority(task)}`}>
                      {getTaskPriority(task)} priority
                    </span>
                  </div>
                  <div className="task-timestamp">
                    {formatTimestamp(task.timestamp)}
                  </div>
                </div>

                <div className="task-reason">
                  <strong>Reason:</strong> {task.reason}
                </div>

                {task.original_input && Object.keys(task.original_input).length > 0 && (
                  <div className="task-input">
                    <strong>Original Input:</strong>
                    <div className="input-preview">
                      {JSON.stringify(task.original_input, null, 2).substring(0, 200)}
                      {JSON.stringify(task.original_input).length > 200 && '...'}
                    </div>
                  </div>
                )}

                {task.attempted_solutions && task.attempted_solutions.length > 0 && (
                  <div className="attempted-solutions">
                    <strong>Attempted Solutions ({task.attempted_solutions.length}):</strong>
                    <ul className="solutions-list">
                      {task.attempted_solutions.slice(0, 3).map((solution, index) => (
                        <li key={index} className="solution-item">
                          {solution}
                        </li>
                      ))}
                      {task.attempted_solutions.length > 3 && (
                        <li className="solution-item more">
                          +{task.attempted_solutions.length - 3} more attempts
                        </li>
                      )}
                    </ul>
                  </div>
                )}

                <div className="task-actions">
                  {task.can_retry && (
                    <button
                      onClick={() => handleRetryTask(task.id)}
                      disabled={retryingTasks.has(task.id)}
                      className="btn-retry-task"
                    >
                      {retryingTasks.has(task.id) ? (
                        <>
                          <span className="loading-spinner">⟳</span>
                          Retrying...
                        </>
                      ) : (
                        <>
                          🔄 Retry Task
                        </>
                      )}
                    </button>
                  )}
                  
                  <button
                    onClick={() => handleMarkComplete(task.id)}
                    className="btn-mark-complete"
                  >
                    ✅ Mark as Complete
                  </button>
                  
                  <button
                    onClick={() => {
                      // Copy task details to clipboard for manual investigation
                      navigator.clipboard.writeText(JSON.stringify(task, null, 2));
                      alert('Task details copied to clipboard');
                    }}
                    className="btn-copy-details"
                  >
                    📋 Copy Details
                  </button>
                </div>

                {!task.can_retry && (
                  <div className="retry-disabled-notice">
                    <span className="notice-icon">⚠️</span>
                    This task cannot be automatically retried. Manual intervention may be required.
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Help section */}
      <div className="shelf-help">
        <details className="help-details">
          <summary className="help-summary">ℹ️ About Dead-End Tasks</summary>
          <div className="help-content">
            <p>
              Dead-end tasks are workflow steps that have failed or stalled and require attention. 
              They appear here when:
            </p>
            <ul>
              <li>A task has exhausted all automatic retry attempts</li>
              <li>An error condition prevents further progress</li>
              <li>Human intervention is needed to resolve the issue</li>
            </ul>
            <p>
              Use the <strong>Retry Task</strong> button to attempt the task again, or 
              <strong>Mark as Complete</strong> if you've resolved the issue manually.
            </p>
          </div>
        </details>
      </div>
    </div>
  );
};

export default DeadEndShelf;
