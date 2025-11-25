from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from app.fet.schemas import (
    ActivityData,
    BuildingData,
    CalendarDay,
    CalendarHour,
    ConstraintBasicCompulsorySpace,
    ConstraintBasicCompulsoryTime,
    ConstraintMinDaysBetweenActivities,
    ConstraintTeacherNotAvailable,
    FetRunRequest,
    StudentGroup,
    StudentYear,
    TeacherData,
)


@dataclass
class _BuilderContext:
    payload: FetRunRequest
    teacher_lookup: Dict[str, TeacherData] = field(default_factory=dict)
    subject_lookup: Dict[str, str] = field(default_factory=dict)
    year_lookup: Dict[str, StudentYear] = field(default_factory=dict)
    group_lookup: Dict[str, StudentGroup] = field(default_factory=dict)
    group_year_lookup: Dict[str, StudentYear] = field(default_factory=dict)
    day_lookup: Dict[int, CalendarDay] = field(default_factory=dict)
    hour_lookup: Dict[int, CalendarHour] = field(default_factory=dict)
    building_lookup: Dict[str, BuildingData] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.teacher_lookup = {teacher.id: teacher for teacher in self.payload.teachers}
        self.subject_lookup = {subject.id: subject.name for subject in self.payload.subjects}
        self.year_lookup = {year.id: year for year in self.payload.student_years}
        for year in self.payload.student_years:
            for group in year.groups:
                self.group_lookup[group.id] = group
                self.group_year_lookup[group.id] = year
        self.day_lookup = {day.index: day for day in self.payload.calendar.days}
        self.hour_lookup = {hour.index: hour for hour in self.payload.calendar.hours}
        self.building_lookup = {building.id: building for building in self.payload.space.buildings}

    def teacher_name(self, teacher_id: str) -> str:
        teacher = self.teacher_lookup.get(teacher_id)
        return teacher.name if teacher else teacher_id

    def subject_name(self, subject_id: str) -> str:
        return self.subject_lookup.get(subject_id, subject_id)

    def students_label(self, reference_type: str, reference_id: str) -> str:
        if reference_type == "year":
            if reference_id in self.year_lookup:
                return reference_id
        elif reference_type == "group":
            if reference_id in self.group_lookup:
                return reference_id
        return reference_id

    def day_name(self, day_index: int) -> str:
        day = self.day_lookup.get(day_index)
        if day:
            return day.long_name or day.name
        return f"Día {day_index + 1}"

    def hour_name(self, hour_index: int) -> str:
        hour = self.hour_lookup.get(hour_index)
        if hour:
            return hour.long_name or hour.name
        return f"Bloque {hour_index + 1}"

    def room_building_name(self, building_id: Optional[str]) -> str:
        if building_id is None:
            return ""
        building = self.building_lookup.get(building_id)
        return building.name if building else building_id


