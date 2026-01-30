// We import ReactNode to type "children"
// ReactNode = anything React can render (JSX, text, components, etc.)
import type { ReactNode } from "react";

// This is a TypeScript type that defines
// what props the Card component accepts
type CardProps = {
  title?: string;        // optional title (can be undefined)
  children: ReactNode;   // REQUIRED: content inside the card
};

// This is a normal React function component
export default function Card({ title, children }: CardProps) {
  return (
    // This div is the CARD container
    // All cards share these styles
    <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
      
      {/* If a title exists, render it */}
      {title && (
        <h3 className="mb-4 text-sm font-medium text-slate-400">
          {title}
        </h3>
      )}

      {/* Whatever you place inside <Card>...</Card> goes here */}
      {children}
    </div>
  );
}
