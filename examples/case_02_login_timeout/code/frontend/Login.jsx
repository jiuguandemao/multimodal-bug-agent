export async function submitLogin(form) {
  setLoading(true);
  const response = await api.post("/api/login", form, { timeout: 8000 });
  setToken(response.data.token);
  setLoading(false);
}
