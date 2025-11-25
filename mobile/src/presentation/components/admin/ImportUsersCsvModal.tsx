import { useState } from "react";

type Props = { open: boolean; onClose: () => void };

export default function ImportUsersCsvModal({ open, onClose }: Props) {
  const [file, setFile] = useState<File | null>(null);
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative z-10 w-[92%] max-w-md rounded-xl bg-white p-5 shadow-xl">
        <h3 className="text-base font-semibold text-gray-900">Importar usuarios por CSV</h3>
        <p className="mt-1 text-xs text-gray-500">Selecciona un archivo .csv para cargar una lista de usuarios.</p>

        <div className="mt-4">
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-gray-700 file:mr-4 file:rounded-md file:border-0 file:bg-blue-600 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-blue-700"
          />
          {file && (
            <p className="mt-2 text-xs text-gray-600">
              Archivo seleccionado: <span className="font-medium">{file.name}</span>
            </p>
          )}
        </div>

        <div className="mt-5 flex justify-end gap-2">
          <button
            className="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            onClick={onClose}
          >
            Cancelar
          </button>
          <button
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-blue-400"
            disabled={!file}
            onClick={onClose}
            title="Vista previa; no realiza importación real."
          >
            Cargar CSV
          </button>
        </div>
      </div>
    </div>
  );
}
