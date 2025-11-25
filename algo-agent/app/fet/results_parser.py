from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from xml.etree import ElementTree as ET

from app.fet.schemas import (
    ActivityData,
    ActivityScheduleEntry,
    BuildingData,
    CalendarConfig,
    CalendarDay,
    CalendarHour,
    FetRunRequest,
    RoomData,
    RoomSummary,
    StudentYear,
)


@dataclass
class _ActivityMetadata:
    subject: str
    duration: int
    students_count: int


class TimetableResultsParser:
    """Ayudas para interpretar los resultados de FET y mapearlos a datos de negocio."""

    timetable_folder_name = "timetables"

    def extract_summary(
        self,
        payload: FetRunRequest,
        workdir: Path,
        input_file: Path,
    ) -> Tuple[List[ActivityScheduleEntry], List[RoomSummary]]:
        timetable_dir = self._resolve_timetable_dir(workdir, input_file.stem)
        activities = self._parse_activities_file(payload, timetable_dir)
        rooms = self._build_rooms_summary(payload.space.rooms, payload.space.buildings)
        return activities, rooms

    def _resolve_timetable_dir(self, workdir: Path, stem: str) -> Optional[Path]:
        base_dir = workdir / self.timetable_folder_name
        if not base_dir.exists():
            return None

        candidates = [
            directory
            for directory in base_dir.iterdir()
            if directory.is_dir() and directory.name.startswith(stem)
        ]
        if not candidates:
            return None

        return max(candidates, key=lambda path: path.stat().st_mtime)

    def _parse_activities_file(
        self,
        payload: FetRunRequest,
        timetable_dir: Optional[Path],
    ) -> List[ActivityScheduleEntry]:
        if not timetable_dir:
            return []

        xml_file = self._find_activities_file(timetable_dir)
        if not xml_file or not xml_file.exists():
            return []

        hours_per_day, day_lookup, hour_lookup = self._build_calendar_mappings(payload.calendar)
        if hours_per_day <= 0:
            return []

        metadata_lookup = self._build_activity_metadata(payload)

        try:
            tree = ET.parse(xml_file)
        except ET.ParseError:
            return []

        activity_entries: List[ActivityScheduleEntry] = []
        root = tree.getroot()
        for activity_node in root.findall("Activity"):
            activity_id = (activity_node.findtext("Id") or "").strip()
            if not activity_id or activity_id not in metadata_lookup:
                continue

            day_name = (activity_node.findtext("Day") or "").strip().lower()
            hour_name = (activity_node.findtext("Hour") or "").strip().lower()
            if not day_name or not hour_name:
                continue

            day_index = day_lookup.get(day_name)
            hour_index = hour_lookup.get(hour_name)
            if day_index is None or hour_index is None:
                continue

            metadata = metadata_lookup[activity_id]
            slot_start = day_index * hours_per_day + hour_index
            time_slots = [slot_start + offset for offset in range(metadata.duration)]

            activity_entries.append(
                ActivityScheduleEntry(
                    id=self._coerce_activity_id(activity_id),
                    subject=metadata.subject,
                    time_slots=time_slots,
                    students_count=metadata.students_count,
                )
            )

        return activity_entries

    def _find_activities_file(self, timetable_dir: Path) -> Optional[Path]:
        matches = sorted(timetable_dir.glob("*_activities.xml"))
        return matches[0] if matches else None

    def _build_calendar_mappings(
        self,
        calendar: CalendarConfig,
    ) -> Tuple[int, Dict[str, int], Dict[str, int]]:
        effective_days = self._effective_days(calendar.days)
        effective_hours = self._effective_hours(calendar.hours)

        day_lookup = self._build_name_lookup(effective_days)
        hour_lookup = self._build_name_lookup(effective_hours)

        return len(effective_hours), day_lookup, hour_lookup

    def _effective_days(self, days: List[CalendarDay]) -> List[CalendarDay]:
        sorted_days = sorted(days, key=lambda day: day.index)
        if sorted_days:
            return sorted_days
        return [
            CalendarDay(index=i, name=f"Day {i + 1}", long_name=f"Day {i + 1}")
            for i in range(5)
        ]

    def _effective_hours(self, hours: List[CalendarHour]) -> List[CalendarHour]:
        sorted_hours = sorted(hours, key=lambda hour: hour.index)
        if sorted_hours:
            return sorted_hours
        return [
            CalendarHour(index=i, name=f"{8 + i:02d}:00", long_name=f"Bloque {i + 1}")
            for i in range(5)
        ]

    def _build_name_lookup(self, items: Iterable[CalendarDay | CalendarHour]) -> Dict[str, int]:
        lookup: Dict[str, int] = {}
        for ordinal, item in enumerate(items):
            for candidate in (item.long_name, item.name):
                if not candidate:
                    continue
                key = candidate.strip().lower()
                if key:
                    lookup[key] = ordinal
        return lookup

    def _build_activity_metadata(self, payload: FetRunRequest) -> Dict[str, _ActivityMetadata]:
        subject_lookup = {subject.id: subject.name for subject in payload.subjects}
        group_students = self._build_group_student_lookup(payload.student_years)
        year_students = {year.id: year.total_students for year in payload.student_years}

        metadata: Dict[str, _ActivityMetadata] = {}
        for activity in payload.activities:
            activity_id = activity.id.strip()
            if not activity_id:
                continue
            subject_name = subject_lookup.get(activity.subject_id, activity.subject_id)
            students_count = self._resolve_students_count(activity, group_students, year_students)
            metadata[activity_id] = _ActivityMetadata(
                subject=subject_name,
                duration=activity.duration,
                students_count=students_count,
            )
        return metadata

    def _build_group_student_lookup(self, years: List[StudentYear]) -> Dict[str, int]:
        lookup: Dict[str, int] = {}
        for year in years:
            for group in year.groups:
                lookup[group.id] = group.students
        return lookup

    def _resolve_students_count(
        self,
        activity: ActivityData,
        groups: Dict[str, int],
        years: Dict[str, int],
    ) -> int:
        reference = activity.students_reference
        if reference.type == "group":
            return groups.get(reference.id, 0)
        if reference.type == "year":
            return years.get(reference.id, 0)
        return 0

    def _build_rooms_summary(
        self,
        rooms: List[RoomData],
        buildings: List[BuildingData],
    ) -> List[RoomSummary]:
        building_names = {building.id: building.name for building in buildings}
        results: List[RoomSummary] = []
        for room in rooms:
            building_name = building_names.get(room.building_id or "", room.building_id or "")
            results.append(
                RoomSummary(
                    name=room.name,
                    capacity=room.capacity or 0,
                    building=building_name or "",
                )
            )
        return results

    def _coerce_activity_id(self, activity_id: str) -> int | str:
        normalized = activity_id.strip()
        if normalized.lstrip("-").isdigit():
            try:
                return int(normalized)
            except ValueError:
                return normalized
        return normalized


__all__ = ["TimetableResultsParser"]
