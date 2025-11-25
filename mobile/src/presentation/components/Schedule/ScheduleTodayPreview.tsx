import { useMemo } from "react";
import { useScheduleEvents } from "../../hooks/useScheduleEvents";
import type { DayKey, ScheduleEventDetail } from "../../types/schedule";

const WEEKDAY_TO_DAYKEY: Partial<Record<number, DayKey>> = {
  1: "lunes",
  2: "martes",
  3: "miércoles",
  4: "jueves",
  5: "viernes",
};

export default function ScheduleTodayPreview() {
  const { details } = useScheduleEvents();
  const today = useMemo(() => new Date(), []);
  const dayKey = WEEKDAY_TO_DAYKEY[today.getDay()];

  const friendlyDate = useMemo(
    () =>
      capitalize(
        new Intl.DateTimeFormat("es-CL", {
          weekday: "long",
          day: "numeric",
          month: "long",
        }).format(today),
      ),
    [today],
  );

  const todaysClasses = useMemo<ScheduleEventDetail[]>(() => {
    if (!dayKey) return [];
    return Object.values(details)
      .filter((detail) => detail.day === dayKey)
      .sort((a, b) => parseTimeToMinutes(a.startTime) - parseTimeToMinutes(b.startTime));
  }, [details, dayKey]);

  const hasSupportedDay = Boolean(dayKey);
  const hasClasses = todaysClasses.length > 0;

  return (
    <div className="space-y-4">
      <div className="rounded-3xl border border-[#004F9F1A] bg-[#004F9F0D] p-4">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#004F9FB3]">Hoy</p>
        <p className="text-lg font-semibold text-[#004F9F]">{friendlyDate}</p>
        <p className="text-sm text-[#004F9FB3]">
          {hasSupportedDay
            ? hasClasses
              ? `Tienes ${todaysClasses.length} ${todaysClasses.length === 1 ? "clase" : "clases"} programadas.`
              : "No tienes clases agendadas para hoy."
            : "No hay clases programadas para hoy."}
        </p>
      </div>

      <div className="space-y-3">
        {hasSupportedDay && hasClasses ? (
          todaysClasses.map((event) => (
            <article
              key={event.id}
              className="rounded-2xl border px-4 py-3 text-[#004F9F] shadow-sm"
              style={{ borderColor: event.color.border, backgroundColor: event.color.bg }}
            >
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-[#004F9FB3]">{event.section}</p>
                  <p className="text-base font-semibold">{event.code}</p>
                </div>
                <span className="text-sm font-semibold">
                  {event.startTime} - {event.endTime}
                </span>
              </div>
              <p className="mt-2 text-sm text-[#002B5C]">{event.title}</p>
              <p className="text-xs text-[#004F9FB3]">
                {event.location} · {event.modality}
              </p>
            </article>
          ))
        ) : (
          <div className="rounded-2xl border border-dashed border-[#004F9F33] p-4 text-center text-sm text-[#004F9FB3]">
            {hasSupportedDay ? "Aprovecha este tiempo libre." : "Disfruta tu fin de semana."}
          </div>
        )}
      </div>
    </div>
  );
}

function parseTimeToMinutes(value: string) {
  const [hours, minutes] = value.split(":").map((part) => parseInt(part, 10));
  if (Number.isNaN(hours) || Number.isNaN(minutes)) {
    return 0;
  }
  return hours * 60 + minutes;
}

const capitalize = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);
