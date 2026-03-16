import React, { useState } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import SessionManager from './components/SessionManager';
import KnowledgeBaseManager from './components/KnowledgeBaseManager';
import { FaRobot, FaHistory, FaGraduationCap, FaBars, FaTimes, FaDatabase } from 'react-icons/fa';

function App() {
  const [currentView, setCurrentView] = useState('chat'); // 'chat', 'knowledge', 'sessions'
  const [currentSession, setCurrentSession] = useState('default');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  const navItems = [
    { id: 'chat', icon: FaRobot, label: '复习问答' },
    { id: 'knowledge', icon: FaDatabase, label: '知识库管理' },
    { id: 'sessions', icon: FaHistory, label: '会话管理' }
  ];

  return (
    <div className="App">
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <FaGraduationCap className="logo-icon" />
          <h2>复习助手</h2>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setCurrentView(item.id);
                  closeSidebar();
                }}
                className={`nav-item ${currentView === item.id ? 'active' : ''}`}
              >
                <IconComponent className="nav-icon" />
                <span className="nav-label">{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <p>期末复习助手</p>
          <small>基于RAG的智能检索系统</small>
        </div>
      </aside>

      <div className="main-content">
        <header className="top-header">
          <button className="menu-toggle" onClick={toggleSidebar}>
            {sidebarOpen ? <FaTimes /> : <FaBars />}
          </button>
          <h1 className="page-title">
            {navItems.find(item => item.id === currentView)?.label}
          </h1>
          <div className="header-spacer"></div>
        </header>

        <main className="page-content">
          {currentView === 'chat' && (
            <ChatInterface
              sessionId={currentSession}
              onSessionChange={setCurrentSession}
            />
          )}
          {currentView === 'knowledge' && <KnowledgeBaseManager />}
          {currentView === 'sessions' && (
            <SessionManager
              onSessionSelect={setCurrentSession}
              currentSession={currentSession}
            />
          )}
        </main>
      </div>

      {sidebarOpen && <div className="sidebar-overlay" onClick={closeSidebar}></div>}
    </div>
  );
}

export default App;
