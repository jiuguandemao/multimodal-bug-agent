export function Profile({ user }) {
  return (
    <section>
      <img src={user.avatar} />
      <h1>{user.name}</h1>
    </section>
  );
}
