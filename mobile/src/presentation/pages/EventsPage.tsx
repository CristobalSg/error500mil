// src/presentation/pages/EventsPage.tsx
import React, { useMemo } from "react";
import BottomNav from "../components/BottomNav"
import dayjs from "dayjs";
import "dayjs/locale/es";
dayjs.locale("es");

import { CalendarDaysIcon } from "@heroicons/react/24/outline";
import EventsCalendar from "../components/Events/EventsCalendar";
import EventModal from "../components/Events/EventModal";
import { useEventsVM } from "../viewmodels/useEventsVM";

const EventsPage: React.FC = () => {
  const vm = useEventsVM();

  const todayText = useMemo(
    () =>
      new Date().toLocaleDateString(undefined, {
        weekday: "short",
        year: "numeric",
        month: "long",
        day: "numeric",
      }),
    []
  );

  const dateLabel = vm.selectedDate?.format("dddd, D [de] MMMM YYYY") ?? "";

  const editingItem =
    vm.editingId ? vm.eventsForSelected.find((e) => e.id === vm.editingId) ?? null : null;

  return (
    <div className="flex min-h-[var(--app-height)] flex-col bg-gray-50">
      {/* Header (con tu layout) */}
      <header className="bg-white shadow-md fixed top-0 left-0 right-0 z-10 safe-top">
        <div className="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CalendarDaysIcon className="h-5 w-5 text-gray-700" />
            <h1 className="text-lg font-semibold text-gray-800">Eventos</h1>
          </div>
          <span className="text-xs text-gray-500">{todayText}</span>
        </div>
      </header>

      {/* Main */}
      <main
        className="ios-scroll mx-auto flex w-full max-w-md flex-1 flex-col overflow-y-auto px-4"
        style={{
          paddingTop: "calc(80px + env(safe-area-inset-top, 0px))",
          paddingBottom: "calc(120px + env(safe-area-inset-bottom, 0px))",
        }}
      >
        <p className="text-gray-700 text-sm mt-4 mb-3">
          Selecciona una fecha para ver y gestionar tus eventos.
        </p>

        {vm.loading ? (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        ) : (
          <EventsCalendar 
            value={vm.selectedDate} 
            onSelect={vm.openForDate}
            eventsMap={vm.eventsMap}
          />
        )}
      </main>

      {/* Modal */}
      <EventModal
        open={vm.isModalOpen}
        dateLabel={dateLabel}
        events={vm.eventsForSelected}
        editingItem={editingItem}
        onCancel={vm.closeModal}
        onUpsert={vm.upsertEvent}
        onEdit={vm.beginEdit}
        onDelete={vm.removeEvent}
      />

      {/* Bottom Nav */}
      <BottomNav />
    </div>
  );
};

export default EventsPage;
