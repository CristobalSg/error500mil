// src/presentation/components/layout/AppLayout.tsx
import type { ReactNode } from "react";
import PageHeader from "./PageHeader";
import BottomNav from "../BottomNav";

type AppLayoutProps = {
  title: string;
  children: ReactNode;
  leftAction?: ReactNode;
  rightAction?: ReactNode;
  showBottomNav?: boolean;
  className?: string;
};

/**
 * Layout base para vistas móviles.
 * - Header fijo arriba
 * - BottomNav fijo abajo
 * - Contenido con márgenes automáticos y safe-area insets
 */
export default function AppLayout({
  title,
  children,
  leftAction,
  rightAction,
  showBottomNav = true,
  className = "",
}: AppLayoutProps) {
  return (
    <div className="flex min-h-[var(--app-height)] flex-col bg-gray-50">
      {/* Header */}
      <PageHeader title={title} leftAction={leftAction} rightAction={rightAction} />

      {/* Contenido principal */}
      <main
        className={`ios-scroll mx-auto flex w-full max-w-md flex-1 flex-col overflow-y-auto px-4 ${className}`}
        style={{
          paddingTop: "calc(80px + env(safe-area-inset-top, 0px))",
          paddingBottom: showBottomNav
            ? "calc(120px + env(safe-area-inset-bottom, 0px))"
            : "env(safe-area-inset-bottom, 0px)",
        }}
      >
        {children}
      </main>

      {/* Bottom Navigation */}
      {showBottomNav && (
        <div
          className="fixed bottom-0 left-0 right-0 z-20"
          style={{
            paddingBottom: "env(safe-area-inset-bottom, 0px)",
            boxShadow: "0 -2px 10px rgba(0,0,0,0.06)",
          }}
        >
          <div className="max-w-md mx-auto">
            <BottomNav />
          </div>
        </div>
      )}
    </div>
  );
}
