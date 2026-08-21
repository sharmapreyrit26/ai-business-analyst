export function LoadingState() {
  return <div className="notice info">Loading data…</div>
}

export function ErrorState({ error }: { error: string }) {
  return (
    <div className="notice error">
      <strong>Could not load data</strong>
      <div>{error}</div>
    </div>
  )
}
