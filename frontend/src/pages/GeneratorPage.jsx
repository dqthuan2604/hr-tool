import { useState, useEffect } from 'react';
import CVPreview from '../components/CVPreview';
import ExportBar from '../components/ExportBar';
import { renderCV } from '../api/generator';
import { getCandidates } from '../api/candidates';
import { getTemplates } from '../api/templates';
import { useToast } from '../components/Toast';
import { MagicWand, Lightning, ArrowsOut, ArrowsIn, User, FilePdf, PencilSimple, X } from '@phosphor-icons/react';

export default function GeneratorPage() {
  const [candidates, setCandidates] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [html, setHtml] = useState('');
  const [draftId, setDraftId] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewScale, setPreviewScale] = useState(0.7);
  const [customJsonText, setCustomJsonText] = useState('{}');
  const [showJsonEditor, setShowJsonEditor] = useState(false);
  const toast = useToast();

  useEffect(() => {
    Promise.all([getCandidates(), getTemplates()])
      .then(([cands, tmplts]) => {
        setCandidates(cands);
        setTemplates(tmplts);
      })
      .catch(() => toast.error('Không thể tải danh sách ứng viên/template.'));
  }, []);

  const handleGenerate = async () => {
    if (!selectedCandidate || !selectedTemplate) {
      toast.error('Vui lòng chọn ứng viên và mẫu CV');
      return;
    }
    setIsGenerating(true);
    try {
      let customJson = null;
      try {
        if (customJsonText && customJsonText.trim() !== '{}') {
          customJson = JSON.parse(customJsonText);
        }
      } catch (e) {
        toast.error('JSON không hợp lệ');
        setIsGenerating(false);
        return;
      }
      const result = await renderCV(selectedCandidate, selectedTemplate, customJson);
      setHtml(result.html);
      setDraftId(result.draft_id);
      toast.success('CV đã được tạo thành công!');
    } catch (err) {
      toast.error(err.message || 'Lỗi khi tạo CV');
    } finally {
      setIsGenerating(false);
    }
  };

  const getCandidateName = (c) => {
    const v = c.versions?.find(v => v.is_current) || c.versions?.[0];
    return v?.profile_json?.basic_info?.full_name || c.source_file || c.id;
  };

  const canGenerate = selectedCandidate && selectedTemplate && !isGenerating;

  return (
    <div
      className="flex overflow-hidden"
      style={{ height: '100vh', background: 'var(--bg-base)' }}
    >
      {/* ─── Controls Panel ─── */}
      <div
        className="w-[280px] flex-shrink-0 flex flex-col overflow-hidden"
        style={{
          background: 'var(--bg-surface)',
          borderRight: '1px solid var(--border)',
        }}
      >
        {/* Panel header */}
        <div className="px-5 pt-6 pb-4" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
          <div
            className="inline-flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest px-2.5 py-1 rounded-full mb-3"
            style={{
              background: 'var(--accent-muted)',
              color: 'var(--accent-hover)',
              border: '1px solid var(--border-accent)',
            }}
          >
            <MagicWand size={10} weight="fill" />
            Generator
          </div>
          <h2
            className="text-base font-bold"
            style={{ color: 'var(--text-primary)', letterSpacing: '-0.01em' }}
          >
            Tạo CV
          </h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Chọn ứng viên và mẫu CV
          </p>
        </div>

        {/* Form controls */}
        <div className="flex-1 overflow-y-auto px-5 py-5 space-y-5">
          {/* Candidate */}
          <div>
            <label
              className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest mb-2"
              style={{ color: 'var(--text-muted)' }}
            >
              <User size={10} />
              Ứng viên
            </label>
            <select
              id="select-candidate"
              value={selectedCandidate}
              onChange={e => setSelectedCandidate(e.target.value)}
              className="dark-input"
            >
              <option value="">-- Chọn ứng viên --</option>
              {candidates.map(c => (
                <option key={c.id} value={c.id}>{getCandidateName(c)}</option>
              ))}
            </select>
            {candidates.length === 0 && (
              <p className="text-[10px] mt-1.5" style={{ color: 'var(--text-disabled)' }}>
                Chưa có ứng viên. Hãy tải lên trước.
              </p>
            )}
          </div>

          {/* Template */}
          <div>
            <label
              className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest mb-2"
              style={{ color: 'var(--text-muted)' }}
            >
              <FilePdf size={10} />
              Mẫu CV
            </label>
            <select
              id="select-template"
              value={selectedTemplate}
              onChange={e => setSelectedTemplate(e.target.value)}
              className="dark-input"
            >
              <option value="">-- Chọn mẫu CV --</option>
              {templates.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
            {templates.length === 0 && (
              <p className="text-[10px] mt-1.5" style={{ color: 'var(--text-disabled)' }}>
                Chưa có template. Hãy tải lên trước.
              </p>
            )}
          </div>

          {/* Generate button */}
          <button
            onClick={() => setShowJsonEditor(true)}
            disabled={!canGenerate}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all mb-2"
            style={{
              background: 'transparent',
              color: canGenerate ? 'var(--text-primary)' : 'var(--text-disabled)',
              border: `1px dashed ${canGenerate ? 'var(--border)' : 'var(--border-subtle)'}`,
              cursor: canGenerate ? 'pointer' : 'not-allowed',
            }}
          >
            <PencilSimple size={14} />
            Tùy chỉnh Dữ liệu (Nâng cao)
          </button>
          <button
            id="btn-generate"
            onClick={handleGenerate}
            disabled={!canGenerate}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all"
            style={{
              background: canGenerate ? 'var(--accent)' : 'var(--bg-elevated)',
              color: canGenerate ? '#fff' : 'var(--text-disabled)',
              border: `1px solid ${canGenerate ? 'transparent' : 'var(--border)'}`,
              cursor: canGenerate ? 'pointer' : 'not-allowed',
              transition: 'all 0.2s cubic-bezier(0.32, 0.72, 0, 1)',
            }}
          >
            {isGenerating ? (
              <>
                <span
                  className="w-4 h-4 rounded-full border-2 flex-shrink-0"
                  style={{
                    borderColor: 'rgba(255,255,255,0.3)',
                    borderTopColor: '#fff',
                    animation: 'spin 0.8s linear infinite',
                  }}
                />
                Đang tạo...
              </>
            ) : (
              <>
                <Lightning size={15} weight="fill" />
                Generate CV
              </>
            )}
          </button>

          {/* Export */}
          {draftId && (
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem' }}>
              <ExportBar draftId={draftId} disabled={isGenerating} />
            </div>
          )}

          {/* Zoom slider */}
          {html && (
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem' }}>
              <div className="flex items-center justify-between mb-2">
                <label
                  className="text-[10px] font-semibold uppercase tracking-widest"
                  style={{ color: 'var(--text-muted)' }}
                >
                  Zoom
                </label>
                <span
                  className="text-[11px] font-mono"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  {Math.round(previewScale * 100)}%
                </span>
              </div>
              <input
                type="range" min="40" max="100"
                value={Math.round(previewScale * 100)}
                onChange={e => setPreviewScale(Number(e.target.value) / 100)}
                className="w-full"
                style={{ accentColor: 'var(--accent)' }}
              />
            </div>
          )}
        </div>
      </div>

      {/* ─── Preview Area ─── */}
      <div
        className="flex-1 overflow-auto flex items-start justify-center p-8"
        style={{ background: 'var(--bg-base)' }}
      >
        {isGenerating ? (
          <div className="flex flex-col items-center justify-center h-full gap-4" style={{ color: 'var(--text-muted)' }}>
            <div
              className="w-12 h-12 rounded-full border-2"
              style={{
                borderColor: 'var(--bg-elevated)',
                borderTopColor: 'var(--accent)',
                animation: 'spin 0.8s linear infinite',
              }}
            />
            <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Đang render CV...</p>
          </div>
        ) : html ? (
          <CVPreview html={html} scale={previewScale} />
        ) : (
          /* Empty state */
          <div className="flex flex-col items-center justify-center h-full gap-6 max-w-sm text-center">
            <div
              className="w-20 h-20 rounded-2xl flex items-center justify-center"
              style={{
                background: 'var(--bg-surface)',
                border: '1px solid var(--border)',
                boxShadow: 'var(--shadow-card)',
              }}
            >
              <MagicWand size={36} style={{ color: 'var(--text-disabled)' }} />
            </div>
            <div>
              <h3 className="font-semibold mb-1" style={{ color: 'var(--text-secondary)' }}>
                Preview CV sẽ hiển thị ở đây
              </h3>
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                Chọn ứng viên và mẫu CV từ panel bên trái, sau đó nhấn Generate.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Custom JSON Modal */}
      {showJsonEditor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in" style={{ background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)' }}>
          <div className="w-full max-w-2xl flex flex-col overflow-hidden rounded-2xl shadow-2xl animate-fade-up" style={{ background: 'var(--bg-overlay)', border: '1px solid var(--border)' }}>
            <div className="flex justify-between items-center p-5" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <div>
                <h2 className="text-lg font-bold leading-tight" style={{ color: 'var(--text-primary)' }}>Tùy chỉnh Dữ liệu (JSON)</h2>
                <p className="text-[11px] mt-1" style={{ color: 'var(--text-muted)' }}>Dữ liệu này sẽ ghi đè lên dữ liệu trích xuất từ CV.</p>
              </div>
              <button onClick={() => setShowJsonEditor(false)} className="rounded-lg p-1.5 transition-all text-neutral-400 hover:bg-neutral-800 hover:text-white">
                <X size={16} />
              </button>
            </div>
            <div className="p-6">
              <textarea
                className="w-full bg-neutral-900 text-sm font-mono rounded-lg border border-neutral-700 focus:border-indigo-500 outline-none p-4 min-h-[300px]"
                value={customJsonText}
                onChange={e => setCustomJsonText(e.target.value)}
                placeholder='{
  "basic_info": {
    "full_name": "Tên mới"
  }
}'
                spellCheck={false}
              />
            </div>
            <div className="p-5 flex justify-end gap-3" style={{ borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-surface)' }}>
              <button onClick={() => setShowJsonEditor(false)} className="px-4 py-2 text-sm font-medium rounded-lg text-neutral-400 hover:text-white transition-colors">Đóng</button>
              <button onClick={() => setShowJsonEditor(false)} className="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white transition-colors">Xong</button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
