import React, { useState, useEffect } from 'react';
import './SessionManager.css';
import { FaHistory, FaTrash, FaPlay, FaSync, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';

const SessionManager = ({ onSessionSelect, currentSession }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const fetchSessions = async () => {
    try {
      setRefreshing(true);
      const response = await fetch('http://localhost:8000/api/sessions');
      const data = await response.json();

      if (response.ok) {
        setSessions(data.sessions);
        setError('');
      } else {
        setError('获取会话列表失败');
      }
    } catch (error) {
      setError('网络错误，请检查后端服务');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!window.confirm(`确定要删除会话 "${sessionId}" 吗？`)) return;

    try {
      const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // 重新获取会话列表
        fetchSessions();
      } else {
        setError('删除会话失败');
      }
    } catch (error) {
      setError('网络错误');
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  return (
    <div className="session-manager">
      <div className="session-header">
        <div className="header-content">
          <FaHistory className="header-icon" />
          <div className="header-text">
            <h2>复习会话管理</h2>
            <p>管理您的复习问答会话历史记录。</p>
          </div>
        </div>
        <button
          onClick={fetchSessions}
          className="refresh-button"
          disabled={refreshing}
        >
          {refreshing ? (
            <>
              <div className="spinner"></div>
              刷新中...
            </>
          ) : (
            <>
              <FaSync className="button-icon" />
              刷新列表
            </>
          )}
        </button>
      </div>

      {loading && !refreshing && (
        <div className="loading-state">
          <div className="spinner large"></div>
          <p>加载中...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <FaExclamationTriangle className="error-icon" />
          <span>{error}</span>
        </div>
      )}

      <div className="sessions-list">
        {sessions.map((session) => (
          <div key={session.session_id} className="session-item">
            <div className="session-main">
              <div className="session-info">
                <h3 className="session-id">{session.session_id}</h3>
                <p className="message-count">
                  <FaCheckCircle className="count-icon" />
                  {session.message_count} 条消息
                </p>
              </div>
              {currentSession === session.session_id && (
                <span className="current-badge">
                  <FaPlay className="current-icon" />
                  当前会话
                </span>
              )}
            </div>
            <div className="session-actions">
              <button
                onClick={() => onSessionSelect(session.session_id)}
                className={`action-button select ${currentSession === session.session_id ? 'active' : ''}`}
                title="选择此会话"
              >
                <FaPlay className="action-icon" />
                {currentSession === session.session_id ? '当前' : '选择'}
              </button>
              <button
                onClick={() => deleteSession(session.session_id)}
                className="action-button delete"
                title="删除此会话"
              >
                <FaTrash className="action-icon" />
                删除
              </button>
            </div>
          </div>
        ))}

        {sessions.length === 0 && !loading && (
          <div className="empty-state">
            <FaHistory className="empty-icon" />
            <h3>暂无会话记录</h3>
            <p>开始您的第一次复习问答，对话历史将显示在这里。</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SessionManager;
