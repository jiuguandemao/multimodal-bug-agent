export async function handleSubmit(form) {
  const response = await fetch("/api/register", {
    method: "POST",
    body: JSON.stringify(form)
  });
  const data = await response.json();
  setCurrentUser(data.user.name);
}
