import { useState, useEffect } from 'react';
import FileUpload from '../components/FileUpload';
import CandidateCard from '../components/CandidateCard';
import CandidateDetailModal from '../components/CandidateDetailModal';
import { getCandidates, deleteCandidate } from '../api/candidates';
import { useToast } from '../components/Toast';
import ConfirmModal from '../components/ConfirmModal';
import { Users, Plus } from '@phosphor-icons/react';

export default function CandidatePage() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const toast = useToast();

  const fetchCandidates = async () => {
    try {
      const data = await getCandidates();
      setCandidates(data);
    } catch {
      toast.error('Không thể tải danh sách ứng viên.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCandidates(); }, []);

  const handleUploadSuccess = () => {
    fetchCandidates();
    setShowUpload(false);
  };

  const handleDelete = async (id) => {
    setConfirmDelete(id);
  };
  
  const executeDelete = async () => {
    if (!confirmDelete) return;
    try {
      await deleteCandidate(confirmDelete);
      setCandidates(prev => prev.filter(c => c.id !== confirmDelete));
      toast.success('Đã xóa ứng viên.');
    } catch {
      toast.error('Lỗi khi xóa ứng viên.');
    } finally {
      setConfirmDelete(null);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">

      {/* Page header */}
      <div className="flex items-start justify-between mb-8 animate-fade-up">
        <div>
          <div
            className="inline-flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest px-2.5 py-1 rounded-full mb-3"
            style={{
              background: 'rgba(99,102,241,0.1)',
              color: 'var(--accent-hover)',
              border: '1px solid var(--border-accent)',
            }}
          >
            <Users size={10} weight="fill" />
            Candidates
          </div>
          <h1
            className="text-2xl font-bold leading-tight"
            style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}
          >
            Ứng viên
          </h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Tải lên CV ứng viên để hệ thống tự động bóc tách và lưu trữ thông tin.
          </p>
        </div>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all"
          style={{
            background: showUpload ? 'var(--bg-elevated)' : 'var(--accent)',
            color: showUpload ? 'var(--text-secondary)' : '#fff',
            border: `1px solid ${showUpload ? 'var(--border)' : 'transparent'}`,
          }}
        >
          <Plus size={16} weight="bold" />
          {showUpload ? 'Đóng' : 'Tải lên CV'}
        </button>
      </div>

      {/* Upload zone */}
      {showUpload && (
        <div className="mb-8 animate-fade-up">
          <FileUpload onUploadSuccess={handleUploadSuccess} isCandidate={true} />
        </div>
      )}

      {/* Grid */}
      <div>
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
            Hồ sơ đã lưu
            <span
              className="ml-2 text-xs px-2 py-0.5 rounded-full"
              style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}
            >
              {candidates.length}
            </span>
          </h2>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {[1,2,3,4].map(i => (
              <div key={i} className="skeleton h-44 rounded-xl" />
            ))}
          </div>
        ) : candidates.length === 0 ? (
          <div
            className="flex flex-col items-center justify-center py-20 rounded-xl"
            style={{ background: 'var(--bg-surface)', border: '1px dashed var(--border)' }}
          >
            <div
              className="w-14 h-14 rounded-xl flex items-center justify-center mb-4"
              style={{ background: 'var(--bg-elevated)' }}
            >
              <Users size={24} style={{ color: 'var(--text-disabled)' }} />
            </div>
            <p className="text-sm font-medium" style={{ color: 'var(--text-muted)' }}>
              Chưa có hồ sơ ứng viên nào.
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-disabled)' }}>
              Nhấn "Tải lên CV" để bắt đầu.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {candidates.map((candidate, idx) => (
              <div key={candidate.id} className="animate-fade-up" style={{ animationDelay: `${idx * 40}ms` }}>
                <CandidateCard
                  candidate={candidate}
                  onClick={(id) => setSelectedCandidate(candidates.find(c => c.id === id))}
                  onDelete={handleDelete}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {confirmDelete && (
        <ConfirmModal 
          title="Xóa ứng viên" 
          message="Bạn có chắc chắn muốn xóa hồ sơ ứng viên này? Hành động này không thể hoàn tác."
          onConfirm={executeDelete}
          onCancel={() => setConfirmDelete(null)}
          confirmText="Xóa ứng viên"
        />
      )}

      {selectedCandidate && (
        <CandidateDetailModal
          candidate={selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
          onUpdate={fetchCandidates}
        />
      )}
    </div>
  );
}
