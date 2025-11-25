import React from "react";
import clsx from "clsx";

type CardProps = {
  children: React.ReactNode;
  variant?: "glass" | "solid";
};

export default function Card({ children, variant = "glass" }: CardProps) {
  return (
    <div
      className={clsx(
        "relative w-full max-w-md rounded-3xl p-10 shadow-xl",
        variant === "glass"
          ? "border border-white/20 bg-white/10 backdrop-blur-lg text-white"
          : "bg-white text-gray-900"
      )}
    >
      {children}
    </div>
  );
}
