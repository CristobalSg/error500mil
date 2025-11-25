// src/presentation/components/EventsCalendar.tsx
import React from "react";
import { Calendar, Badge } from "antd";
import type { Dayjs } from "dayjs";
import type { EventsMap } from "../../viewmodels/useEventsVM";

type Props = {
  value?: Dayjs | null;
  onSelect: (d: Dayjs) => void;
  eventsMap?: EventsMap;
};

const EventsCalendar: React.FC<Props> = ({ value, onSelect, eventsMap = {} }) => {
  const dateCellRender = (date: Dayjs) => {
    const dateKey = date.format("YYYY-MM-DD");
    const events = eventsMap[dateKey] || [];
    
    if (events.length === 0) return null;
    
    return (
      <div className="flex justify-center">
        <Badge 
          count={events.length} 
          style={{ backgroundColor: '#52c41a', fontSize: '10px' }}
        />
      </div>
    );
  };

  return (
    <div className="bg-white shadow-sm p-3 w-full rounded-xl border border-gray-200">
      <Calendar 
        fullscreen={false} 
        value={value ?? undefined} 
        onSelect={onSelect}
        cellRender={dateCellRender}
      />
    </div>
  );
};

export default EventsCalendar;
