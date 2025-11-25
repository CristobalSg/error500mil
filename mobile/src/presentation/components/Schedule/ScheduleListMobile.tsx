import { useMemo, useState } from "react";
import { DIAS, DIA_LABELS, HORAS, type ScheduleEventDetailsMap, type ScheduleEventDetail } from "../../types/schedule";
import type { Events } from "../../types/schedule";

const HOUR_COLUMN_WIDTH = 20;
const ROW_HEIGHT = 44;

export default function ScheduleListMobile({ events, details }: { events: Events; details: ScheduleEventDetailsMap }) {
  const gridTemplateColumns = `repeat(${DIAS.length}, minmax(0, 1fr))`;
  const gridTemplateRows = `repeat(${HORAS.length}, ${ROW_HEIGHT}px)`;

  const positionedEvents = useMemo(() => buildPositionedEvents(events, details), [events, details]);
  const [selected, setSelected] = useState<ScheduleEventDetail | null>(null);

  return (
    <div className="overflow-hidden">
      <div className="w-full rounded-[26px] border border-[#004F9F1A] bg-gradient-to-b from-white via-[#F8FAFF] to-white p-4 shadow-[0_20px_60px_rgba(0,79,159,0.08)] sm:p-6">
        <div
          className="grid items-center gap-3 text-[9px] font-semibold uppercase tracking-[0.2em] text-[#004F9F99]"
          style={{ gridTemplateColumns: `${HOUR_COLUMN_WIDTH}px 1fr` }}
        >
          <div className="text-left tracking-[0.18em] text-[#004F9FCC]">Hora</div>
          <div className="grid" style={{ gridTemplateColumns }}>
            {DIAS.map((day) => (
              <div key={`head-${day}`} className="text-center">
                {DIA_LABELS[day]}
              </div>
            ))}
          </div>
        </div>

        <div className="mt-4 flex gap-2">
          <div
            className="grid text-[8px] font-semibold text-[#004F9F]"
            style={{ width: `${HOUR_COLUMN_WIDTH}px`, gridTemplateRows }}
          >
            {HORAS.map((hora) => {
              const [start] = hora.split(" - ");
              return (
                <div
                  key={`hour-${hora}`}
                  className="flex items-center justify-center text-center"
                >
                  <span>{start}</span>
                </div>
              );
            })}
          </div>

          <div className="relative flex-1">
            <div className="relative overflow-hidden rounded-[24px] border border-[#DCE4F4] bg-white">
              <div
                className="grid"
                style={{ gridTemplateColumns, gridTemplateRows }}
              >
                {HORAS.map((_, rowIdx) =>
                  DIAS.map((day, colIdx) => {
                    const isAlternateRow = rowIdx % 2 === 1;
                    const isLastColumn = colIdx === DIAS.length - 1;
                    const isLastRow = rowIdx === HORAS.length - 1;
                    return (
                      <div
                        key={`bg-${day}-${rowIdx}`}
                        className={`${isAlternateRow ? "bg-[#F5F7FB]" : "bg-white"} border-[#E3E9F5] ${
                          isLastColumn ? "" : "border-r"
                        } ${isLastRow ? "" : "border-b"}`}
                      />
                    );
                  }),
                )}
              </div>

              <div className="absolute inset-0 px-1 py-1">
                <div
                  className="grid h-full w-full"
                  style={{ gridTemplateColumns, gridTemplateRows }}
                >
                  {positionedEvents.map((card) => (
                    <div
                      key={card.key}
                      className="pointer-events-auto px-1 py-1"
                      style={{
                        gridColumnStart: card.columnStart,
                        gridRow: `${card.rowStart} / span ${card.rowSpan}`,
                      }}
                    >
                      <button
                        type="button"
                        onClick={() => setSelected(card.detail)}
                        className="flex h-full w-full flex-col justify-center rounded-[8px] border px-1 text-left text-[#004F9F] shadow-[0_8px_18px_rgba(0,0,0,0.08)]"
                        style={{
                          borderColor: card.detail.color.border,
                          backgroundColor: card.detail.color.bg,
                          boxShadow: `0 8px 18px ${card.detail.color.border}33`,
                        }}
                      >
                        <p className="text-[8px] font-semibold leading-tight break-words whitespace-normal">
                          {card.detail.code}
                        </p>
                        <p className="text-[7px] font-medium text-[#004F9FCC] break-words whitespace-normal">
                          {card.detail.location}
                        </p>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 px-4">
          <div className="relative w-full max-w-sm rounded-3xl bg-white p-6 shadow-2xl">
            <button
              type="button"
              className="absolute right-4 top-4 text-sm font-semibold text-[#004F9F]"
              onClick={() => setSelected(null)}
            >
              Cerrar
            </button>
            <div className="space-y-3">
              <div>
                <p
                  className="text-xs font-semibold uppercase tracking-[0.3em]"
                  style={{ color: selected.color.accent }}
                >
                  {selected.section}
                </p>
                <h3 className="text-lg font-bold text-[#004F9F]">{selected.code}</h3>
                <p className="text-sm font-medium text-[#004F9FCC]">{selected.title}</p>
              </div>
              <div className="space-y-2 text-sm text-[#002B5C]">
                <p><span className="font-semibold">Modalidad:</span> {selected.modality}</p>
                <p><span className="font-semibold">Campus:</span> {selected.campus}</p>
                <p><span className="font-semibold">UbicaciÃ³n:</span> {selected.location}</p>
                <p>
                  <span className="font-semibold">Horario:</span>{" "}
                  {capitalize(selected.day)} {selected.startTime} - {selected.endTime}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const capitalize = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);

interface PositionedEvent {
  key: string;
  columnStart: number;
  rowStart: number;
  rowSpan: number;
  detail: ScheduleEventDetail;
}

function buildPositionedEvents(events: Events, details: ScheduleEventDetailsMap): PositionedEvent[] {
  const positioned: PositionedEvent[] = [];

  DIAS.forEach((day, dayIdx) => {
    HORAS.forEach((hour, hourIdx) => {
      const slotEvents = events[day]?.[hour] ?? [];

      slotEvents.forEach((eventId, labelIdx) => {
        const detail = details[eventId];
        if (!detail) return;

        if (
          hourIdx > 0 &&
          (events[day]?.[HORAS[hourIdx - 1]] ?? []).includes(eventId)
        ) {
          return;
        }

        let span = 1;
        let nextIdx = hourIdx + 1;
        while (
          nextIdx < HORAS.length &&
          (events[day]?.[HORAS[nextIdx]] ?? []).includes(eventId)
        ) {
          span += 1;
          nextIdx += 1;
        }

        positioned.push({
          key: `${day}-${hourIdx}-${labelIdx}`,
          columnStart: dayIdx + 1,
          rowStart: hourIdx + 1,
          rowSpan: span,
          detail,
        });
      });
    });
  });

  return positioned;
}
