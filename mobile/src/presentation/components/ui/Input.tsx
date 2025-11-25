// src/ui/Input.tsx
import React from "react";
import clsx from "clsx";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  value: string;
  variant?: "glass" | "solid";
}

const Input: React.FC<InputProps> = ({ label, value, className, variant = "glass", ...props }) => {
  const isGlass = variant === "glass";
  return (
    <div className="relative w-full">
      {/* Input */}
      <input
        {...props}
        value={value}
        required
        // 👇 puntos clave para iOS:
        // - peer para que funcionen peer-focus/peer-placeholder-shown
        // - appearance-none/shadow-none quitan look nativo
        // - text-base (≈16px) evita zoom en iOS
        // - placeholder=" " para usar :placeholder-shown en el label
        placeholder=" "
        className={clsx(
          "peer w-full text-base",
          "px-4 pt-5 pb-2 min-h-12 rounded-xl",
          "appearance-none shadow-none outline-none transition",
          isGlass
            ? "border border-white/20 bg-white/10 text-white backdrop-blur-md focus:border-cyan-400 focus:bg-white/20 focus-visible:ring-2 focus-visible:ring-cyan-400/30"
            : "border border-gray-300 bg-white text-gray-900 focus:border-indigo-500 focus-visible:ring-2 focus-visible:ring-indigo-500/30",
          className
        )}
        // ayudas de teclado iOS (ajusta según el campo real)
        inputMode={props.inputMode ?? "text"}
        autoComplete={props.autoComplete ?? "on"}
      />

      {/* Label flotante */}
      {label && (
        <label
          className={clsx(
            "absolute left-4 top-2 z-[1]",
            "px-1 rounded transition-all duration-200 pointer-events-none",
            // estado base cuando placeholder está visible (no hay texto)
            isGlass ? "text-white/70" : "text-gray-500",
            "peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-base peer-placeholder-shown:bg-transparent",
            // flotado cuando hay valor o foco
            (value?.length ?? 0) > 0
              ? clsx(
                  "top-1 text-sm",
                  isGlass ? "bg-purple-600 text-cyan-100" : "bg-white text-indigo-600"
                )
              : clsx(
                  "peer-focus:top-1 peer-focus:text-sm",
                  isGlass
                    ? "peer-focus:bg-purple-600 peer-focus:text-cyan-100"
                    : "peer-focus:bg-white peer-focus:text-indigo-600"
                )
          )}
        >
          {label}
        </label>
      )}

      {/* Borde animado */}
      <span
        className={clsx(
          "pointer-events-none absolute bottom-0 left-1/2 h-0.5 w-0 -translate-x-1/2 transform",
          "bg-gradient-to-r from-cyan-400 to-indigo-500",
          "transition-all duration-300",
          "peer-focus:w-full"
        )}
      />
    </div>
  );
};

export default Input;
