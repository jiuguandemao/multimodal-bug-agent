export async function loadUsers() {
  const response = await api.get("/api/admin/users");
  setUsers(response.data);
}
