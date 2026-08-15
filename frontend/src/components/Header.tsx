interface Props {
  ollamaAvailable: boolean | null;
}

export function Header({ ollamaAvailable }: Props) {
  return (
    <header className="border-b border-[var(--color-line)] px-8 py-6 flex items-baseline justify-between scanline-grid">
      <div>
        <h1 className="font-display text-3xl tracking-tight text-[var(--color-text)]">
          EIDOLON
        </h1>
        <p className="font-mono text-xs text-[var(--color-text-dim)] mt-1 tracking-wide">
          when does an ai stop being itself?
        </p>
      </div>
      <div className="font-mono text-xs flex items-center gap-2">
        <span
          className={`inline-block w-2 h-2 rounded-full ${
            ollamaAvailable === null
              ? "bg-[var(--color-text-faint)]"
              : ollamaAvailable
              ? "bg-[var(--color-cyan)]"
              : "bg-[var(--color-amber)]"
          }`}
        />
        <span className="text-[var(--color-text-dim)]">
          {ollamaAvailable === null
            ? "checking ollama…"
            : ollamaAvailable
            ? "ollama connected"
            : "ollama unavailable — demo mode"}
        </span>
      </div>
    </header>
  );
}
