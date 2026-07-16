const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export const uploadTemplate = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/templates/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to upload file");
  }

  return response.json();
};

export const getTemplates = async () => {
  const response = await fetch(`${API_URL}/templates`);
  if (!response.ok) {
    throw new Error("Failed to fetch templates");
  }
  return response.json();
};

export const deleteTemplate = async (id) => {
  const response = await fetch(`${API_URL}/templates/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to delete template");
  }
  return response.json();
};
