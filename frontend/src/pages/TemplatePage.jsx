import { useState, useEffect } from 'react';
import FileUpload from '../components/FileUpload';
import TemplateCard from '../components/TemplateCard';
import TemplateDetailModal from '../components/TemplateDetailModal';
import { getTemplates, deleteTemplate } from '../api/templates';
import { useToast } from '../components/Toast';
import ConfirmModal from '../components/ConfirmModal';
import { FilePdf, Plus } from '@phosphor-icons/react';

export default function TemplatePage() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const toast = useToast();

  const fetchTemplates = async () => {
    try {
      const data = await getTemplates();
      setTemplates(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchTemplates(); }, []);

  const handleUploadSuccess = () => {
    fetchTemplates();
    setShowUpload(false);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Xóa mẫu CV này?')) return;
    try {
      await deleteTemplate(id);
      setTemplates(prev => prev.filter(t => t.id !== id));
      toast.success('Đã xóa template.');
    } catch {
      toast.error('Lỗi khi xóa template.');
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
              background: 'var(--accent-muted)',
              color: 'var(--accent-hover)',
              border: '1px solid var(--border-accent)',
            }}
          >
            <FilePdf size={10} weight="fill" />
            Templates
          </div>
          <h1
            className="text-2xl font-bold leading-tight"
            style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}
          >
            Mẫu CV
          </h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Tải lên mẫu CV để hệ thống phân tích cấu trúc layout tự động.
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
          {showUpload ? 'Đóng' : 'Tải lên mẫu mới'}
        </button>
      </div>

      {/* Upload zone */}
      {showUpload && (
        <div className="mb-8 animate-fade-up">
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        </div>
      )}

      {/* Grid */}
      <div>
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
            Đã tải lên
            <span
              className="ml-2 text-xs px-2 py-0.5 rounded-full"
              style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}
            >
              {templates.length}
            </span>
          </h2>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {[1,2,3].map(i => (
              <div key={i} className="skeleton h-48 rounded-xl" />
            ))}
          </div>
        ) : templates.length === 0 ? (
          <div
            className="flex flex-col items-center justify-center py-20 rounded-xl"
            style={{ background: 'var(--bg-surface)', border: '1px dashed var(--border)' }}
          >
            <div
              className="w-14 h-14 rounded-xl flex items-center justify-center mb-4"
              style={{ background: 'var(--bg-elevated)' }}
            >
              <FilePdf size={24} style={{ color: 'var(--text-disabled)' }} />
            </div>
            <p className="text-sm font-medium" style={{ color: 'var(--text-muted)' }}>
              Chưa có mẫu CV nào.
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-disabled)' }}>
              Nhấn "Tải lên mẫu mới" để bắt đầu.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {templates.map((tpl, idx) => (
              <div key={tpl.id} className="animate-fade-up" style={{ animationDelay: `${idx * 40}ms` }}>
                <TemplateCard template={tpl} onDelete={handleDelete} onViewDetail={() => setSelectedTemplate(tpl)} />
              </div>
            ))}
          </div>
        )}
      </div>

      {confirmDelete && (
        <ConfirmModal 
          title="Xóa mẫu CV" 
          message="Bạn có chắc chắn muốn xóa mẫu CV này? Hành động này không thể hoàn tác."
          onConfirm={executeDelete}
          onCancel={() => setConfirmDelete(null)}
          confirmText="Xóa mẫu CV"
        />
      )}

      {selectedTemplate && (
        <TemplateDetailModal
          template={selectedTemplate}
          onClose={() => setSelectedTemplate(null)}
        />
      )}
    </div>
  );
}
