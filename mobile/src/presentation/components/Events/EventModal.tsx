// src/presentation/components/EventModal.tsx
import React, { useEffect } from "react";
import { Modal, Button, Form, Input, TimePicker, Badge } from "antd";
import dayjs, { Dayjs } from "dayjs";
import { PlusCircleIcon } from "@heroicons/react/24/outline";
import type { EventItem } from "../../viewmodels/useEventsVM";
import EventList from "./EventList";

type FormValues = { 
  title: string; 
  description?: string; 
  startTime?: Dayjs | null;
  endTime?: Dayjs | null;
};

type Props = {
  open: boolean;
  dateLabel: string;
  events: EventItem[];
  editingItem: EventItem | null;
  onCancel: () => void;
  onUpsert: (data: { 
    id?: string; 
    title: string; 
    description?: string; 
    startTime?: string; 
    endTime?: string;
  }) => void;
  onEdit: (item: EventItem) => void;
  onDelete: (id: string) => void;
};

const EventModal: React.FC<Props> = ({
  open,
  dateLabel,
  events,
  editingItem,
  onCancel,
  onUpsert,
  onEdit,
  onDelete,
}) => {
  const [form] = Form.useForm<FormValues>();

  // Función para deshabilitar horas fuera del rango 08:00 - 21:00
  const disabledHours = () => {
    const hours = [];
    for (let i = 0; i < 8; i++) hours.push(i);  // 00:00 - 07:59
    for (let i = 22; i < 24; i++) hours.push(i); // 22:00 - 23:59
    return hours;
  };

  // Cargar datos al comenzar edición
  useEffect(() => {
    if (editingItem) {
      form.setFieldsValue({
        title: editingItem.title,
        description: editingItem.description,
        startTime: editingItem.startTime ? dayjs(editingItem.startTime, "HH:mm:ss") : null,
        endTime: editingItem.endTime ? dayjs(editingItem.endTime, "HH:mm:ss") : null,
      });
    } else {
      form.resetFields();
    }
  }, [editingItem, form]);

  const submit = async () => {
    const values = await form.validateFields();
    onUpsert({
      id: editingItem?.id,
      title: values.title,
      description: values.description,
      startTime: values.startTime ? dayjs(values.startTime).format("HH:mm") : undefined,
      endTime: values.endTime ? dayjs(values.endTime).format("HH:mm") : undefined,
    });
    form.resetFields();
  };

  return (
    <Modal
      open={open}
      onCancel={onCancel}
      title={
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-sm text-gray-500">Eventos para</span>
            <span className="text-base font-semibold">{dateLabel}</span>
          </div>
          <Badge count={events.length} />
        </div>
      }
      footer={
        <div className="flex items-center justify-between w-full">
          <Button onClick={onCancel}>Cerrar</Button>
          <Button type="primary" icon={<PlusCircleIcon className="h-4 w-4" />} onClick={submit}>
            {editingItem ? "Guardar cambios" : "Agregar evento"}
          </Button>
        </div>
      }
    >
      <Form form={form} layout="vertical" className="mb-4" initialValues={{ title: "", description: "", startTime: null, endTime: null }}>
        <Form.Item label="Título" name="title" rules={[{ required: true, message: "Ingresa un título" }]}>
          <Input placeholder="Ej. Reunión, Cumpleaños, Tarea..." />
        </Form.Item>
        <Form.Item label="Descripción" name="description">
          <Input.TextArea placeholder="Detalles opcionales" autoSize={{ minRows: 2, maxRows: 4 }} />
        </Form.Item>
        
        <div className="grid grid-cols-2 gap-4">
          <Form.Item 
            label="Hora de Inicio" 
            name="startTime"
            rules={[{ required: true, message: "Selecciona hora de inicio" }]}
          >
            <TimePicker 
              format="HH:mm" 
              minuteStep={5} 
              placeholder="Inicio"
              className="w-full"
              disabledHours={disabledHours}
              showNow={false}
              defaultOpenValue={dayjs().hour(8).minute(0)}
            />
          </Form.Item>
          
          <Form.Item 
            label="Hora de Fin" 
            name="endTime"
            rules={[
              { required: true, message: "Selecciona hora de fin" },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  const startTime = getFieldValue('startTime');
                  if (!value || !startTime) {
                    return Promise.resolve();
                  }
                  if (value.isAfter(startTime)) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('La hora de fin debe ser posterior a la hora de inicio'));
                },
              }),
            ]}
          >
            <TimePicker 
              format="HH:mm" 
              minuteStep={5} 
              placeholder="Fin"
              className="w-full"
              disabledHours={disabledHours}
              showNow={false}
              defaultOpenValue={dayjs().hour(9).minute(0)}
            />
          </Form.Item>
        </div>
        
        <div className="text-xs text-gray-500 mt-2">
          ⏰ Horario permitido: 08:00 - 21:00
        </div>
      </Form>

      <EventList events={events} onEdit={onEdit} onDelete={onDelete} />
    </Modal>
  );
};

export default EventModal;
