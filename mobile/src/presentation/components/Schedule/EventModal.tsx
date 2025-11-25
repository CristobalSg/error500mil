import { useMemo, useState } from "react";
import { Modal, Button, Input, Space, Empty } from "antd";
import { PlusIcon, PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import type { Events, SlotRef } from "../../types/schedule";

interface Props {
  open: boolean;
  onClose: () => void;
  events: Events;
  slot: SlotRef | null;
  canEdit: boolean;
  onAdd: (slot: SlotRef, text: string) => void;
  onEdit: (slot: SlotRef, idx: number, text: string) => void;
  onDelete: (slot: SlotRef, idx: number) => void;
}

export default function EventModal({
  open, onClose, events, slot, canEdit, onAdd, onEdit, onDelete,
}: Props) {
  const [draft, setDraft] = useState("");
  const [editingIdx, setEditingIdx] = useState<number | null>(null);
  const [editingText, setEditingText] = useState("");

  const list = useMemo(() => {
    if (!slot) return [];
    return events[slot.day]?.[slot.hour] ?? [];
  }, [events, slot]);

  const title = slot ? `${slot.day.toUpperCase()} - ${slot.hour}` : "Eventos";

  return (
    <Modal open={open} title={title} onCancel={onClose} footer={null} destroyOnClose>
      {list.length === 0 ? (
        <Empty description="No hay eventos en este horario." />
      ) : (
        <div className="space-y-2">
          {list.map((evt, idx) => (
            <div key={idx} className="flex items-start justify-between gap-2 border-b pb-2">
              {editingIdx === idx ? (
                <div className="flex-1">
                  <Input
                    value={editingText}
                    onChange={(e) => setEditingText(e.target.value)}
                    size="small"
                    autoFocus
                  />
                </div>
              ) : (
                <span className="flex-1">{evt}</span>
              )}
              {canEdit && slot && (
                <Space>
                  {editingIdx === idx ? (
                    <>
                      <Button
                        size="small"
                        type="primary"
                        onClick={() => {
                          if (!editingText.trim()) return;
                          onEdit(slot, idx, editingText.trim());
                          setEditingIdx(null);
                          setEditingText("");
                        }}
                      >
                        Guardar
                      </Button>
                      <Button
                        size="small"
                        onClick={() => {
                          setEditingIdx(null);
                          setEditingText("");
                        }}
                      >
                        Cancelar
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button
                        type="link"
                        size="small"
                        icon={<PencilIcon className="h-4 w-4" />}
                        onClick={() => {
                          setEditingIdx(idx);
                          setEditingText(evt);
                        }}
                      />
                      <Button
                        type="link"
                        danger
                        size="small"
                        icon={<TrashIcon className="h-4 w-4" />}
                        onClick={() => onDelete(slot, idx)}
                      />
                    </>
                  )}
                </Space>
              )}
            </div>
          ))}
        </div>
      )}

      {canEdit && slot && (
        <div className="mt-4 flex gap-2">
          <Input
            placeholder="Nombre del evento"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onPressEnter={() => {
              if (!draft.trim()) return;
              onAdd(slot, draft.trim());
              setDraft("");
            }}
          />
          <Button
            type="primary"
            icon={<PlusIcon className="h-4 w-4" />}
            onClick={() => {
              if (!draft.trim()) return;
              onAdd(slot, draft.trim());
              setDraft("");
            }}
          >
            Agregar
          </Button>
        </div>
      )}
    </Modal>
  );
}
