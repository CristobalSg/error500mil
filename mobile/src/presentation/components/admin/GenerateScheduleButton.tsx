// src/presentation/components/admin/GenerateScheduleButton.tsx
import React, { useState } from "react";
import { Button, Progress, Modal, message } from "antd";
import { SparklesIcon } from "@heroicons/react/24/outline";
import { useScheduleGenerator } from "../../hooks/useScheduleGenerator";

const GenerateScheduleButton: React.FC = () => {
  const { generating, progress, error, generateSchedule } = useScheduleGenerator();
  const [showModal, setShowModal] = useState(false);

  const handleConfirm = async () => {
    setShowModal(false);
    try {
      await generateSchedule();
      message.success("Horario generado exitosamente");
    } catch (err) {
      message.error(error || "Error al generar el horario");
    }
  };

  return (
    <>
      <section className="rounded-3xl border border-gray-100 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h2 className="text-base font-semibold text-gray-900">Generación de horarios</h2>
            <p className="mt-2 text-sm text-gray-600">
              Genera automáticamente el horario del semestre basado en las configuraciones actuales.
            </p>
          </div>
          
          <Button
            type="primary"
            size="large"
            icon={<SparklesIcon className="h-5 w-5" />}
            onClick={() => setShowModal(true)}
            loading={generating}
            disabled={generating}
            className="ml-4"
          >
            Generar horario
          </Button>
        </div>

        {generating && (
          <div className="mt-4">
            <Progress
              percent={progress}
              status={progress === 100 ? "success" : "active"}
              strokeColor={{
                "0%": "#1890ff",
                "50%": "#52c41a",
                "75%": "#faad14",
                "100%": "#f5222d",
              }}
            />
          </div>
        )}
      </section>

      <Modal
        title="Generar horario del semestre"
        open={showModal}
        onOk={handleConfirm}
        onCancel={() => setShowModal(false)}
        okText="Confirmar y generar"
        cancelText="Cancelar"
        okButtonProps={{ danger: false, type: "primary" }}
      >
        <p>¿Estás seguro de que deseas generar el horario? Este proceso puede tomar varios minutos.</p>
      </Modal>
    </>
  );
};

export default GenerateScheduleButton;
