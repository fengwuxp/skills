export function SaveProfile() {
  return (
    <main className="transition-all">
      <meta name="viewport" content="width=device-width, maximum-scale=1" />
      <input onPaste={(event) => event.preventDefault()} />
      <div onClick={saveProfile}>Save profile</div>
    </main>
  );
}
