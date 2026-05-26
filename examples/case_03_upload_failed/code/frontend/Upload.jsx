export async function uploadFile(file) {
  const response = await api.post("/api/upload", file);
  if (!response.ok) {
    setError("上传失败");
  }
}
