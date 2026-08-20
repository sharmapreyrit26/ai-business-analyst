export function LoadingState() { return <div className="card state-card"><div className="spinner"/><span>Loading ProfitLens data…</span></div> }
export function ErrorState({ error }: { error: string }) { return <div className="card state-card error"><strong>Could not load data</strong><span>{error}</span></div> }
export function EmptyState({ title, message }: { title: string; message: string }) { return <div className="card state-card"><strong>{title}</strong><span>{message}</span></div> }
