import React, { useState, useEffect, useRef } from 'react';
import './ChatInterface.css';
import { FaUser, FaRobot, FaPaperPlane, FaCog } from 'react-icons/fa';

const ChatInterface = ({ sessionId, onSessionChange }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState(null);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // 清理WebSocket连接
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return wsRef.current;
    }

    const ws = new WebSocket('ws://localhost:8000/api/chat/stream');
    
    ws.onopen = () => {
      console.log('WebSocket连接已建立');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'chunk') {
          // 流式数据块
          setMessages(prev => {
            const newMessages = [...prev];
            const lastIndex = newMessages.length - 1;
            
            if (lastIndex >= 0 && newMessages[lastIndex].type === 'ai' && newMessages[lastIndex].id === streamingMessageId) {
              // 更新正在流式输出的消息
              newMessages[lastIndex] = {
                ...newMessages[lastIndex],
                content: newMessages[lastIndex].content + (data.content || '')
              };
            } else {
              // 创建新的AI消息
              const aiMessage = {
                id: streamingMessageId,
                type: 'ai',
                content: data.content || ''
              };
              newMessages.push(aiMessage);
            }
            return newMessages;
          });
          scrollToBottom();
        } else if (data.type === 'done') {
          // 流式输出完成
          setIsLoading(false);
          setStreamingMessageId(null);
          scrollToBottom();
        } else if (data.type === 'error') {
          // 错误处理
          setIsLoading(false);
          setStreamingMessageId(null);
          const errorMessage = { type: 'error', content: data.error || '发送失败' };
          setMessages(prev => [...prev, errorMessage]);
        }
      } catch (error) {
        console.error('解析WebSocket消息失败:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
      setIsLoading(false);
      setStreamingMessageId(null);
      const errorMessage = { type: 'error', content: 'WebSocket连接错误' };
      setMessages(prev => [...prev, errorMessage]);
    };

    ws.onclose = () => {
      console.log('WebSocket连接已关闭');
    };

    wsRef.current = ws;
    return ws;
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = { type: 'user', content: inputMessage };
    setMessages(prev => [...prev, userMessage]);
    const message = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    // 生成唯一ID用于标识流式消息
    const messageId = Date.now().toString();
    setStreamingMessageId(messageId);

    try {
      const ws = connectWebSocket();
      
      // 等待WebSocket连接
      if (ws.readyState === WebSocket.CONNECTING) {
        await new Promise((resolve, reject) => {
          const timeout = setTimeout(() => {
            reject(new Error('WebSocket连接超时'));
          }, 5000);
          
          ws.onopen = () => {
            clearTimeout(timeout);
            resolve();
          };
          
          ws.onerror = () => {
            clearTimeout(timeout);
            reject(new Error('WebSocket连接失败'));
          };
        });
      }

      if (ws.readyState === WebSocket.OPEN) {
        // 发送消息
        ws.send(JSON.stringify({
          message: message,
          session_id: sessionId
        }));
      } else {
        throw new Error('WebSocket未连接');
      }

    } catch (error) {
      setIsLoading(false);
      setStreamingMessageId(null);
      const errorMessage = { type: 'error', content: error.message || '网络错误，请检查后端服务' };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="session-indicator">
          <FaCog className="session-icon" />
          <span>当前会话: {sessionId}</span>
        </div>
        <div className="session-controls">
          <label>会话ID: </label>
          <input
            type="text"
            value={sessionId}
            onChange={(e) => onSessionChange(e.target.value)}
            placeholder="输入会话ID"
            className="session-input"
          />
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <FaRobot className="welcome-icon" />
            <h3>欢迎使用期末复习助手！</h3>
            <p>请提出您的复习问题，我会基于知识库为您提供准确的答案。</p>
          </div>
        )}
        {messages.map((msg, index) => (
          <div key={msg.id || index} className={`message ${msg.type}`}>
            <div className="message-avatar">
              {msg.type === 'user' ? <FaUser /> : <FaRobot />}
            </div>
            <div className="message-content">
              <div className="message-text">
                {msg.content}
                {isLoading && msg.id === streamingMessageId && (
                  <span className="streaming-cursor">▋</span>
                )}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message ai loading">
            <div className="message-avatar">
              <FaRobot />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的复习问题..."
            disabled={isLoading}
            rows="3"
            className="message-input"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="send-button"
          >
            <FaPaperPlane />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;