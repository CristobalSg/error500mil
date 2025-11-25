import { useMemo } from "react";
import {
  DIAS,
  HORAS,
  type DayKey,
  type ScheduleEventDetailsMap,
  type ScheduleEventColor,
} from "../types/schedule";
import type { Events } from "../types/schedule";

interface ClassBlock {
  id: string;
  code: string;
  title: string;
  location: string;
  campus: string;
  modality: string;
  section: string;
  day: DayKey;
  startHour: number;
  startMinute: number;
  endHour: number;
  endMinute: number;
}

const CLASS_BLOCKS: ClassBlock[] = [
  {
    id: "DDO1031-WED-0800",
    code: "DDO1031",
    title: "Televisión Mas Media y Sociedad",
    location: "Sala Virtual",
    campus: "Campus Virtual",
    modality: "Online",
    section: "S2",
    day: "miércoles",
    startHour: 8,
    startMinute: 0,
    endHour: 10,
    endMinute: 10,
  },
  {
    id: "INFO1158-FRI-1130",
    code: "INFO1158",
    title: "Teoría de Grafos",
    location: "CJP08 · Sala 370",
    campus: "Campus San Juan Pablo II",
    modality: "Presencial",
    section: "S1",
    day: "viernes",
    startHour: 11,
    startMinute: 30,
    endHour: 14,
    endMinute: 50,
  },
  {
    id: "INFO1162-THU-0800",
    code: "INFO1162",
    title: "Planificación Estratégica",
    location: "CJP12 · Sala 160",
    campus: "Campus San Juan Pablo II",
    modality: "Presencial",
    section: "S1",
    day: "jueves",
    startHour: 8,
    startMinute: 0,
    endHour: 11,
    endMinute: 20,
  },
  {
    id: "INFO1164-THU-1020",
    code: "INFO1164",
    title: "Práctica Inicial",
    location: "Sala Virtual",
    campus: "Campus Virtual",
    modality: "Online",
    section: "S1",
    day: "jueves",
    startHour: 10,
    startMinute: 20,
    endHour: 11,
    endMinute: 20,
  },
  {
    id: "INFO1173-WED-1610",
    code: "INFO1173",
    title: "Taller de Integración IV",
    location: "CJP10 · Sala 165",
    campus: "Campus San Juan Pablo II",
    modality: "Presencial",
    section: "S1",
    day: "miércoles",
    startHour: 16,
    startMinute: 10,
    endHour: 18,
    endMinute: 20,
  },
  {
    id: "INFO1185-WED-1350",
    code: "INFO1185",
    title: "Inteligencia Artificial",
    location: "CJP10 · Sala 165",
    campus: "Campus San Juan Pablo II",
    modality: "Presencial",
    section: "S1",
    day: "miércoles",
    startHour: 13,
    startMinute: 50,
    endHour: 16,
    endMinute: 0,
  },
  {
    id: "INFO1185-THU-1130",
    code: "INFO1185",
    title: "Inteligencia Artificial",
    location: "CJP10 · Sala 205",
    campus: "Campus San Juan Pablo II",
    modality: "Presencial",
    section: "S1",
    day: "jueves",
    startHour: 11,
    startMinute: 30,
    endHour: 12,
    endMinute: 30,
  },
  {
    id: "INFO1188-MON-1130",
    code: "INFO1188",
    title: "Tópicos Avanzados de Desarrollo de Software I",
    location: "CJP07 · Lab Proyectos",
    campus: "Campus San Juan Pablo II",
    modality: "Presencial",
    section: "S1",
    day: "lunes",
    startHour: 11,
    startMinute: 30,
    endHour: 13,
    endMinute: 40,
  },
  {
    id: "INFO1188-WED-1130",
    code: "INFO1188",
    title: "Tópicos Avanzados de Desarrollo de Software I",
    location: "CJP07 · Lab Proyectos",
    campus: "Campus San Juan Pablo II",
    modality: "Presencial",
    section: "S1",
    day: "miércoles",
    startHour: 11,
    startMinute: 30,
    endHour: 13,
    endMinute: 40,
  },
  {
    id: "INFO1189-MON-1500",
    code: "INFO1189",
    title: "Tópicos Avanzados de Desarrollo de Software II",
    location: "CJP07 · Lab Proyectos",
    campus: "Campus San Juan Pablo II",
    modality: "Presencial",
    section: "S1",
    day: "lunes",
    startHour: 15,
    startMinute: 0,
    endHour: 17,
    endMinute: 10,
  },
  {
    id: "INFO1189-FRI-0800",
    code: "INFO1189",
    title: "Tópicos Avanzados de Desarrollo de Software II",
    location: "CJP03 · Sala 303",
    campus: "Campus San Juan Pablo II",
    modality: "Presencial",
    section: "S1",
    day: "viernes",
    startHour: 8,
    startMinute: 0,
    endHour: 10,
    endMinute: 10,
  },
];

const SLOT_START_HOUR = 8;
const COLOR_PALETTE: ScheduleEventColor[] = [
  { bg: "#FFF5E6", border: "#F6B756", accent: "#F6B756" },
  { bg: "#E6F4FF", border: "#5CA4F6", accent: "#2D6CD8" },
  { bg: "#F3E8FF", border: "#B48CFF", accent: "#7B48D3" },
  { bg: "#E7FFF5", border: "#35C38F", accent: "#1E8A62" },
  { bg: "#FFE8F2", border: "#FF7EB6", accent: "#E15B94" },
];

const previewEvents: Events = DIAS.reduce<Events>((acc, day) => {
  acc[day] = createEmptyDay();
  return acc;
}, {} as Events);
const detailMap: ScheduleEventDetailsMap = {};

CLASS_BLOCKS.forEach((block) => {
  const label = block.id;
  const daySlots = previewEvents[block.day];
  detailMap[block.id] = {
    id: block.id,
    code: block.code,
    title: block.title,
    location: block.location,
    campus: block.campus,
    modality: block.modality,
    section: block.section,
    day: block.day,
    startTime: formatTime(block.startHour, block.startMinute),
    endTime: formatTime(block.endHour, block.endMinute),
    color: getColorForCode(block.code),
  };

  HORAS.forEach((slot, slotIdx) => {
    const slotStart = SLOT_START_HOUR + slotIdx;
    const slotEnd = slotStart + 1;
    const eventStart = block.startHour + block.startMinute / 60;
    const eventEnd = block.endHour + block.endMinute / 60;

    if (eventStart < slotEnd && eventEnd > slotStart) {
      daySlots[slot].push(label);
    }
  });
});

export function useScheduleEvents() {
  const events = useMemo(() => previewEvents, []);
  const details = useMemo(() => detailMap, []);
  const allEventsCount = useMemo(() => Object.keys(detailMap).length, []);

  return { events, allEventsCount, details };
}

function createEmptyDay() {
  return HORAS.reduce<Record<string, string[]>>((acc, hour) => {
    acc[hour] = [];
    return acc;
  }, {});
}

function formatTime(hour: number, minute: number) {
  return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

function getColorForCode(code: string): ScheduleEventColor {
  const hash = [...code].reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return COLOR_PALETTE[hash % COLOR_PALETTE.length];
}