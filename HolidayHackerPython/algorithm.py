from datetime import date, timedelta
from typing import List, Set, Dict, Optional
from models import CalendarDay, DayStatus

class Strategy:
    def __init__(self, start_date: date, end_date: date, total_days: int, leaves_needed: int, 
                 leave_dates: List[date], sequence: Optional[List[CalendarDay]] = None, efficiency: Optional[float] = None):
        self.start_date = start_date
        self.end_date = end_date
        self.total_days = total_days
        self.leaves_needed = leaves_needed
        self.leave_dates = leave_dates
        self.sequence = sequence or []
        if efficiency is not None:
            self._efficiency = efficiency
        else:
            self._efficiency = float(total_days) if leaves_needed == 0 else (total_days / leaves_needed)

    def get_efficiency(self) -> float:
        return self._efficiency

    @property
    def efficiency(self) -> float:
        return self._efficiency

class HolidayOptimizer:
    def build_calendar(self, start: date, end: date, holidays: list, existing_leaves: list) -> List[CalendarDay]:
        holiday_map = {h.holiday_date: h.holiday_name for h in holidays}
        leave_dates = {l.leave_date for l in existing_leaves}

        calendar_days = []
        curr = start
        while curr <= end:
            cd = CalendarDay(date=curr)
            if curr.weekday() >= 5:
                cd.status = DayStatus.WEEKEND
                cd.label = "Weekend"
            elif curr in holiday_map:
                cd.status = DayStatus.PUBLIC_HOLIDAY
                cd.label = holiday_map[curr]
            elif curr in leave_dates:
                cd.status = DayStatus.EXISTING_LEAVE
                cd.label = "Existing Leave"
            else:
                cd.status = DayStatus.WORKING_DAY
                cd.label = None
            calendar_days.append(cd)
            curr += timedelta(days=1)
        return calendar_days

    def find_best_strategies(self, start: date, end: date, holidays: list, existing_leaves: list, max_new_leaves: int) -> List[Strategy]:
        base_cal = self.build_calendar(start, end, holidays, existing_leaves)
        n = len(base_cal)
        if n == 0:
            return []

        free = [day.is_day_off() for day in base_cal]
        strategies: List[Strategy] = []
        seen_ranges = set()

        # 1. Zero-leave baseline opportunities (any long weekend or holiday run >= 3 days)
        i = 0
        while i < n:
            if free[i]:
                j = i
                while j < n and free[j]:
                    j += 1
                length = j - i
                if length >= 3:
                    seq = [CalendarDay(date=base_cal[k].date, status=base_cal[k].status, label=base_cal[k].label) for k in range(i, j)]
                    key = (base_cal[i].date, base_cal[j-1].date)
                    if key not in seen_ranges:
                        seen_ranges.add(key)
                        strategies.append(Strategy(
                            start_date=base_cal[i].date,
                            end_date=base_cal[j-1].date,
                            total_days=length,
                            leaves_needed=0,
                            leave_dates=[],
                            sequence=seq,
                            efficiency=float(length)
                        ))
                i = j
            else:
                i += 1

        # 2. Comprehensive search for all high-efficiency windows around holidays
        for budget in range(1, max_new_leaves + 1):
            for left in range(n):
                work_count = 0
                for right in range(left, n):
                    if not free[right]:
                        work_count += 1
                    if work_count > budget:
                        break

                    # Window is maximal if it cannot be extended left or right without adding more leaves
                    is_max_left = (left == 0 or not free[left - 1])
                    is_max_right = (right == n - 1 or not free[right + 1])

                    if is_max_left and is_max_right and work_count > 0:
                        has_holiday = any(base_cal[k].status == DayStatus.PUBLIC_HOLIDAY for k in range(left, right + 1))
                        total_days = right - left + 1
                        if has_holiday and total_days >= budget + 2:
                            rec_dates = [base_cal[k].date for k in range(left, right + 1) if not free[k]]
                            actual_leaves = len(rec_dates)
                            key = (base_cal[left].date, base_cal[right].date)
                            if key not in seen_ranges and actual_leaves > 0:
                                seen_ranges.add(key)
                                seq = []
                                for k in range(left, right + 1):
                                    orig = base_cal[k]
                                    if not free[k]:
                                        seq.append(CalendarDay(date=orig.date, status=DayStatus.RECOMMENDED_LEAVE, label="Recommended Leave"))
                                    else:
                                        seq.append(CalendarDay(date=orig.date, status=orig.status, label=orig.label))

                                eff = total_days / actual_leaves
                                strategies.append(Strategy(
                                    start_date=base_cal[left].date,
                                    end_date=base_cal[right].date,
                                    total_days=total_days,
                                    leaves_needed=actual_leaves,
                                    leave_dates=rec_dates,
                                    sequence=seq,
                                    efficiency=eff
                                ))

        # 3. Also include the global best allocation for each budget if not already present
        for budget in range(1, max_new_leaves + 1):
            best_arr, win_start, win_end, win_len = self._find_best_allocation(free, n, budget)
            if win_len > 0:
                key = (base_cal[win_start].date, base_cal[win_end].date)
                if key not in seen_ranges:
                    recommended = [base_cal[i].date for i in range(n) if best_arr[i] and not free[i]]
                    actual_leaves = len(recommended)
                    if actual_leaves > 0:
                        seen_ranges.add(key)
                        sequence = []
                        for i in range(win_start, win_end + 1):
                            orig = base_cal[i]
                            cd = CalendarDay(date=orig.date, status=orig.status, label=orig.label)
                            if not free[i] and best_arr[i]:
                                cd.status = DayStatus.RECOMMENDED_LEAVE
                                cd.label = "Recommended Leave"
                            sequence.append(cd)

                        strategies.append(Strategy(
                            start_date=base_cal[win_start].date,
                            end_date=base_cal[win_end].date,
                            total_days=win_len,
                            leaves_needed=actual_leaves,
                            leave_dates=recommended,
                            sequence=sequence,
                            efficiency=win_len / actual_leaves
                        ))

        # Sort by efficiency descending, then total days descending
        strategies.sort(key=lambda s: (s.efficiency, s.total_days), reverse=True)
        return strategies

    def _find_best_allocation(self, free: List[bool], n: int, budget: int):
        best_len = 0
        best_left = 0
        left = 0
        work_count = 0

        for right in range(n):
            if not free[right]:
                work_count += 1

            while work_count > budget:
                if not free[left]:
                    work_count -= 1
                left += 1

            window_len = right - left + 1
            if window_len > best_len:
                best_len = window_len
                best_left = left

        best_right = min(n - 1, best_left + best_len - 1)
        res_arr = list(free)
        for i in range(best_left, best_right + 1):
            res_arr[i] = True

        return res_arr, best_left, best_right, best_len

    def _longest_run_with_range(self, arr: List[bool]):
        max_len = 0
        max_start = 0
        cur_start = 0
        cur_len = 0

        for i, val in enumerate(arr):
            if val:
                if cur_len == 0:
                    cur_start = i
                cur_len += 1
                if cur_len > max_len:
                    max_len = cur_len
                    max_start = cur_start
            else:
                cur_len = 0

        return max_len, (max_start, max_start + max_len - 1 if max_len > 0 else 0)
