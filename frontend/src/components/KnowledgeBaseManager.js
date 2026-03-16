import React, { useState, useEffect } from 'react';
import './KnowledgeBaseManager.css';
import { FaTrash, FaFileAlt, FaSync, FaCloudUploadAlt, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';

const KnowledgeBaseManager = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // 文件上传相关状态
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadResults, setUploadResults] = useState([]);

  const fetchDocuments = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/api/documents');
      if (!response.ok) {
        throw new Error('获取文档列表失败');
      }
      const data = await response.json();
      setDocuments(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 文件上传相关处理函数
  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    const allowedTypes = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const allowedExtensions = ['.txt', '.pdf', '.docx'];
    
    const validFiles = files.filter(file => {
      const hasValidType = allowedTypes.includes(file.type);
      const hasValidExtension = allowedExtensions.some(ext => 
        file.name.toLowerCase().endsWith(ext)
      );
      return hasValidType || hasValidExtension;
    });
    
    if (validFiles.length > 0) {
      setSelectedFiles(validFiles);
      setUploadStatus('');
      if (validFiles.length < files.length) {
        setUploadStatus(`已选择 ${validFiles.length} 个有效文件，${files.length - validFiles.length} 个文件格式不支持`);
      }
    } else {
      setSelectedFiles([]);
      setUploadStatus('请选择.txt, .pdf或.docx格式的文件');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    const allowedTypes = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const allowedExtensions = ['.txt', '.pdf', '.docx'];
    
    const validFiles = files.filter(file => {
      const hasValidType = allowedTypes.includes(file.type);
      const hasValidExtension = allowedExtensions.some(ext => 
        file.name.toLowerCase().endsWith(ext)
      );
      return hasValidType || hasValidExtension;
    });
    
    if (validFiles.length > 0) {
      setSelectedFiles(validFiles);
      setUploadStatus('');
    } else {
      setSelectedFiles([]);
      setUploadStatus('请选择.txt, .pdf或.docx格式的文件');
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    setUploadStatus('');
    setUploadResults([]);

    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/api/upload/batch', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadResults(result.results);
        if (result.success_count > 0) {
          setUploadStatus(`批量上传完成：成功 ${result.success_count} 个，失败 ${result.failed_count} 个`);
          fetchDocuments(); // 重新获取文档列表
        } else {
          setUploadStatus('所有文件上传失败');
        }
        // 清空已选择的文件
        setTimeout(() => {
          setSelectedFiles([]);
          setUploadResults([]);
          document.getElementById('file-input').value = '';
        }, 3000);
      } else {
        setUploadStatus('上传失败: ' + (result.detail || '未知错误'));
      }
    } catch (err) {
      setUploadStatus('上传失败: ' + err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const deleteDocument = async (documentId) => {
    if (!window.confirm(`确定要删除文档 "${documentId}" 吗？`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/documents/${documentId}`, {
        method: 'DELETE',
      });
      const result = await response.json();
      if (result.success) {
        alert('删除成功');
        fetchDocuments(); // 重新获取列表
      } else {
        alert('删除失败: ' + result.message);
      }
    } catch (err) {
      alert('删除失败: ' + err.message);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <div className="knowledge-base-manager">
      <div className="manager-header">
        <h2>知识库管理</h2>
        <button onClick={fetchDocuments} className="refresh-button" disabled={loading}>
          <FaSync className={`refresh-icon ${loading ? 'spinning' : ''}`} />
          刷新
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* 文件上传区域 */}
      <div className="upload-section">
        <h3>上传新文档</h3>
        <div className="upload-container">
          <div 
            className={`drop-zone ${isDragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="file-input"
              onChange={handleFileSelect}
              accept=".txt,.pdf,.docx"
              multiple
              style={{ display: 'none' }}
            />

            {selectedFiles.length === 0 ? (
              <div className="drop-zone-content">
                <FaFileAlt className="file-icon" />
                <div className="drop-zone-text">
                  <p className="primary-text">拖拽文件到此处或 <label htmlFor="file-input" className="file-link">点击选择</label></p>
                  <p className="secondary-text">支持 .txt, .pdf, .docx 格式文件，可多选</p>
                </div>
              </div>
            ) : (
              <div className="files-list">
                {selectedFiles.map((file, index) => (
                  <div key={index} className="file-info">
                    <FaFileAlt className="file-icon selected" />
                    <div className="file-details">
                      <p className="file-name"><strong>{file.name}</strong></p>
                      <p className="file-size">{(file.size / 1024).toFixed(2)} KB</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={handleUpload}
            disabled={selectedFiles.length === 0 || isUploading}
            className="upload-button"
          >
            {isUploading ? (
              <>
                <div className="spinner"></div>
                上传中...
              </>
            ) : (
              <>
                <FaCloudUploadAlt className="button-icon" />
                上传 {selectedFiles.length > 0 ? `${selectedFiles.length} 个文件` : '到知识库'}
              </>
            )}
          </button>

          {uploadStatus && (
            <div className={`status-message ${uploadStatus.includes('成功') || uploadStatus.includes('完成') ? 'success' : 'error'}`}>
              {uploadStatus.includes('成功') || uploadStatus.includes('完成') ? (
                <FaCheckCircle className="status-icon" />
              ) : (
                <FaExclamationTriangle className="status-icon" />
              )}
              <span>{uploadStatus}</span>
            </div>
          )}

          {uploadResults.length > 0 && (
            <div className="upload-results">
              <h4>上传结果详情：</h4>
              {uploadResults.map((result, index) => (
                <div key={index} className={`upload-result-item ${result.success ? 'success' : 'error'}`}>
                  <span className="result-file-name">{result.file_name}</span>
                  <span className="result-message">{result.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 文档列表区域 */}
      <div className="documents-section">
        <h3>知识库文档 ({documents.length})</h3>
        <div className="documents-list">
          {documents.length === 0 && !loading ? (
            <div className="empty-state">
              <FaFileAlt className="empty-icon" />
              <p>知识库中暂无文档</p>
              <p className="empty-hint">请先上传文档文件</p>
            </div>
          ) : (
            documents.map((doc) => (
              <div key={doc.id} className="document-item">
                <div className="document-info">
                  <FaFileAlt className="document-icon" />
                  <div className="document-details">
                    <h3 className="document-source">{doc.source}</h3>
                    <p className="document-meta">
                      创建时间: {doc.create_time}
                    </p>
                    <p className="document-preview">{doc.content_preview}</p>
                  </div>
                </div>
                <button
                  onClick={() => deleteDocument(doc.id)}
                  className="delete-button"
                  title="删除文档"
                >
                  <FaTrash />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBaseManager;