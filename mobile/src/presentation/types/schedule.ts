export type DayKey = "lunes" | "martes" | "miércoles" | "jueves" | "viernes";

export interface Events {
  [day: string]: { [hour: string]: string[] };
}

export interface SlotRef {
  day: DayKey;
  hour: string;
}

export interface ScheduleEventDetail {
  id: string;
  code: string;
  title: string;
  location: string;
  campus: string;
  modality: string;
  section: string;
  day: DayKey;
  startTime: string;
  endTime: string;
  color: ScheduleEventColor;
}

export interface ScheduleEventColor {
  bg: string;
  border: string;
  accent: string;
}

export type ScheduleEventDetailsMap = Record<string, ScheduleEventDetail>;

export const DIAS: DayKey[] = ["lunes", "martes", "miércoles", "jueves", "viernes"];
export const DIA_LABELS: Record<DayKey, string> = {
  lunes: "L",
  martes: "M",
  miércoles: "X",
  jueves: "J",
  viernes: "V",
};

export const HORAS: string[] = [
  "08:00 - 09:00",
  "09:00 - 10:00",
  "10:00 - 11:00",
  "11:00 - 12:00",
  "12:00 - 13:00",
  "13:00 - 14:00",
  "14:00 - 15:00",
  "15:00 - 16:00",
  "16:00 - 17:00",
  "17:00 - 18:00",
  "18:00 - 19:00",
  "19:00 - 20:00",
];