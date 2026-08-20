export function SectionTitle({ title, subtitle }: { title: string; subtitle?: string }) {
  return <div className="section-heading"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div></div>
}
