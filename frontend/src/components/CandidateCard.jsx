import { User, Envelope, Briefcase, Trash, Eye } from '@phosphor-icons/react';

export default function CandidateCard({ candidate, onClick, onDelete }) {
  const currentVersion = candidate.versions?.find(v => v.is_current) || candidate.versions?.[0];
  const profile = currentVersion?.profile_json || {};
  const basicInfo = profile.basic_info || {};
  const workExp = profile.work_experiences || [];
  const skills = profile.skills || [];

  const displayName = basicInfo.full_name || candidate.source_file?.replace(/\.[^/.]+$/, '') || 'Ứng viên';
  const hasGoodExtract = basicInfo.full_name && basicInfo.email;

  return (
    <div
      className="glass-card flex flex-col h-full cursor-pointer"
      onClick={() => onClick(candidate.id)}
    >
      {/* Header */}
      <div className="p-4 pb-3">
        <div className="flex items-start justify-between gap-2 mb-3">
          {/* Avatar */}
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: 'var(--accent-muted)', border: '1px solid var(--border-accent)' }}
          >
            <User size={18} weight="duotone" style={{ color: 'var(--accent-hover)' }} />
          </div>

          {/* Status badge */}
          <span
            className="text-[10px] px-2 py-0.5 rounded-full font-medium flex items-center gap-1"
            style={hasGoodExtract
              ? { background: 'rgba(34,197,94,0.1)', color: '#4ade80', border: '1px solid rgba(34,197,94,0.2)' }
              : { background: 'rgba(234,179,8,0.1)', color: '#facc15', border: '1px solid rgba(234,179,8,0.2)' }
            }
          >
            <span
              className="w-1 h-1 rounded-full"
              style={{ background: hasGoodExtract ? '#4ade80' : '#facc15' }}
            />
            {hasGoodExtract ? 'Trích xuất OK' : 'Một phần'}
          </span>
        </div>

        {/* Name */}
        <h3
          className="text-sm font-semibold line-clamp-1 mb-1"
          style={{ color: 'var(--text-primary)' }}
        >
          {displayName}
        </h3>

        {/* File source */}
        <p
          className="text-[10px] truncate"
          style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
        >
          {candidate.source_file}
        </p>
      </div>

      {/* Details */}
      <div
        className="px-4 py-3 space-y-2 flex-1"
        style={{ borderTop: '1px solid var(--border-subtle)' }}
      >
        {basicInfo.email && (
          <div className="flex items-center gap-2">
            <Envelope size={12} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
            <span className="text-xs truncate" style={{ color: 'var(--text-secondary)' }}>
              {basicInfo.email}
            </span>
          </div>
        )}
        <div className="flex items-center gap-2">
          <Briefcase size={12} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            {workExp.length} kinh nghiệm
          </span>
        </div>
      </div>

      {/* Actions */}
      <div
        className="flex gap-2 p-3"
        style={{ borderTop: '1px solid var(--border-subtle)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-medium transition-all"
          style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)' }}
          onClick={() => onClick(candidate.id)}
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
          className="w-8 h-7 flex items-center justify-center rounded-lg text-xs transition-all"
          style={{ background: 'var(--bg-elevated)', color: 'var(--text-muted)' }}
          onClick={() => onDelete(candidate.id)}
          title="Xóa ứng viên"
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
  );
}
