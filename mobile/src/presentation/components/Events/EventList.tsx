// src/presentation/components/EventList.tsx
import React from "react";
import { Button, List, Popconfirm, Empty } from "antd";
import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import type { EventItem } from "../../viewmodels/useEventsVM";

type Props = {
  events: EventItem[];
  onEdit: (item: EventItem) => void;
  onDelete: (id: string) => void;
};

const EventList: React.FC<Props> = ({ events, onEdit, onDelete }) => {
  if (!events.length) {
    return (
      <div className="py-6">
        <Empty description="Sin eventos para este día" />
      </div>
    );
  }

  return (
    <List
      itemLayout="horizontal"
      dataSource={events}
      renderItem={(item) => (
        <List.Item
          actions={[
            <Button key="edit" type="text" onClick={() => onEdit(item)} icon={<PencilIcon className="h-4 w-4" />}>
              Editar
            </Button>,
            <Popconfirm
              key="delete"
              title="Eliminar evento"
              description="¿Seguro que deseas eliminar este evento?"
              okText="Sí"
              cancelText="No"
              onConfirm={() => onDelete(item.id)}
            >
              <Button type="text" danger icon={<TrashIcon className="h-4 w-4" />}>
                Eliminar
              </Button>
            </Popconfirm>,
          ]}
        >
          <List.Item.Meta
            title={
              <div className="flex items-center gap-2">
                {(item.startTime || item.time) && (
                  <span className="inline-flex items-center px-2 py-0.5 text-xs rounded bg-blue-100 text-blue-800">
                    {item.startTime ? item.startTime.substring(0, 5) : item.time}
                    {item.endTime && ` - ${item.endTime.substring(0, 5)}`}
                  </span>
                )}
                <span className="font-medium">{item.title}</span>
              </div>
            }
            description={item.description}
          />
        </List.Item>
      )}
    />
  );
};

export default EventList;
