export function AuthShell({
  eyebrow,
  title,
  subtitle,
  children,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <main className="flex min-h-screen">
      {/* Left: form */}
      <div className="flex w-full flex-col justify-center px-8 py-16 sm:px-16 lg:w-1/2">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/15 text-accent">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2l3 6 6 1-4.5 4.5L18 20l-6-3-6 3 1.5-6.5L3 9l6-1 3-6z" />
              </svg>
            </div>
            <span className="font-display text-sm font-semibold tracking-wide text-white">AI CAREER COPILOT</span>
          </div>

          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-accent2">{eyebrow}</p>
          <h1 className="font-display mb-2 text-3xl font-bold text-white">{title}</h1>
          <p className="mb-8 text-sm text-muted">{subtitle}</p>

          {children}
        </div>
      </div>

      {/* Right: cockpit visual */}
      <div className="relative hidden w-1/2 overflow-hidden border-l border-line bg-panel lg:block">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="relative h-72 w-72">
            <div className="absolute inset-0 rounded-full border border-line" />
            <div className="absolute inset-8 rounded-full border border-accent/30" />
            <div className="absolute inset-16 rounded-full border border-accent2/20" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <p className="font-display text-5xl font-bold text-white">92%</p>
                <p className="mt-1 text-xs uppercase tracking-wider text-muted">ATS Match Score</p>
              </div>
            </div>
          </div>
        </div>
        <div className="absolute bottom-10 left-10 right-10 rounded-xl2 border border-line bg-panel2/80 p-4 backdrop-blur">
          <p className="text-xs uppercase tracking-wider text-muted">Master Resume</p>
          <p className="mt-1 text-sm text-white">Parsed once. Reused everywhere - matching, tailoring, cover letters.</p>
        </div>
      </div>
    </main>
  );
}
