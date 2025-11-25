from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    timetable_id: str = Field(..., min_length=1)
    semester: str = Field(..., min_length=1)
    institution_name: Optional[str] = None
    comments: Optional[str] = None


class CalendarDay(BaseModel):
    index: int = Field(..., ge=0)
    name: str = Field(..., min_length=1)
    long_name: Optional[str] = None


class CalendarHour(BaseModel):
    index: int = Field(..., ge=0)
    name: str = Field(..., min_length=1)
    long_name: Optional[str] = None


class CalendarConfig(BaseModel):
    days: List[CalendarDay] = Field(default_factory=list)
    hours: List[CalendarHour] = Field(default_factory=list)


class SubjectData(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    comments: Optional[str] = None


class TeacherData(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    target_hours: int = 0
    comments: Optional[str] = None


class StudentGroup(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    students: int = Field(..., ge=0)


class StudentYear(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    total_students: int = Field(..., ge=0)
    groups: List[StudentGroup] = Field(default_factory=list)


class StudentsReference(BaseModel):
    type: Literal["year", "group"]
    id: str = Field(..., min_length=1)


class ActivityData(BaseModel):
    id: str = Field(..., min_length=1)
    group_id: str = Field(..., min_length=1)
    teacher_id: str = Field(..., min_length=1)
    subject_id: str = Field(..., min_length=1)
    students_reference: StudentsReference
    duration: int = Field(..., ge=1)
    total_duration: int = Field(..., ge=1)
    active: bool = True
    comments: Optional[str] = None


class NotAvailableSlot(BaseModel):
    day_index: int = Field(..., ge=0)
    hour_index: int = Field(..., ge=0)


class TimeConstraintBase(BaseModel):
    weight: float = Field(..., ge=0, le=100)
    active: bool = True


class ConstraintBasicCompulsoryTime(TimeConstraintBase):
    type: Literal["basic_compulsory_time"]


class ConstraintMinDaysBetweenActivities(TimeConstraintBase):
    type: Literal["min_days_between_activities"]
    min_days: int = Field(..., ge=0)
    activity_ids: List[str] = Field(default_factory=list)
    consecutive_if_same_day: bool = False


class ConstraintTeacherNotAvailable(TimeConstraintBase):
    type: Literal["teacher_not_available"]
    teacher_id: str = Field(..., min_length=1)
    not_available_slots: List[NotAvailableSlot] = Field(default_factory=list)


TimeConstraint = Union[
    ConstraintBasicCompulsoryTime,
    ConstraintMinDaysBetweenActivities,
    ConstraintTeacherNotAvailable,
]


class BuildingData(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    comments: Optional[str] = None


class RoomData(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    building_id: Optional[str] = None
    capacity: Optional[int] = None
    comments: Optional[str] = None


class SpaceConstraintBase(BaseModel):
    weight: float = Field(..., ge=0, le=100)
    active: bool = True


class ConstraintBasicCompulsorySpace(SpaceConstraintBase):
    type: Literal["basic_compulsory_space"]


SpaceConstraint = ConstraintBasicCompulsorySpace


class SpaceData(BaseModel):
    buildings: List[BuildingData] = Field(default_factory=list)
    rooms: List[RoomData] = Field(default_factory=list)
    space_constraints: List[SpaceConstraint] = Field(default_factory=list)


class FetRunRequest(BaseModel):
    metadata: Metadata
    calendar: CalendarConfig
    subjects: List[SubjectData] = Field(default_factory=list)
    teachers: List[TeacherData] = Field(default_factory=list)
    student_years: List[StudentYear] = Field(default_factory=list)
    activities: List[ActivityData] = Field(default_factory=list)
    time_constraints: List[TimeConstraint] = Field(default_factory=list)
    space: SpaceData = Field(default_factory=SpaceData)


class ActivityScheduleEntry(BaseModel):
    id: Union[int, str]
    subject: str
    time_slots: List[int] = Field(default_factory=list)
    students_count: int = 0


class RoomSummary(BaseModel):
    name: str
    capacity: int = 0
    building: str = ""


class FetRunSummary(BaseModel):
    status: str = Field(default="success")
    semester: str
    timetable_id: str
    fet_input_file: str
    output_directory: str
    stdout: str = ""
    stderr: str = ""
    activities_schedule: List[ActivityScheduleEntry] = Field(default_factory=list)
    rooms: List[RoomSummary] = Field(default_factory=list)


__all__ = [
    "Metadata",
    "CalendarConfig",
    "CalendarDay",
    "CalendarHour",
    "SubjectData",
    "TeacherData",
    "StudentYear",
    "StudentGroup",
    "StudentsReference",
    "ActivityData",
    "TimeConstraint",
    "ConstraintBasicCompulsoryTime",
    "ConstraintMinDaysBetweenActivities",
    "ConstraintTeacherNotAvailable",
    "SpaceData",
    "BuildingData",
    "RoomData",
    "SpaceConstraint",
    "ConstraintBasicCompulsorySpace",
    "FetRunRequest",
    "ActivityScheduleEntry",
    "RoomSummary",
    "FetRunSummary",
]
