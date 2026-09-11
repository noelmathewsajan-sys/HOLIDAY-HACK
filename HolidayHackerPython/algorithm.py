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
        baseline_consecutive, (base_start, base_end) = self._longest_run_with_range(free)

        strategies: List[Strategy] = []

        # Iterate over all budgets from 1 to max_new_leaves
        for budget in range(1, max_new_leaves + 1):
            best_arr, win_start, win_end, win_len = self._find_best_allocation(free, n, budget)
            if win_len > 0:
                recommended = [base_cal[i].date for i in range(n) if best_arr[i] and not free[i]]
                actual_leaves = len(recommended)
                efficiency = float(win_len) if actual_leaves == 0 else (win_len / actual_leaves)

                sequence: List[CalendarDay] = []
                for i in range(win_start, win_end + 1):
                    orig = base_cal[i]
                    cd = CalendarDay(date=orig.date, status=orig.status, label=orig.label)
                    if not free[i] and best_arr[i]:
                        cd.status = DayStatus.RECOMMENDED_LEAVE
                        cd.label = "Recommended Leave"
                    sequence.append(cd)

                strategy = Strategy(
                    start_date=base_cal[win_start].date,
                    end_date=base_cal[win_end].date,
                    total_days=win_len,
                    leaves_needed=actual_leaves,
                    leave_dates=recommended,
                    sequence=sequence,
                    efficiency=efficiency
                )
                strategies.append(strategy)

        # Baseline zero-leave strategy
        if baseline_consecutive > 0:
            seq = [
                CalendarDay(date=base_cal[i].date, status=base_cal[i].status, label=base_cal[i].label)
                for i in range(base_start, base_end + 1)
            ]
            strategies.append(Strategy(
                start_date=base_cal[base_start].date,
                end_date=base_cal[base_end].date,
                total_days=baseline_consecutive,
                leaves_needed=0,
                leave_dates=[],
                sequence=seq,
                efficiency=float(baseline_consecutive)
            ))

        # Sort by efficiency descending, then consecutive days descending
        strategies.sort(key=lambda s: (s.efficiency, s.total_days), reverse=True)

        # Deduplicate: if multiple strategies yield the same consecutive days, keep the one needing fewest leaves
        deduped: List[Strategy] = []
        seen_consecutive = set()
        for s in strategies:
            if s.total_days not in seen_consecutive:
                seen_consecutive.add(s.total_days)
                deduped.append(s)

        return deduped

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
