const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

/**
 * Render a CV HTML from candidate + template (returns draft_id + html)
 */
export const renderCV = async (candidateId, templateId, customJson = null) => {
  const response = await fetch(`${API_URL}/generator/render`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate_id: candidateId,
      template_id: templateId,
      custom_json: customJson,
    }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to render CV");
  }
  return response.json(); // { draft_id, html }
};

/**
 * Export a draft as PDF blob (trigger browser download)
 */
export const exportPDF = async (draftId) => {
  const response = await fetch(`${API_URL}/generator/export/pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ draft_id: draftId }),
  });
  if (!response.ok) throw new Error("Failed to export PDF");
  return response.blob();
};

/**
 * Export a draft as DOCX blob
 */
export const exportDOCX = async (draftId) => {
  const response = await fetch(`${API_URL}/generator/export/docx`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ draft_id: draftId }),
  });
  if (!response.ok) throw new Error("Failed to export DOCX");
  return response.blob();
};

/**
 * Update draft custom_json and re-render
 */
export const updateDraft = async (draftId, customJson) => {
  const response = await fetch(`${API_URL}/generator/drafts/${draftId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ custom_json: customJson }),
  });
  if (!response.ok) throw new Error("Failed to update draft");
  return response.json(); // { draft_id, html }
};

/**
 * Trigger a blob download in the browser
 */
export const downloadBlob = (blob, filename) => {
  const href = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = href;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(href);
};
