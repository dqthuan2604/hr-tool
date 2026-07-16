import { useEffect, useRef, useState } from 'react';
import { X } from '@phosphor-icons/react';

export default function TemplateDetailModal({ template, onClose }) {
  const [jsonExpanded, setJsonExpanded] = useState(false);
  const overlayRef = useRef(null);

  const schema = template?.schema_json || {};
  const sections = schema.sections || [];
  const layout = schema.layout || {};
  const columns = layout.columns || [];
  const colors = schema.colors || {};

  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  const handleOverlayClick = (e) => {
    if (e.target === overlayRef.current) onClose();
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('vi-VN', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  };

  return (
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in"
      style={{ background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)' }}
    >
      <div
        className="w-full max-w-5xl max-h-[85vh] flex flex-col overflow-hidden rounded-2xl animate-fade-up"
        style={{
          background: 'var(--bg-overlay)',
          border: '1px solid var(--border)',
          boxShadow: 'var(--shadow-modal)',
        }}
      >
        {/* Header */}
        <div
          className="flex items-start justify-between p-5"
          style={{ borderBottom: '1px solid var(--border-subtle)' }}
        >
          <div>
            <h2
              className="text-base font-bold leading-tight"
              style={{ color: 'var(--text-primary)', letterSpacing: '-0.01em' }}
            >
              {template.name}
            </h2>
            <p
              className="text-[11px] mt-1"
              style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
            >
              {template.id}
            </p>
            <p className="text-xs mt-0.5" style={{ color: 'var(--text-disabled)' }}>
              Tải lên: {formatDate(template.created_at)}
            </p>
          </div>
          <button
            onClick={onClose}
            className="ml-4 rounded-lg p-1.5 transition-all"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={e => {
              e.currentTarget.style.background = 'var(--bg-raised)';
              e.currentTarget.style.color = 'var(--text-primary)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = 'var(--text-muted)';
            }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div className="flex flex-1 overflow-hidden">

          {/* Left — Layout & Stats */}
          <div
            className="w-52 flex-shrink-0 overflow-y-auto p-5 space-y-5"
            style={{ borderRight: '1px solid var(--border-subtle)' }}
          >
            <div>
              <p
                className="text-[10px] font-semibold uppercase tracking-widest mb-2"
                style={{ color: 'var(--text-muted)' }}
              >
                Layout
              </p>
              <div className="space-y-1">
                {columns.length > 0 ? columns.map((col, i) => (
                  <div
                    key={i}
                    className="text-xs px-2 py-1 rounded font-mono"
                    style={{ background: 'var(--accent-muted)', color: 'var(--accent-hover)' }}
                  >
                    Col {i + 1}: {col}
                  </div>
                )) : (
                  <span className="text-xs" style={{ color: 'var(--text-disabled)' }}>Không có dữ liệu</span>
                )}
              </div>
            </div>

            <div>
              <p
                className="text-[10px] font-semibold uppercase tracking-widest mb-2"
                style={{ color: 'var(--text-muted)' }}
              >
                Màu sắc
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(colors).map(([key, hex]) => hex && (
                  <div key={key} className="flex items-center gap-2 w-full">
                    <span
                      className="w-4 h-4 rounded-full shadow-sm flex-shrink-0"
                      style={{ background: hex, border: '1px solid var(--border-subtle)' }}
                    />
                    <span className="text-[10px] font-mono text-gray-400 capitalize">{key}</span>
                  </div>
                ))}
                {Object.keys(colors).length === 0 && (
                  <span className="text-xs" style={{ color: 'var(--text-disabled)' }}>Không có dữ liệu</span>
                )}
              </div>
            </div>

            <div>
              <p
                className="text-[10px] font-semibold uppercase tracking-widest mb-2"
                style={{ color: 'var(--text-muted)' }}
              >
                Thống kê
              </p>
              <div className="space-y-2">
                {[
                  { label: 'Sections', value: sections.length },
                  { label: 'Columns', value: columns.length || '—' },
                ].map(({ label, value }) => (
                  <div key={label} className="flex justify-between items-center">
                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{label}</span>
                    <span
                      className="text-sm font-bold"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      {value}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <p
                className="text-[10px] font-semibold uppercase tracking-widest mb-2"
                style={{ color: 'var(--text-muted)' }}
              >
                Trạng thái
              </p>
              <span
                className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-medium"
                style={sections.length > 0
                  ? { background: 'rgba(34,197,94,0.1)', color: '#4ade80', border: '1px solid rgba(34,197,94,0.2)' }
                  : { background: 'rgba(234,179,8,0.1)', color: '#facc15', border: '1px solid rgba(234,179,8,0.2)' }
                }
              >
                <span
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ background: sections.length > 0 ? '#4ade80' : '#facc15' }}
                />
                {sections.length > 0 ? 'Đã phân tích' : 'Đang xử lý'}
              </span>
            </div>
          </div>

          {/* Right — Sections list */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div
              className="p-4"
              style={{ borderBottom: '1px solid var(--border-subtle)' }}
            >
              <p
                className="text-[10px] font-semibold uppercase tracking-widest"
                style={{ color: 'var(--text-muted)' }}
              >
                Sections bóc tách ({sections.length})
              </p>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-1">
              {sections.length === 0 ? (
                <div className="flex items-center justify-center h-24">
                  <p className="text-sm" style={{ color: 'var(--text-disabled)' }}>
                    Chưa có sections nào được phân tích.
                  </p>
                </div>
              ) : sections.map((section, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 py-1.5 px-2 rounded-lg transition-colors"
                  style={{ ':hover': { background: 'var(--bg-raised)' } }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-raised)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <span
                    className="text-[10px] font-mono w-6 text-right flex-shrink-0 mt-0.5"
                    style={{ color: 'var(--text-disabled)' }}
                  >
                    {idx + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-sm font-medium truncate"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      {section.label || section.type || `Section ${idx + 1}`}
                    </p>
                    {section.type && section.type !== section.label && (
                      <p
                        className="text-[10px] font-mono mt-0.5"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        {section.type}
                      </p>
                    )}
                    <div 
                      className="mt-2 rounded-md p-3 space-y-2 transition-all"
                      style={{ 
                        border: `1px dashed ${colors.primary || 'var(--border-subtle)'}`,
                        background: 'var(--bg-base)',
                      }}
                    >
                      <div className="text-[11px] font-bold uppercase" style={{ color: colors.primary || 'var(--text-primary)' }}>
                        [Placeholder] {section.label || section.type}
                      </div>
                      <p className="text-[10px]" style={{ color: colors.text_primary || 'var(--text-secondary)', lineHeight: '1.5' }}>
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                      </p>
                      <ul className="text-[10px] pl-3 list-disc space-y-1" style={{ color: colors.text_secondary || 'var(--text-muted)', lineHeight: '1.4' }}>
                        <li>Ut enim ad minim veniam, quis nostrud exercitation ullamco</li>
                        <li>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum</li>
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Rightmost — Template Preview */}
          <div className="w-80 flex-shrink-0 flex flex-col overflow-hidden" style={{ borderLeft: '1px solid var(--border-subtle)', background: 'var(--bg-base)' }}>
            <div className="p-4" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <p className="text-[10px] font-semibold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>
                Template Preview
              </p>
            </div>
            <div className="flex-1 overflow-y-auto p-6 bg-neutral-900/50 flex items-start justify-center">
              <div 
                className="w-full bg-white shadow-xl relative flex flex-col"
                style={{ aspectRatio: '210/297', color: '#111' }}
              >
                {/* Dummy Header */}
                <div className="w-full p-4 flex gap-3 items-center" style={{ background: colors.primary || '#1e293b', color: 'white' }}>
                  <div className="w-10 h-10 rounded-full flex-shrink-0" style={{ background: 'rgba(255,255,255,0.2)' }}></div>
                  <div>
                    <div className="text-[12px] font-bold uppercase tracking-widest mb-1">NGUYEN VAN A</div>
                    <div className="text-[7px] opacity-80 font-mono tracking-wider">SENIOR SOFTWARE ENGINEER</div>
                  </div>
                </div>
                
                {/* Columns */}
                <div className="flex-1 flex flex-row overflow-hidden">
                  {/* Left Column (if exists) */}
                  {(columns.includes('left') || columns.length === 2) && (
                    <div className="w-1/3 h-full p-3 space-y-3 flex flex-col" style={{ background: colors.primary ? colors.primary + '10' : '#f8fafc' }}>
                      {sections.filter(s => s.column === 'left' || (columns.length === 2 && !s.column)).map((s, i) => (
                        <div key={i}>
                          <div className="text-[7px] font-bold uppercase mb-1.5" style={{ color: colors.primary || '#3b82f6', letterSpacing: '0.05em' }}>
                            {s.label || s.type}
                          </div>
                          <div className="space-y-1">
                            <div className="h-1 w-full rounded" style={{ background: colors.primary ? colors.primary + '30' : '#cbd5e1' }}></div>
                            <div className="h-1 w-5/6 rounded" style={{ background: colors.primary ? colors.primary + '30' : '#cbd5e1' }}></div>
                            <div className="h-1 w-4/6 rounded" style={{ background: colors.primary ? colors.primary + '30' : '#cbd5e1' }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  {/* Right Column / Single Column */}
                  <div className="flex-1 h-full p-4 space-y-4 flex flex-col overflow-hidden">
                    {sections.filter(s => s.column === 'right' || s.column === 'single' || columns.length < 2).map((s, i) => (
                      <div key={i}>
                        <div className="flex items-center gap-1.5 mb-2">
                          <div className="w-1.5 h-1.5 rounded-full" style={{ background: colors.accent || colors.primary || '#3b82f6' }}></div>
                          <div className="text-[8px] font-bold uppercase tracking-wider" style={{ color: colors.text || '#1e293b' }}>
                            {s.label || s.type}
                          </div>
                        </div>
                        {/* Dummy items */}
                        <div className="space-y-2">
                          <div className="flex justify-between items-start">
                            <div className="text-[6px] font-semibold" style={{ color: '#334155' }}>Senior Developer at ABC Corp</div>
                            <div className="text-[5px] text-gray-400">2021 - Present</div>
                          </div>
                          <div className="space-y-0.5">
                            <div className="h-0.5 w-full bg-gray-200 rounded"></div>
                            <div className="h-0.5 w-11/12 bg-gray-200 rounded"></div>
                            <div className="h-0.5 w-4/5 bg-gray-200 rounded"></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer — Collapsible JSON */}
        <div style={{ borderTop: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => setJsonExpanded(!jsonExpanded)}
            className="w-full flex items-center justify-between px-5 py-3 text-xs transition-colors"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={e => {
              e.currentTarget.style.background = 'var(--bg-raised)';
              e.currentTarget.style.color = 'var(--text-secondary)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = 'var(--text-muted)';
            }}
          >
            <span style={{ fontFamily: 'var(--font-mono)' }}>Raw Schema JSON</span>
            <svg
              className={`w-3.5 h-3.5 transition-transform ${jsonExpanded ? 'rotate-180' : ''}`}
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {jsonExpanded && (
            <div className="px-5 pb-4">
              <pre
                className="text-[11px] overflow-auto max-h-40 p-3 rounded-lg leading-relaxed"
                style={{
                  background: 'var(--bg-base)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-secondary)',
                  fontFamily: 'var(--font-mono)',
                }}
              >
                {JSON.stringify(schema, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
