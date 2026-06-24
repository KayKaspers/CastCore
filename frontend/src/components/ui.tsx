import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from "react";

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`cc-panel p-5 ${className}`}>{children}</div>;
}

type Variant = "primary" | "ghost" | "danger";

const variants: Record<Variant, string> = {
  primary: "bg-core-green text-deep-navy hover:brightness-110",
  ghost: "border border-slate/40 text-mist hover:border-core-green/60",
  danger: "bg-danger text-white hover:brightness-110",
};

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={`px-3 py-2 rounded-md text-sm font-medium transition disabled:opacity-40 disabled:cursor-not-allowed ${variants[variant]} ${className}`}
      {...props}
    />
  );
}

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className="w-full bg-deep-navy border border-slate/40 rounded-md px-3 py-2 text-sm text-mist
                 focus:outline-none focus:border-core-green placeholder:text-slate/60"
      {...props}
    />
  );
}

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className="w-full bg-deep-navy border border-slate/40 rounded-md px-3 py-2 text-sm text-mist
                 focus:outline-none focus:border-core-green"
      {...props}
    />
  );
}

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block space-y-1">
      <span className="text-xs uppercase tracking-wide text-slate">{label}</span>
      {children}
    </label>
  );
}

const badgeColors: Record<string, string> = {
  running: "bg-core-green/20 text-core-green",
  starting: "bg-signal-cyan/20 text-signal-cyan",
  stopped: "bg-slate/20 text-slate",
  failed: "bg-danger/20 text-danger",
  green: "bg-core-green/20 text-core-green",
  yellow: "bg-warning/20 text-warning",
  red: "bg-danger/20 text-danger",
  done: "bg-core-green/20 text-core-green",
  pending: "bg-slate/20 text-slate",
  skipped: "bg-warning/20 text-warning",
};

export function Badge({ status, children }: { status: string; children?: ReactNode }) {
  const color = badgeColors[status] ?? "bg-slate/20 text-slate";
  return <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>{children ?? status}</span>;
}