class FetXmlBuilder:
    """Convierte el payload validado en un XML .fet compatible con FET."""

    fet_version = "6.0.0"

    def build(self, payload: FetRunRequest) -> str:
        context = _BuilderContext(payload=payload)
        root = Element("fet", attrib={"version": self.fet_version})

        metadata = payload.metadata
        self._add_text(root, "Mode", "Official")
        self._add_text(root, "Institution_Name", metadata.institution_name or "SGH")
        self._add_text(root, "Comments", metadata.comments or f"Generado automáticamente para {metadata.semester}")

        self._build_days_list(root, context)
        self._build_hours_list(root, context)
        self._build_students_list(root, context)
        self._build_teachers_list(root, context)
        self._build_subjects_list(root, context)
        self._build_activity_tags(root)
        self._build_activities(root, context)
        self._build_buildings_list(root, context)
        self._build_rooms_list(root, context)
        self._build_time_constraints(root, context)
        self._build_space_constraints(root, context)

        raw_xml = tostring(root, encoding="utf-8")
        parsed = minidom.parseString(raw_xml)
        return parsed.toprettyxml(indent="\t", encoding="UTF-8").decode("utf-8")

    def _add_text(self, parent: Element, tag: str, text: str) -> Element:
        node = SubElement(parent, tag)
        node.text = text
        return node

    def _build_days_list(self, root: Element, context: _BuilderContext) -> None:
        days_node = SubElement(root, "Days_List")
        days = sorted(context.payload.calendar.days, key=lambda day: day.index)
        if not days:
            days = [CalendarDay(index=i, name=f"Day {i+1}", long_name=f"Day {i+1}") for i in range(5)]
        SubElement(days_node, "Number_of_Days").text = str(len(days))
        for day in days:
            day_node = SubElement(days_node, "Day")
            SubElement(day_node, "Name").text = day.long_name or day.name

    def _build_hours_list(self, root: Element, context: _BuilderContext) -> None:
        hours_node = SubElement(root, "Hours_List")
        hours = sorted(context.payload.calendar.hours, key=lambda hour: hour.index)
        if not hours:
            hours = [
                CalendarHour(index=i, name=f"{8 + i:02d}:00", long_name=f"Bloque {i+1}")
                for i in range(5)
            ]
        SubElement(hours_node, "Number_of_Hours").text = str(len(hours))
        for hour in hours:
            hour_node = SubElement(hours_node, "Hour")
            SubElement(hour_node, "Name").text = hour.long_name or hour.name

    def _build_students_list(self, root: Element, context: _BuilderContext) -> None:
        students_node = SubElement(root, "Students_List")
        for year in context.payload.student_years:
            year_node = SubElement(students_node, "Year")
            SubElement(year_node, "Name").text = year.id
            SubElement(year_node, "Number_of_Students").text = str(year.total_students)
            SubElement(year_node, "Comments").text = year.name
            SubElement(year_node, "Number_of_Categories").text = "0"
            SubElement(year_node, "Separator").text = " "

            for group in year.groups:
                group_node = SubElement(year_node, "Group")
                SubElement(group_node, "Name").text = group.id
                SubElement(group_node, "Number_of_Students").text = str(group.students)
                SubElement(group_node, "Comments").text = group.name

                subgroup_node = SubElement(group_node, "Subgroup")
                SubElement(subgroup_node, "Name").text = f"{group.id}-sub"
                SubElement(subgroup_node, "Number_of_Students").text = str(group.students)
                SubElement(subgroup_node, "Comments").text = group.name

    def _build_teachers_list(self, root: Element, context: _BuilderContext) -> None:
        teachers_node = SubElement(root, "Teachers_List")
        for teacher in context.payload.teachers:
            teacher_node = SubElement(teachers_node, "Teacher")
            SubElement(teacher_node, "Name").text = teacher.name
            SubElement(teacher_node, "Target_Number_of_Hours").text = str(teacher.target_hours)
            SubElement(teacher_node, "Qualified_Subjects").text = ""
            SubElement(teacher_node, "Comments").text = teacher.comments or ""

    def _build_subjects_list(self, root: Element, context: _BuilderContext) -> None:
        subjects_node = SubElement(root, "Subjects_List")
        for subject in context.payload.subjects:
            subject_node = SubElement(subjects_node, "Subject")
            SubElement(subject_node, "Name").text = subject.name
            SubElement(subject_node, "Code").text = subject.code
            SubElement(subject_node, "Comments").text = subject.comments or ""

    def _build_activity_tags(self, root: Element) -> None:
        SubElement(root, "Activity_Tags_List")

    def _build_activities(self, root: Element, context: _BuilderContext) -> None:
        activities_node = SubElement(root, "Activities_List")
        for activity in context.payload.activities:
            self._append_activity(activities_node, activity, context)

    def _append_activity(self, activities_node: Element, activity: ActivityData, context: _BuilderContext) -> None:
        activity_node = SubElement(activities_node, "Activity")
        SubElement(activity_node, "Teacher").text = context.teacher_name(activity.teacher_id)
        SubElement(activity_node, "Subject").text = context.subject_name(activity.subject_id)
        SubElement(activity_node, "Students").text = context.students_label(
            activity.students_reference.type,
            activity.students_reference.id,
        )
        SubElement(activity_node, "Duration").text = str(activity.duration)
        SubElement(activity_node, "Total_Duration").text = str(activity.total_duration)
        SubElement(activity_node, "Id").text = str(activity.id)
        SubElement(activity_node, "Activity_Group_Id").text = str(activity.group_id)
        SubElement(activity_node, "Active").text = "true" if activity.active else "false"
        SubElement(activity_node, "Comments").text = activity.comments or ""

    def _build_buildings_list(self, root: Element, context: _BuilderContext) -> None:
        buildings_node = SubElement(root, "Buildings_List")
        for building in context.payload.space.buildings:
            building_node = SubElement(buildings_node, "Building")
            SubElement(building_node, "Name").text = building.name
            SubElement(building_node, "Short_Name").text = building.name[:10]
            SubElement(building_node, "Comments").text = building.comments or ""

    def _build_rooms_list(self, root: Element, context: _BuilderContext) -> None:
        rooms_node = SubElement(root, "Rooms_List")
        for room in context.payload.space.rooms:
            room_node = SubElement(rooms_node, "Room")
            SubElement(room_node, "Name").text = room.name
            SubElement(room_node, "Long_Name").text = room.name
            SubElement(room_node, "Code").text = room.id
            SubElement(room_node, "Building").text = context.room_building_name(room.building_id)
            SubElement(room_node, "Capacity").text = str(room.capacity or 0)
            SubElement(room_node, "Virtual").text = "false"
            SubElement(room_node, "Comments").text = room.comments or ""

    def _build_time_constraints(self, root: Element, context: _BuilderContext) -> None:
        constraints_node = SubElement(root, "Time_Constraints_List")
        if not context.payload.time_constraints:
            self._add_basic_compulsory_time(constraints_node, ConstraintBasicCompulsoryTime(type="basic_compulsory_time", weight=100.0))
            return

        for constraint in context.payload.time_constraints:
            if isinstance(constraint, ConstraintBasicCompulsoryTime):
                self._add_basic_compulsory_time(constraints_node, constraint)
            elif isinstance(constraint, ConstraintMinDaysBetweenActivities):
                self._add_min_days_constraint(constraints_node, constraint)
            elif isinstance(constraint, ConstraintTeacherNotAvailable):
                self._add_teacher_not_available(constraints_node, constraint, context)

    def _build_space_constraints(self, root: Element, context: _BuilderContext) -> None:
        constraints_node = SubElement(root, "Space_Constraints_List")
        if not context.payload.space.space_constraints:
            self._add_basic_compulsory_space(constraints_node, ConstraintBasicCompulsorySpace(type="basic_compulsory_space", weight=100.0))
            return

        for constraint in context.payload.space.space_constraints:
            if isinstance(constraint, ConstraintBasicCompulsorySpace):
                self._add_basic_compulsory_space(constraints_node, constraint)

    def _add_basic_compulsory_time(
        self,
        constraints_node: Element,
        constraint: ConstraintBasicCompulsoryTime,
    ) -> None:
        node = SubElement(constraints_node, "ConstraintBasicCompulsoryTime")
        SubElement(node, "Weight_Percentage").text = str(constraint.weight)
        SubElement(node, "Active").text = "true" if constraint.active else "false"
        SubElement(node, "Comments").text = ""

    def _add_min_days_constraint(
        self,
        constraints_node: Element,
        constraint: ConstraintMinDaysBetweenActivities,
    ) -> None:
        node = SubElement(constraints_node, "ConstraintMinDaysBetweenActivities")
        SubElement(node, "Weight_Percentage").text = str(constraint.weight)
        SubElement(node, "Consecutive_If_Same_Day").text = "true" if constraint.consecutive_if_same_day else "false"
        SubElement(node, "Number_of_Activities").text = str(len(constraint.activity_ids))
        for activity_id in constraint.activity_ids:
            SubElement(node, "Activity_Id").text = str(activity_id)
        SubElement(node, "MinDays").text = str(constraint.min_days)
        SubElement(node, "Active").text = "true" if constraint.active else "false"
        SubElement(node, "Comments").text = ""

    def _add_teacher_not_available(
        self,
        constraints_node: Element,
        constraint: ConstraintTeacherNotAvailable,
        context: _BuilderContext,
    ) -> None:
        node = SubElement(constraints_node, "ConstraintTeacherNotAvailableTimes")
        SubElement(node, "Weight_Percentage").text = str(constraint.weight)
        SubElement(node, "Teacher").text = context.teacher_name(constraint.teacher_id)
        SubElement(node, "Number_of_Not_Available_Times").text = str(len(constraint.not_available_slots))

        for slot in constraint.not_available_slots:
            slot_node = SubElement(node, "Not_Available_Time")
            SubElement(slot_node, "Day").text = context.day_name(slot.day_index)
            SubElement(slot_node, "Hour").text = context.hour_name(slot.hour_index)

        SubElement(node, "Active").text = "true" if constraint.active else "false"
        SubElement(node, "Comments").text = ""

    def _add_basic_compulsory_space(
        self,
        constraints_node: Element,
        constraint: ConstraintBasicCompulsorySpace,
    ) -> None:
        node = SubElement(constraints_node, "ConstraintBasicCompulsorySpace")
        SubElement(node, "Weight_Percentage").text = str(constraint.weight)
        SubElement(node, "Active").text = "true" if constraint.active else "false"
        SubElement(node, "Comments").text = ""


__all__ = ["FetXmlBuilder"]
