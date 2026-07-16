import { Eye, Trash } from '@phosphor-icons/react';

export default function TemplateCard({ template, onDelete, onViewDetail }) {
  const schema = template.schema_json || {};
  const sections = schema.sections || [];
  const layout = schema.layout || {};
  const columns = layout.columns || [];

  return (
    <>
      <div className="glass-card flex flex-col h-full">

        {/* Header */}
        <div className="p-4 pb-3">
          <div className="flex items-start justify-between gap-2 mb-3">
            {/* File type badge */}
            <div
              className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-md font-mono"
              style={{ background: 'var(--accent-muted)', color: 'var(--accent-hover)' }}
            >
              PDF
            </div>
            {/* Sections count */}
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                sections.length > 0 ? 'badge-success' : 'badge-warning'
              }`}
            >
              {sections.length} sections
            </span>
          </div>

          <h3
            className="text-sm font-semibold line-clamp-2 leading-snug mb-1"
            style={{ color: 'var(--text-primary)' }}
          >
            {template.name}
          </h3>
          <p
            className="text-[10px] truncate"
            style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
          >
            {template.id.substring(0, 16)}...
          </p>
        </div>

        {/* Stats */}
        <div
          className="px-4 py-3 space-y-2 flex-1"
          style={{ borderTop: '1px solid var(--border-subtle)' }}
        >
          <div className="flex items-center justify-between text-xs">
            <span style={{ color: 'var(--text-muted)' }}>Layout</span>
            <span
              className="font-mono text-[11px] px-1.5 py-0.5 rounded"
              style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)' }}
            >
              {columns.join(' / ') || '—'}
            </span>
          </div>

          {/* Section preview */}
          <div className="flex flex-wrap gap-1 mt-2">
            {sections.slice(0, 2).map((s, idx) => (
              <span
                key={idx}
                className="text-[9px] px-1.5 py-0.5 rounded truncate max-w-[80px]"
                style={{ background: 'var(--accent-muted)', color: 'var(--accent-hover)' }}
              >
                {s.label || s.type}
              </span>
            ))}
            {sections.length > 2 && (
              <span
                className="text-[9px] px-1.5 py-0.5 rounded"
                style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}
              >
                +{sections.length - 2}
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div
          className="flex gap-2 p-3"
          style={{ borderTop: '1px solid var(--border-subtle)' }}
        >
          <button
            className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-medium transition-all"
            style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)' }}
            onClick={() => onViewDetail(template)}
            onMouseEnter={e => {
              e.currentTarget.style.background = 'var(--accent-muted)';
              e.currentTarget.style.color = 'var(--accent-hover)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = 'var(--bg-elevated)';
              e.currentTarget.style.color = 'var(--text-secondary)';
            }}
          >
            <Eye size={13} />
            Chi tiết
          </button>
          <button
            className="w-8 h-7 flex items-center justify-center rounded-lg transition-all"
            style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}
            onClick={() => onDelete(template.id)}
            title="Xóa template"
            onMouseEnter={e => {
              e.currentTarget.style.background = 'rgba(239,68,68,0.12)';
              e.currentTarget.style.color = '#f87171';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = 'var(--bg-elevated)';
              e.currentTarget.style.color = 'var(--text-muted)';
            }}
          >
            <Trash size={13} />
          </button>
        </div>
      </div>
    </>
  );
}
