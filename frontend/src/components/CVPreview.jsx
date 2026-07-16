import { useRef, useEffect } from 'react';

/**
 * CVPreview — renders HTML string inside a sandboxed iframe.
 * Uses srcdoc for safe, isolated rendering.
 */
export default function CVPreview({ html, scale = 0.75 }) {
  const iframeRef = useRef(null);

  // Adjust iframe height to match content after load
  const handleLoad = () => {
    try {
      const iframe = iframeRef.current;
      if (iframe && iframe.contentDocument) {
        const height = iframe.contentDocument.documentElement.scrollHeight;
        iframe.style.height = `${height}px`;
      }
    } catch (_) {
      // Cross-origin guard — safe to ignore
    }
  };

  if (!html) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[500px] bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg text-gray-400">
        <svg className="w-16 h-16 mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="font-medium">Chọn ứng viên và mẫu CV, sau đó bấm <strong>Generate</strong></p>
      </div>
    );
  }

  return (
    <div className="relative w-full overflow-auto bg-gray-100 rounded-lg border border-gray-200 shadow-inner" style={{ minHeight: '600px' }}>
      <div
        style={{
          transform: `scale(${scale})`,
          transformOrigin: 'top center',
          width: `${100 / scale}%`,
          marginLeft: `${-(100 / scale - 100) / 2}%`,
        }}
      >
        <iframe
          ref={iframeRef}
          srcDoc={html}
          sandbox="allow-same-origin"
          onLoad={handleLoad}
          style={{
            width: '100%',
            minHeight: '842px', /* A4 height approximation */
            border: 'none',
            display: 'block',
            background: '#fff',
            boxShadow: '0 4px 24px rgba(0,0,0,0.12)',
          }}
          title="CV Preview"
        />
      </div>
    </div>
  );
}
