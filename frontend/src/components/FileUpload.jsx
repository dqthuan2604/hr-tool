import { useState, useRef, useEffect } from 'react';
import { UploadSimple, FileDoc, FilePdf, CheckCircle } from '@phosphor-icons/react';
import { uploadTemplate } from '../api/templates';
import { uploadCandidate } from '../api/candidates';
import { useToast } from './Toast';

export default function FileUpload({ onUploadSuccess, isCandidate = false }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState({ status: '', message: '' });
  const [done, setDone] = useState(false);
  const fileInputRef = useRef(null);
  const eventSourceRef = useRef(null);
  const toast = useToast();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files?.[0]) await processFile(e.dataTransfer.files[0]);
  };

  const handleChange = async (e) => {
    e.preventDefault();
    if (e.target.files?.[0]) await processFile(e.target.files[0]);
  };

  const processFile = async (file) => {
    const ext = file.name.split('.').pop().toLowerCase();
    if (ext !== 'pdf') {
      toast.error('Chỉ hỗ trợ file .PDF');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File quá lớn. Tối đa 10MB.');
      return;
    }

    setDone(false);
    setIsUploading(true);
    setProgress({ status: 'uploading', message: 'Đang tải lên...' });

    try {
      if (isCandidate) {
        setProgress({ status: 'processing', message: 'Đang trích xuất dữ liệu CV...' });
        const candidate = await uploadCandidate(file);
        setIsUploading(false);
        setDone(true);
        toast.success('Tải lên thành công! Dữ liệu ứng viên đã được trích xuất.');
        if (onUploadSuccess) onUploadSuccess(candidate);
        setTimeout(() => setDone(false), 3000);
      } else {
        const { job_id } = await uploadTemplate(file);
        startListeningToProgress(job_id);
      }
    } catch (err) {
      toast.error('Lỗi khi tải file. Kiểm tra kết nối backend.');
      setIsUploading(false);
    }
  };

  const startListeningToProgress = (jobId) => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    const es = new EventSource(`${API_URL}/templates/upload/${jobId}/stream`);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setProgress({ status: data.status, message: data.message });

        if (data.status === 'done') {
          es.close();
          setIsUploading(false);
          setDone(true);
          toast.success('Template đã được phân tích thành công!');
          if (onUploadSuccess) onUploadSuccess(data.payload);
          setTimeout(() => setDone(false), 3000);
        } else if (data.status === 'error') {
          es.close();
          toast.error(data.message || 'Lỗi khi xử lý template.');
          setIsUploading(false);
        }
      } catch (err) {
        console.error('SSE parse error', err);
      }
    };

    es.onerror = () => {
      es.close();
      toast.error('Mất kết nối với server trong khi xử lý.');
      setIsUploading(false);
    };
  };

  useEffect(() => {
    return () => eventSourceRef.current?.close();
  }, []);

  return (
    <div className="w-full max-w-2xl mx-auto relative">
      {/* Upload zone */}
      <div
        className="relative rounded-xl p-10 text-center cursor-pointer transition-all duration-300"
        style={{
          background: isDragging ? 'rgba(99,102,241,0.06)' : 'var(--bg-surface)',
          border: `2px dashed ${isDragging ? 'var(--accent)' : 'var(--border)'}`,
          boxShadow: isDragging ? 'var(--shadow-glow)' : 'none',
          animation: isDragging ? 'glowPulse 1.8s ease-in-out infinite' : 'none',
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf"
          onChange={handleChange}
        />

        {done ? (
          <div className="flex flex-col items-center gap-3">
            <CheckCircle size={48} weight="fill" style={{ color: '#4ade80' }} />
            <p className="text-sm font-medium" style={{ color: '#4ade80' }}>Tải lên thành công!</p>
          </div>
        ) : (
          <>
            <div
              className="w-14 h-14 rounded-xl flex items-center justify-center mx-auto mb-4 transition-all"
              style={{
                background: isDragging ? 'var(--accent-muted)' : 'var(--bg-elevated)',
                border: `1px solid ${isDragging ? 'var(--border-accent)' : 'var(--border)'}`,
              }}
            >
              <UploadSimple
                size={24}
                style={{ color: isDragging ? 'var(--accent-hover)' : 'var(--text-muted)' }}
              />
            </div>
            <p className="font-medium" style={{ color: 'var(--text-primary)', fontSize: '0.9rem' }}>
              Kéo thả file vào đây,{' '}
              <span style={{ color: 'var(--accent-hover)', cursor: 'pointer' }}>
                hoặc chọn file
              </span>
            </p>
            <p className="mt-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
              Hỗ trợ PDF — Tối đa 10MB
            </p>

            <div className="flex items-center justify-center gap-3 mt-4">
              <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-disabled)' }}>
                <FilePdf size={13} />
                <span style={{ fontFamily: 'var(--font-mono)' }}>.pdf</span>
              </div>
            </div>
          </>
        )}

        {/* Processing overlay */}
        {isUploading && (
          <div
            className="absolute inset-0 rounded-xl flex flex-col items-center justify-center gap-3"
            style={{
              background: 'rgba(9,9,15,0.85)',
              backdropFilter: 'blur(8px)',
            }}
          >
            <div
              className="w-8 h-8 rounded-full border-2"
              style={{
                borderColor: 'var(--bg-elevated)',
                borderTopColor: 'var(--accent)',
                animation: 'spin 0.8s linear infinite',
              }}
            />
            <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
              {progress.message || 'Đang xử lý...'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
