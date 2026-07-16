import { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';
import { CheckCircle, XCircle, Info, X } from '@phosphor-icons/react';

/* ═══════════════════════════════════════════════════
   Toast Context
═══════════════════════════════════════════════════ */
const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const counterRef = useRef(0);

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = ++counterRef.current;
    setToasts(prev => {
      const next = [...prev, { id, message, type }];
      return next.slice(-3); // max 3 toasts
    });
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, duration);
    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const toast = {
    success: (msg, duration) => addToast(msg, 'success', duration),
    error: (msg, duration) => addToast(msg, 'error', duration),
    info: (msg, duration) => addToast(msg, 'info', duration),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}

/* ═══════════════════════════════════════════════════
   Toast Container
═══════════════════════════════════════════════════ */
function ToastContainer({ toasts, onRemove }) {
  if (toasts.length === 0) return null;
  return (
    <div
      className="fixed bottom-6 right-6 z-[200] flex flex-col gap-2.5"
      style={{ maxWidth: '360px' }}
    >
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   Toast Item
═══════════════════════════════════════════════════ */
const toastConfig = {
  success: {
    icon: CheckCircle,
    bg:   'rgba(20, 28, 20, 0.95)',
    border: 'rgba(34, 197, 94, 0.3)',
    iconColor: '#4ade80',
    textColor: '#bbf7d0',
  },
  error: {
    icon: XCircle,
    bg:   'rgba(28, 14, 14, 0.95)',
    border: 'rgba(239, 68, 68, 0.3)',
    iconColor: '#f87171',
    textColor: '#fecaca',
  },
  info: {
    icon: Info,
    bg:   'rgba(14, 14, 28, 0.95)',
    border: 'rgba(99, 102, 241, 0.35)',
    iconColor: 'var(--accent-hover)',
    textColor: 'var(--text-primary)',
  },
};

function ToastItem({ toast, onRemove }) {
  const config = toastConfig[toast.type] || toastConfig.info;
  const Icon = config.icon;

  return (
    <div
      className="flex items-start gap-3 px-4 py-3 rounded-xl animate-slide-in-right"
      style={{
        background: config.bg,
        border: `1px solid ${config.border}`,
        backdropFilter: 'blur(12px)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
      }}
    >
      <Icon
        size={18}
        weight="fill"
        style={{ color: config.iconColor, flexShrink: 0, marginTop: 1 }}
      />
      <p
        className="text-sm flex-1 leading-snug"
        style={{ color: config.textColor, fontFamily: 'var(--font-sans)' }}
      >
        {toast.message}
      </p>
      <button
        onClick={() => onRemove(toast.id)}
        className="flex-shrink-0 transition-opacity hover:opacity-60"
        style={{ color: 'var(--text-muted)', marginTop: 1 }}
      >
        <X size={14} />
      </button>
    </div>
  );
}

/* Default export for App.jsx compatibility */
export default function Toast() {
  return null; // Container is managed by ToastProvider
}
