import customtkinter as ctk
from datetime import datetime, date, timedelta
from views.ui_constants import UIConstants
from algorithm import HolidayOptimizer
from models import HolidayPlan
from humor_utils import get_efficiency_label, get_random_success, get_random_failure
import tkinter.messagebox as messagebox
import calendar

class HackerView(ctk.CTkFrame):
    def __init__(self, master, user, holiday_service, leave_service, plan_service, main_app):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.holiday_service = holiday_service
        self.leave_service = leave_service
        self.plan_service = plan_service
        self.main_app = main_app

        today = date.today()
        self.today = today
        
        # Default Start Date is Today
        self.start_date = today
        self.start_cal_year = today.year
        self.start_cal_month = today.month

        # Default End Date is Today + 30 days
        self.end_date = today + timedelta(days=30)
        self.end_cal_year = self.end_date.year
        self.end_cal_month = self.end_date.month

        self.build_ui()

    def _get_next_holiday_info(self):
        """Find the next upcoming public holiday relative to today."""
        today = self.today
        all_holidays = self.holiday_service.get_all_holidays()
        upcoming = [h for h in all_holidays if h.holiday_date >= today]
        upcoming.sort(key=lambda h: h.holiday_date)

        # Check today's status
        today_holiday = next((h for h in all_holidays if h.holiday_date == today), None)
        is_weekend = today.weekday() >= 5
        if today_holiday:
            today_status = f"🎉 Today is {today_holiday.holiday_name}!"
        elif is_weekend:
            today_status = "🛌 Weekend (Rest Day)"
        else:
            today_status = "💼 Working Day"

        if upcoming:
            next_h = upcoming[0]
            days_left = (next_h.holiday_date - today).days
            if days_left == 0:
                countdown = "Today! 🎉"
            elif days_left == 1:
                countdown = "Tomorrow! 🚀"
            else:
                countdown = f"in {days_left} days"
            next_txt = f"🎉 Next Holiday: {next_h.holiday_name} on {next_h.holiday_date.strftime('%d %b %Y')} ({countdown})"
        else:
            next_txt = "No more upcoming holidays recorded this year."

        return today_status, next_txt

    def build_ui(self):
        # 1. Header & Live Date Banner
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(header, text="🔍 Find Holidays — Dual Calendar Strategy Explorer", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        title.pack(anchor="w")

        today_status, next_h_txt = self._get_next_holiday_info()

        # Today & Next Holiday Banner
        banner_card = ctk.CTkFrame(self, fg_color=UIConstants.CARD_BG, corner_radius=10)
        banner_card.pack(fill="x", pady=(0, 12))

        b_inner = ctk.CTkFrame(banner_card, fg_color="transparent")
        b_inner.pack(fill="x", padx=16, pady=10)

        today_txt = f"📅 Today: {self.today.strftime('%A, %d %B %Y')}   •   {today_status}"
        ctk.CTkLabel(b_inner, text=today_txt, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.SUCCESS).pack(side="left")
        ctk.CTkLabel(b_inner, text=next_h_txt, font=UIConstants.FONT_BODY, text_color=UIConstants.PRIMARY).pack(side="right")

        # 2. TWO SEPARATE CALENDARS (SIDE BY SIDE)
        calendars_container = ctk.CTkFrame(self, fg_color="transparent")
        calendars_container.pack(fill="x", pady=(0, 12))
        calendars_container.grid_columnconfigure(0, weight=1)
        calendars_container.grid_columnconfigure(1, weight=1)

        # Left: START DATE CALENDAR
        self.start_card = ctk.CTkFrame(calendars_container, fg_color=UIConstants.CARD_BG, corner_radius=12)
        self.start_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        s_top = ctk.CTkFrame(self.start_card, fg_color="transparent")
        s_top.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(s_top, text="📅 START DATE CALENDAR", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.PRIMARY).pack(anchor="w")
        self.start_sel_lbl = ctk.CTkLabel(s_top, text="", font=UIConstants.FONT_SMALL, text_color=UIConstants.SUCCESS)
        self.start_sel_lbl.pack(anchor="w")

        s_nav = ctk.CTkFrame(self.start_card, fg_color="transparent")
        s_nav.pack(fill="x", padx=14, pady=(4, 6))
        ctk.CTkButton(s_nav, text="◀", width=34, height=28, fg_color=UIConstants.SIDEBAR_BG, hover_color=UIConstants.PRIMARY_HOVER, command=self.prev_start_month).pack(side="left")
        self.start_month_label = ctk.CTkLabel(s_nav, text="", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY)
        self.start_month_label.pack(side="left", expand=True)
        ctk.CTkButton(s_nav, text="▶", width=34, height=28, fg_color=UIConstants.SIDEBAR_BG, hover_color=UIConstants.PRIMARY_HOVER, command=self.next_start_month).pack(side="right")

        self.start_grid = ctk.CTkFrame(self.start_card, fg_color="transparent")
        self.start_grid.pack(fill="x", padx=14, pady=(0, 12))

        # Right: END DATE CALENDAR
        self.end_card = ctk.CTkFrame(calendars_container, fg_color=UIConstants.CARD_BG, corner_radius=12)
        self.end_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        e_top = ctk.CTkFrame(self.end_card, fg_color="transparent")
        e_top.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(e_top, text="📅 END DATE CALENDAR", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.PRIMARY).pack(anchor="w")
        self.end_sel_lbl = ctk.CTkLabel(e_top, text="", font=UIConstants.FONT_SMALL, text_color=UIConstants.SUCCESS)
        self.end_sel_lbl.pack(anchor="w")

        e_nav = ctk.CTkFrame(self.end_card, fg_color="transparent")
        e_nav.pack(fill="x", padx=14, pady=(4, 6))
        ctk.CTkButton(e_nav, text="◀", width=34, height=28, fg_color=UIConstants.SIDEBAR_BG, hover_color=UIConstants.PRIMARY_HOVER, command=self.prev_end_month).pack(side="left")
        self.end_month_label = ctk.CTkLabel(e_nav, text="", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY)
        self.end_month_label.pack(side="left", expand=True)
        ctk.CTkButton(e_nav, text="▶", width=34, height=28, fg_color=UIConstants.SIDEBAR_BG, hover_color=UIConstants.PRIMARY_HOVER, command=self.next_end_month).pack(side="right")

        self.end_grid = ctk.CTkFrame(self.end_card, fg_color="transparent")
        self.end_grid.pack(fill="x", padx=14, pady=(0, 12))

        # 3. Action Bar / Hack Controls
        action_card = ctk.CTkFrame(self, fg_color=UIConstants.CARD_BG, corner_radius=12)
        action_card.pack(fill="x", pady=(0, 12))

        a_inner = ctk.CTkFrame(action_card, fg_color="transparent")
        a_inner.pack(fill="x", padx=16, pady=12)

        self.range_summary_lbl = ctk.CTkLabel(a_inner, text="", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.SUCCESS)
        self.range_summary_lbl.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        ctk.CTkLabel(a_inner, text="Available Leaves:", font=UIConstants.FONT_SMALL).grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.leaves_entry = ctk.CTkEntry(a_inner, width=80)
        self.leaves_entry.insert(0, str(self.user.available_leaves))
        self.leaves_entry.grid(row=1, column=1, sticky="w")

        hack_btn = ctk.CTkButton(
            a_inner, text="🔥 HACK MY CALENDAR", font=UIConstants.FONT_BODY_BOLD,
            fg_color=UIConstants.PRIMARY, text_color="#000", hover_color=UIConstants.PRIMARY_HOVER,
            command=self.run_hack, height=36
        )
        hack_btn.grid(row=1, column=2, padx=(20, 0))

        # Refresh both calendars
        self.refresh_start_calendar()
        self.refresh_end_calendar()
        self.update_summary_labels()

        # Scrollable area for Hack Results
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)

    def update_summary_labels(self):
        """Update the selected date text and range duration."""
        if self.start_date:
            self.start_sel_lbl.configure(text=f"Selected: {self.start_date.strftime('%d %b %Y (%A)')}")
        if self.end_date:
            self.end_sel_lbl.configure(text=f"Selected: {self.end_date.strftime('%d %b %Y (%A)')}")

        if self.start_date and self.end_date:
            if self.start_date <= self.end_date:
                days = (self.end_date - self.start_date).days + 1
                self.range_summary_lbl.configure(
                    text=f"🚀 Selected Range: {self.start_date.strftime('%d %b %Y')} ➔ {self.end_date.strftime('%d %b %Y')} ({days} Days Total)",
                    text_color=UIConstants.SUCCESS
                )
            else:
                self.range_summary_lbl.configure(
                    text="⚠️ Warning: Start Date is after End Date. Please adjust End Date.",
                    text_color=UIConstants.DANGER
                )

    # Start Date Navigation
    def prev_start_month(self):
        if self.start_cal_month == 1:
            self.start_cal_month = 12
            self.start_cal_year -= 1
        else:
            self.start_cal_month -= 1
        self.refresh_start_calendar()

    def next_start_month(self):
        if self.start_cal_month == 12:
            self.start_cal_month = 1
            self.start_cal_year += 1
        else:
            self.start_cal_month += 1
        self.refresh_start_calendar()

    # End Date Navigation
    def prev_end_month(self):
        if self.end_cal_month == 1:
            self.end_cal_month = 12
            self.end_cal_year -= 1
        else:
            self.end_cal_month -= 1
        self.refresh_end_calendar()

    def next_end_month(self):
        if self.end_cal_month == 12:
            self.end_cal_month = 1
            self.end_cal_year += 1
        else:
            self.end_cal_month += 1
        self.refresh_end_calendar()

    def select_start_date(self, d):
        self.start_date = d
        self.update_summary_labels()
        self.refresh_start_calendar()
        self.refresh_end_calendar()

    def select_end_date(self, d):
        self.end_date = d
        self.update_summary_labels()
        self.refresh_start_calendar()
        self.refresh_end_calendar()

    def refresh_start_calendar(self):
        """Render the Start Date calendar month grid."""
        for widget in self.start_grid.winfo_children():
            widget.destroy()

        month_name = calendar.month_name[self.start_cal_month]
        self.start_month_label.configure(text=f"{month_name} {self.start_cal_year}")

        for i in range(7):
            self.start_grid.grid_columnconfigure(i, weight=1)

        days_of_week = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, dow in enumerate(days_of_week):
            lbl = ctk.CTkLabel(self.start_grid, text=dow, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY)
            lbl.grid(row=0, column=i, pady=(0, 2))

        _, num_days = calendar.monthrange(self.start_cal_year, self.start_cal_month)
        first_date = date(self.start_cal_year, self.start_cal_month, 1)
        start_dow = first_date.weekday()

        row = 1
        col = start_dow

        for day in range(1, num_days + 1):
            curr_date = date(self.start_cal_year, self.start_cal_month, day)
            is_start = (curr_date == self.start_date)
            is_today = (curr_date == self.today)
            in_range = (self.start_date and self.end_date and self.start_date <= curr_date <= self.end_date)

            bg_color = UIConstants.CARD_BG
            text_color = UIConstants.TEXT_PRIMARY
            hover = UIConstants.CARD_BG_HOVER

            if is_start:
                bg_color = UIConstants.PRIMARY
                text_color = "#000000"
                hover = UIConstants.PRIMARY_HOVER
            elif in_range:
                bg_color = UIConstants.SECONDARY_HOVER
            elif is_today:
                bg_color = "#1e2840"

            btn_text = f"{day}*" if (is_today and not is_start) else str(day)

            btn = ctk.CTkButton(
                self.start_grid, text=btn_text, height=28,
                fg_color=bg_color, text_color=text_color, hover_color=hover,
                font=UIConstants.FONT_SMALL,
                command=lambda d=curr_date: self.select_start_date(d)
            )
            btn.grid(row=row, column=col, padx=1, pady=1, sticky="ew")

            col += 1
            if col > 6:
                col = 0
                row += 1

    def refresh_end_calendar(self):
        """Render the End Date calendar month grid."""
        for widget in self.end_grid.winfo_children():
            widget.destroy()

        month_name = calendar.month_name[self.end_cal_month]
        self.end_month_label.configure(text=f"{month_name} {self.end_cal_year}")

        for i in range(7):
            self.end_grid.grid_columnconfigure(i, weight=1)

        days_of_week = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, dow in enumerate(days_of_week):
            lbl = ctk.CTkLabel(self.end_grid, text=dow, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY)
            lbl.grid(row=0, column=i, pady=(0, 2))

        _, num_days = calendar.monthrange(self.end_cal_year, self.end_cal_month)
        first_date = date(self.end_cal_year, self.end_cal_month, 1)
        start_dow = first_date.weekday()

        row = 1
        col = start_dow

        for day in range(1, num_days + 1):
            curr_date = date(self.end_cal_year, self.end_cal_month, day)
            is_end = (curr_date == self.end_date)
            is_today = (curr_date == self.today)
            in_range = (self.start_date and self.end_date and self.start_date <= curr_date <= self.end_date)

            bg_color = UIConstants.CARD_BG
            text_color = UIConstants.TEXT_PRIMARY
            hover = UIConstants.CARD_BG_HOVER

            if is_end:
                bg_color = UIConstants.PRIMARY
                text_color = "#000000"
                hover = UIConstants.PRIMARY_HOVER
            elif in_range:
                bg_color = UIConstants.SECONDARY_HOVER
            elif is_today:
                bg_color = "#1e2840"

            btn_text = f"{day}*" if (is_today and not is_end) else str(day)

            btn = ctk.CTkButton(
                self.end_grid, text=btn_text, height=28,
                fg_color=bg_color, text_color=text_color, hover_color=hover,
                font=UIConstants.FONT_SMALL,
                command=lambda d=curr_date: self.select_end_date(d)
            )
            btn.grid(row=row, column=col, padx=1, pady=1, sticky="ew")

            col += 1
            if col > 6:
                col = 0
                row += 1

    def run_hack(self):
        if not self.start_date or not self.end_date:
            messagebox.showwarning("Range Error", "Please select both a Start Date and an End Date using the separate calendars.")
            return

        if self.start_date > self.end_date:
            messagebox.showerror("Invalid Range", "Start Date must be before or equal to End Date.")
            return

        start_date = self.start_date
        end_date = self.end_date
        
        try:
            leaves = int(self.leaves_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid leaves input. Must be a number.")
            return

        self.user.available_leaves = leaves

        holidays = self.holiday_service.get_holidays_in_range(start_date, end_date)
        user_leaves = self.leave_service.get_user_leaves_in_range(self.user.id, start_date, end_date)

        optimizer = HolidayOptimizer()
        strategies = optimizer.find_best_strategies(start_date, end_date, holidays, user_leaves, leaves)

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not strategies:
            msg = f"😭 {get_random_failure()}"
            ctk.CTkLabel(self.results_frame, text=msg, font=UIConstants.FONT_HEADING, text_color=UIConstants.DANGER).pack(pady=40)
            return

        # Best strategy (highest efficiency among those using leaves, or fallback to first)
        paid_strategies = [s for s in strategies if s.leaves_needed > 0]
        best_strat = paid_strategies[0] if paid_strategies else strategies[0]

        # 1. Trophy Card for Best Hack
        trophy_card = ctk.CTkFrame(self.results_frame, fg_color=UIConstants.CARD_BG, corner_radius=14)
        trophy_card.pack(fill="x", pady=(0, 15))

        t_inner = ctk.CTkFrame(trophy_card, fg_color="transparent")
        t_inner.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(t_inner, text="🏆 BEST HOLIDAY HACK", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY).pack(anchor="w")

        # Consecutive days label
        days_lbl = ctk.CTkLabel(
            t_inner, text=f"{best_strat.total_days} CONSECUTIVE DAYS OFF",
            font=UIConstants.FONT_HUGE, text_color=UIConstants.SUCCESS
        )
        days_lbl.pack(anchor="w", pady=(8, 4))

        meta_txt = (
            f"From {best_strat.start_date.strftime('%d %b %Y')} to {best_strat.end_date.strftime('%d %b %Y')}   •   "
            f"Leaves Needed: {best_strat.leaves_needed} / {self.user.available_leaves}   •   "
            f"Efficiency: {best_strat.efficiency:.1f}× ({get_efficiency_label(best_strat.efficiency)})"
        )
        ctk.CTkLabel(t_inner, text=meta_txt, font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 10))

        # Recommended leave days
        if best_strat.leave_dates:
            ctk.CTkLabel(t_inner, text="📌 Take Leave On:", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.WARNING).pack(anchor="w", pady=(4, 2))
            recs_frame = ctk.CTkFrame(t_inner, fg_color="transparent")
            recs_frame.pack(fill="x", pady=(0, 10))
            for d in best_strat.leave_dates:
                ctk.CTkLabel(recs_frame, text=f"• {d.strftime('%d %b %Y (%A)')}", font=UIConstants.FONT_SMALL, text_color=UIConstants.CAL_RECOMMENDED).pack(anchor="w", padx=10)

        # Day sequence visual preview (up to 14 days)
        if best_strat.sequence:
            ctk.CTkLabel(t_inner, text="Break Sequence Preview:", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(6, 4))
            seq_frame = ctk.CTkFrame(t_inner, fg_color=UIConstants.SIDEBAR_BG, corner_radius=8)
            seq_frame.pack(fill="x", pady=(0, 12), padx=5)

            seq_grid = ctk.CTkFrame(seq_frame, fg_color="transparent")
            seq_grid.pack(fill="x", padx=10, pady=8)

            for i, cd in enumerate(best_strat.sequence[:14]):
                item_txt = f"{cd.get_emoji()} {cd.date.strftime('%b %d')} ({cd.get_status_text()})"
                color = UIConstants.CAL_RECOMMENDED if cd.status.name == "RECOMMENDED_LEAVE" else UIConstants.TEXT_PRIMARY
                ctk.CTkLabel(seq_grid, text=item_txt, font=UIConstants.FONT_SMALL, text_color=color).pack(anchor="w", pady=1)

            if len(best_strat.sequence) > 14:
                ctk.CTkLabel(seq_grid, text=f"... and {len(best_strat.sequence) - 14} more days", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=1)

        # Humor quote
        quote_lbl = ctk.CTkLabel(t_inner, text=f"💬 {get_random_success()}", font=UIConstants.FONT_BODY, text_color=UIConstants.ACCENT)
        quote_lbl.pack(anchor="w", pady=(4, 14))

        # Save and calendar buttons for best hack
        action_row = ctk.CTkFrame(t_inner, fg_color="transparent")
        action_row.pack(fill="x")

        def save_best():
            self.save_strategy_plan(best_strat)

        save_btn = ctk.CTkButton(
            action_row, text="💾 Save Plan", width=130,
            font=UIConstants.FONT_BODY_BOLD, fg_color=UIConstants.SUCCESS,
            text_color="#000", hover_color="#00C853", command=save_best
        )
        save_btn.pack(side="left", padx=(0, 10))

        def view_best_on_cal():
            self.main_app.calendar_view.set_recommended_dates(best_strat.leave_dates)
            self.main_app.show_calendar()

        cal_btn = ctk.CTkButton(
            action_row, text="📅 View on Calendar", width=150,
            font=UIConstants.FONT_BODY, fg_color=UIConstants.PRIMARY,
            text_color="#000", hover_color=UIConstants.PRIMARY_HOVER, command=view_best_on_cal
        )
        cal_btn.pack(side="left")

        # 2. Alternative Options Section
        ctk.CTkLabel(self.results_frame, text=f"All Ranked Options ({len(strategies)} Strategies Found):", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(10, 8))

        for idx, strategy in enumerate(strategies):
            s_card = ctk.CTkFrame(self.results_frame, fg_color=UIConstants.CARD_BG, corner_radius=10)
            s_card.pack(fill="x", pady=6)

            s_inner = ctk.CTkFrame(s_card, fg_color="transparent")
            s_inner.pack(fill="x", padx=16, pady=12)

            top_line = ctk.CTkFrame(s_inner, fg_color="transparent")
            top_line.pack(fill="x")

            lbl = ctk.CTkLabel(
                top_line, text=f"Option {idx+1}: {strategy.start_date.strftime('%d %b %Y')} to {strategy.end_date.strftime('%d %b %Y')}",
                font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY
            )
            lbl.pack(side="left")

            badge = ctk.CTkLabel(
                top_line, text=get_efficiency_label(strategy.efficiency),
                font=UIConstants.FONT_SMALL, text_color=UIConstants.PRIMARY
            )
            badge.pack(side="right")

            stats_line = (
                f"Takes {strategy.leaves_needed} leaves to get {strategy.total_days} consecutive days off  •  "
                f"Efficiency: {strategy.efficiency:.1f}×"
            )
            ctk.CTkLabel(s_inner, text=stats_line, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(4, 8))

            row_btns = ctk.CTkFrame(s_inner, fg_color="transparent")
            row_btns.pack(anchor="e")

            def save_this(strat=strategy):
                self.save_strategy_plan(strat)

            def view_this(strat=strategy):
                self.main_app.calendar_view.set_recommended_dates(strat.leave_dates)
                self.main_app.show_calendar()

            ctk.CTkButton(row_btns, text="💾 Save", width=80, height=28, font=UIConstants.FONT_SMALL, command=save_this).pack(side="left", padx=5)
            ctk.CTkButton(row_btns, text="📅 View", width=80, height=28, font=UIConstants.FONT_SMALL, fg_color=UIConstants.PRIMARY, text_color="#000", hover_color=UIConstants.PRIMARY_HOVER, command=view_this).pack(side="left", padx=5)

    def save_strategy_plan(self, strat):
        plan = HolidayPlan(
            id=0,
            user_id=self.user.id,
            plan_name=f"Break {strat.start_date.strftime('%d %b')} ({strat.total_days}d)",
            start_date=strat.start_date,
            end_date=strat.end_date,
            leaves_used=strat.leaves_needed,
            consecutive_days=strat.total_days,
            efficiency=strat.efficiency,
            recommended_dates=strat.leave_dates
        )
        self.plan_service.save_plan(plan)
        messagebox.showinfo("Saved", "Holiday Plan successfully saved! 🏖️")