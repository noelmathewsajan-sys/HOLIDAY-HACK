from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional
from enum import Enum

class DayStatus(Enum):
    WORKING_DAY = "Working Day"
    WEEKEND = "Weekend"
    PUBLIC_HOLIDAY = "Public Holiday"
    EXISTING_LEAVE = "Existing Leave"
    RECOMMENDED_LEAVE = "Recommended Leave"

@dataclass
class CalendarDay:
    date: date
    status: DayStatus = DayStatus.WORKING_DAY
    label: Optional[str] = None

    def is_day_off(self) -> bool:
        return self.status != DayStatus.WORKING_DAY

    def get_emoji(self) -> str:
        if self.status == DayStatus.WEEKEND:
            return "🛌"
        elif self.status == DayStatus.PUBLIC_HOLIDAY:
            return "🎉"
        elif self.status == DayStatus.RECOMMENDED_LEAVE:
            return "🏖️"
        elif self.status == DayStatus.EXISTING_LEAVE:
            return "🌴"
        return "💼"

    def get_status_text(self) -> str:
        return self.status.value

@dataclass
class User:
    id: int = 0
    name: str = ""
    email: str = ""
    role: str = "user"
    available_leaves: int = 10
    created_at: Optional[datetime] = None

@dataclass
class PublicHoliday:
    id: int
    holiday_name: str
    holiday_date: date
    description: Optional[str] = ""

@dataclass
class Leave:
    id: int
    user_id: int
    leave_date: date
    status: str = "approved"

@dataclass
class HolidayPlan:
    id: int
    user_id: int
    plan_name: str
    start_date: date
    end_date: date
    leaves_used: int
    consecutive_days: int
    efficiency: float
    recommended_dates: List[date] = field(default_factory=list)
    created_at: Optional[datetime] = None
