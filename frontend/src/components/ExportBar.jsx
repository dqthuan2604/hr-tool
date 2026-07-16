import { useState } from 'react';
import { exportPDF, exportDOCX, downloadBlob } from '../api/generator';

export default function ExportBar({ draftId, disabled = false }) {
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportingDocx, setExportingDocx] = useState(false);
  const [error, setError] = useState('');

  const handleExportPDF = async () => {
    if (!draftId) return;
    setExportingPdf(true);
    setError('');
    try {
      const blob = await exportPDF(draftId);
      downloadBlob(blob, 'cv_export.pdf');
    } catch (err) {
      setError('Lỗi xuất PDF. Vui lòng thử lại.');
    } finally {
      setExportingPdf(false);
    }
  };

  const handleExportDOCX = async () => {
    if (!draftId) return;
    setExportingDocx(true);
    setError('');
    try {
      const blob = await exportDOCX(draftId);
      downloadBlob(blob, 'cv_export.docx');
    } catch (err) {
      setError('Lỗi xuất DOCX. Vui lòng thử lại.');
    } finally {
      setExportingDocx(false);
    }
  };

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Xuất file</h3>

      <button
        onClick={handleExportPDF}
        disabled={disabled || !draftId || exportingPdf}
        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors font-medium text-sm"
      >
        {exportingPdf ? (
          <>
            <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
            Đang tạo PDF...
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export PDF
          </>
        )}
      </button>

      <button
        onClick={handleExportDOCX}
        disabled={disabled || !draftId || exportingDocx}
        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors font-medium text-sm"
      >
        {exportingDocx ? (
          <>
            <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
            Đang tạo DOCX...
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export DOCX
          </>
        )}
      </button>

      {error && (
        <p className="text-xs text-red-600 bg-red-50 px-3 py-2 rounded border border-red-100">
          ⚠️ {error}
        </p>
      )}

      {!draftId && (
        <p className="text-xs text-gray-400 text-center">
          Generate CV trước để có thể xuất file
        </p>
      )}
    </div>
  );
}
