// src/presentation/components/layout/PageHeader.tsx
import type { ReactNode } from "react";

type PageHeaderProps = {
  title: string;
  leftAction?: ReactNode;
  rightAction?: ReactNode;
  className?: string;
};

/**
 * Encabezado fijo superior reutilizable.
 * Compatible con safe-area y botones izquierdo/derecho (Heroicons u otros).
 */
export default function PageHeader({
  title,
  leftAction,
  rightAction,
  className = "",
}: PageHeaderProps) {
  return (
    <header className={`bg-white shadow-md fixed top-0 left-0 right-0 z-20 safe-top ${className}`}>
      <div className="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
        <div className="w-8 flex justify-start">{leftAction}</div>
        <h1 className="text-lg font-semibold text-gray-800 truncate">{title}</h1>
        <div className="w-8 flex justify-end">{rightAction}</div>
      </div>
    </header>
  );
}
