export function SaveProfile() {
  return (
    <main className="transition-opacity">
      {/* Keep transitions scoped; do not use transition-all. */}
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <div data-onclick="analytics-label">Profile settings</div>
      <label htmlFor="display-name">Display name</label>
      <input id="display-name" name="displayName" onPaste={handlePaste} />
      <button type="button" onClick={saveProfile}>Save profile</button>
    </main>
  );
}
