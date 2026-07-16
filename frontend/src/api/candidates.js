const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export const uploadCandidate = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/candidates/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to upload candidate");
  }

  return response.json();
};

export const getCandidates = async () => {
  const response = await fetch(`${API_URL}/candidates`);
  if (!response.ok) {
    throw new Error("Failed to fetch candidates");
  }
  return response.json();
};

export const getCandidate = async (id) => {
  const response = await fetch(`${API_URL}/candidates/${id}`);
  if (!response.ok) {
    throw new Error("Failed to fetch candidate");
  }
  return response.json();
};

export const deleteCandidate = async (id) => {
  const response = await fetch(`${API_URL}/candidates/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to delete candidate");
  }
  return response.json();
};

export const getCandidateVersions = async (id) => {
  const response = await fetch(`${API_URL}/candidates/${id}/versions`);
  if (!response.ok) {
    throw new Error("Failed to fetch versions");
  }
  return response.json();
};

export const saveCandidateVersion = async (id, profile_json) => {
  const response = await fetch(`${API_URL}/candidates/${id}/versions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile_json }),
  });
  if (!response.ok) {
    throw new Error("Failed to save version");
  }
  return response.json();
};

export const restoreCandidateVersion = async (candidateId, versionId) => {
  const response = await fetch(`${API_URL}/candidates/${candidateId}/versions/${versionId}/restore`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to restore version");
  }
  return response.json();
};
