import { Warning } from '@phosphor-icons/react';

export default function ConfirmModal({ title, message, onConfirm, onCancel, confirmText = 'Xác nhận', cancelText = 'Hủy', variant = 'danger' }) {
  const isDanger = variant === 'danger';
  
  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 animate-fade-in"
      style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}
      onClick={onCancel}
    >
      <div
        className="w-full max-w-sm rounded-2xl shadow-2xl p-6 animate-fade-up flex flex-col items-center text-center relative overflow-hidden"
        style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
        onClick={e => e.stopPropagation()}
      >
        {/* Top accent line */}
        <div 
          className="absolute top-0 left-0 right-0 h-1"
          style={{ background: isDanger ? '#ef4444' : 'var(--accent)' }}
        />
        
        <div 
          className="w-12 h-12 rounded-full flex items-center justify-center mb-4"
          style={{ background: isDanger ? 'rgba(239, 68, 68, 0.1)' : 'var(--bg-elevated)', color: isDanger ? '#ef4444' : 'var(--accent)' }}
        >
          <Warning size={24} weight="duotone" />
        </div>
        
        <h3 className="text-lg font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
          {title}
        </h3>
        <p className="text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>
          {message}
        </p>
        
        <div className="flex items-center gap-3 w-full">
          <button
            onClick={onCancel}
            className="flex-1 py-2.5 rounded-xl text-sm font-semibold transition-colors"
            style={{ background: 'var(--bg-elevated)', color: 'var(--text-primary)' }}
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-md"
            style={{ 
              background: isDanger ? '#ef4444' : 'var(--accent)', 
              color: '#fff',
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
