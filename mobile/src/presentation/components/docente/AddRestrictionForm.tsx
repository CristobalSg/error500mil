import React, { useEffect, useRef, type RefObject } from "react";
import dayjs from "dayjs";
import { Modal, Form, Select, Input, Switch } from "antd";
import type { InputRef } from "antd";
import type { RestriccionHorarioInput, RestriccionHorarioView } from "../../hooks/useDocenteHorarioRestrictions";
import { useAuth } from "../../../app/providers/AuthProvider";

const { TextArea } = Input;

interface AddRestrictionFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: RestriccionHorarioInput, id?: number) => Promise<void> | void;
  saving?: boolean;
  mode?: "create" | "edit";
  initialValues?: RestriccionHorarioView | null;
}

const daysOfWeek = [
  { label: "Lunes", value: 1 },
  { label: "Martes", value: 2 },
  { label: "Miércoles", value: 3 },
  { label: "Jueves", value: 4 },
  { label: "Viernes", value: 5 },
  { label: "Sábado", value: 6 },
  { label: "Domingo", value: 0 },
];

const AddRestrictionForm: React.FC<AddRestrictionFormProps> = ({
  open,
  onClose,
  onSubmit,
  saving = false,
  mode = "create",
  initialValues = null,
}) => {
  const [form] = Form.useForm();
  const { user } = useAuth();
  const startHourRef = useRef<InputRef | null>(null);
  const startMinuteRef = useRef<InputRef | null>(null);
  const endHourRef = useRef<InputRef | null>(null);
  const endMinuteRef = useRef<InputRef | null>(null);
  const handleStartHourChange = createTimeInputHandler(form, "startHour", 23, startMinuteRef);
  const handleStartMinuteChange = createTimeInputHandler(form, "startMinute", 59, endHourRef);
  const handleEndHourChange = createTimeInputHandler(form, "endHour", 23, endMinuteRef);
  const handleEndMinuteChange = createTimeInputHandler(form, "endMinute", 59);

  useEffect(() => {
    if (!open) return;

    if (mode === "edit" && initialValues) {
      const startTime = dayjs(initialValues.hora_inicio);
      const endTime = dayjs(initialValues.hora_fin);
      form.setFieldsValue({
        dia: initialValues.dia_semana,
        startHour: startTime.format("HH"),
        startMinute: startTime.format("mm"),
        endHour: endTime.format("HH"),
        endMinute: endTime.format("mm"),
        descripcion: initialValues.descripcion ?? "",
        disponible: initialValues.disponible,
      });
    } else {
      form.resetFields();
      form.setFieldsValue({ disponible: false });
    }
  }, [open, mode, initialValues, form]);

const handleOk = async () => {
  const values = await form.validateFields();

  if (!user?.id) {
    throw new Error("Usuario no autenticado");
  }

  const startTime = buildDayjsTime(values.startHour, values.startMinute);
  const endTime = buildDayjsTime(values.endHour, values.endMinute);

  if (!endTime.isAfter(startTime)) {
    form.setFields([
      {
        name: "endHour",
        errors: ["La hora de fin debe ser posterior a la hora de inicio"],
      },
      {
        name: "endMinute",
        errors: [],
      },
    ]);
    return;
  }

  const payload: RestriccionHorarioInput = {
    dia_semana: Number(values.dia),
    hora_inicio: startTime.format("HH:mm:ss"),
    hora_fin: endTime.format("HH:mm:ss"),
    descripcion: values.descripcion?.trim() || "",
    disponible: !!values.disponible,
    activa: true,
    user_id: Number(user.id),
  };
  await onSubmit(payload, initialValues?.id);
  form.resetFields();
};

function buildDayjsTime(hour: string | number, minute: string | number) {
  const safeHour = Number(hour ?? 0);
  const safeMinute = Number(minute ?? 0);
  return dayjs().set("hour", safeHour).set("minute", safeMinute).set("second", 0).set("millisecond", 0);
}

function buildTimeRules(label: string, max: number) {
  return [
    { required: true, message: `Ingresa ${label}` },
    {
      validator: (_: unknown, value: string) => {
        if (value === undefined || value === null || value === "") {
          return Promise.resolve();
        }
        if (!/^\d{1,2}$/.test(value)) {
          return Promise.reject(new Error("Solo números de dos dígitos"));
        }
        const numericValue = Number(value);
        if (Number.isNaN(numericValue) || numericValue < 0 || numericValue > max) {
          return Promise.reject(new Error(`Introduce un valor entre 0 y ${max}`));
        }
        return Promise.resolve();
      },
    },
  ];
}

function sanitizeInput(value: string, max: number) {
  const digits = value.replace(/\D/g, "").slice(0, 2);
  if (digits === "") return "";
  const numericValue = Number(digits);
  if (Number.isNaN(numericValue)) return "";
  const clamped = Math.min(numericValue, max);
  return clamped.toString().padStart(digits.length >= 2 ? 2 : digits.length, "0");
}

function createTimeInputHandler(
  form: ReturnType<typeof Form.useForm>[0],
  field: string,
  max: number,
  nextRef?: RefObject<InputRef | null>,
) {
  return (event: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = sanitizeInput(event.target.value, max);
    form.setFieldsValue({ [field]: formatted });
    if (formatted.length === 2 && nextRef?.current) {
      nextRef.current.focus?.();
    }
  };
}


  const handleCancel = () => {
    form.resetFields();
    onClose();
  };


  return (
    <Modal
      title={mode === "edit" ? "Editar Restricción" : "Agregar Restricción"}
      open={open}
      onCancel={handleCancel}
      onOk={handleOk}
      okText={mode === "edit" ? "Guardar cambios" : "Guardar"}
      confirmLoading={saving}
      centered
      style={{ paddingBottom: 0 }}
      rootClassName="docente-restriction-modal"
    >
      <Form
        form={form}
        layout="vertical"
        className="space-y-3"
        style={{ marginTop: 10 }}
        initialValues={{ disponible: false }}
      >
        <Form.Item
          label="Día de la semana"
          name="dia"
          rules={[{ required: true, message: "Selecciona un día" }]}
        >
          <Select
            placeholder="Selecciona un día"
            options={daysOfWeek}
            optionFilterProp="label"
          />
        </Form.Item>

        <Form.Item label="Horario" required className="mb-0">
          <div className="flex flex-row flex-wrap gap-4 sm:items-end">
            <div className="flex flex-1 flex-col gap-1">
              <span className="text-xs font-semibold uppercase tracking-[0.2em] text-[#004F9F99]">
                Inicio
              </span>
              <div className="flex items-center gap-1">
                <Form.Item
                  name="startHour"
                  className="mb-0 w-16"
                  rules={buildTimeRules("la hora de inicio", 23)}
                >
                  <Input
                    ref={startHourRef}
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={2}
                    placeholder="HH"
                    autoComplete="off"
                    onChange={handleStartHourChange}
                  />
                </Form.Item>
                <span className="text-gray-500">:</span>
                <Form.Item
                  name="startMinute"
                  className="mb-0 w-16"
                  rules={buildTimeRules("los minutos de inicio", 59)}
                >
                  <Input
                    ref={startMinuteRef}
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={2}
                    placeholder="MM"
                    autoComplete="off"
                    onChange={handleStartMinuteChange}
                  />
                </Form.Item>
              </div>
            </div>

            <div className="flex flex-1 flex-col gap-1">
              <span className="text-xs font-semibold uppercase tracking-[0.2em] text-[#004F9F99]">
                Fin
              </span>
              <div className="flex items-center gap-1">
                <Form.Item
                  name="endHour"
                  className="mb-0 w-16"
                  rules={buildTimeRules("la hora de fin", 23)}
                >
                  <Input
                    ref={endHourRef}
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={2}
                    placeholder="HH"
                    autoComplete="off"
                    onChange={handleEndHourChange}
                  />
                </Form.Item>
                <span className="text-gray-500">:</span>
                <Form.Item
                  name="endMinute"
                  className="mb-0 w-16"
                  rules={buildTimeRules("los minutos de fin", 59)}
                >
                  <Input
                    ref={endMinuteRef}
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={2}
                    placeholder="MM"
                    autoComplete="off"
                    onChange={handleEndMinuteChange}
                  />
                </Form.Item>
              </div>
            </div>
          </div>
        </Form.Item>

        <Form.Item
          label="Descripción"
          name="descripcion"
        >
          <TextArea rows={2} placeholder="Motivo o detalle de la restricción" />
        </Form.Item>

        <Form.Item
          label="Disponibilidad"
          name="disponible"
          valuePropName="checked"
        >
          <Switch checkedChildren="Disponible" unCheckedChildren="No disponible" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default AddRestrictionForm;
