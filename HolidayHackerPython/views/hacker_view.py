import customtkinter as ctk
from datetime import datetime, date
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
        self.current_year = today.year
        self.current_month = today.month
        
        self.start_date = None
        self.end_date = None

        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(header, text="🔍 Find Holidays — Hack Your Calendar", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        title.pack(anchor="w")

        # Calendar Card
        self.cal_card = ctk.CTkFrame(self, fg_color=UIConstants.CARD_BG, corner_radius=12)
        self.cal_card.pack(fill="x", pady=(0, 15))
        
        # Calendar Header (prev/next)
        cal_nav = ctk.CTkFrame(self.cal_card, fg_color="transparent")
        cal_nav.pack(fill="x", pady=(15, 10), padx=20)
        
        ctk.CTkButton(cal_nav, text="◀", width=40, fg_color=UIConstants.BG_COLOR, hover_color=UIConstants.SIDEBAR_BG, command=self.prev_month).pack(side="left")
        self.month_label = ctk.CTkLabel(cal_nav, text="", font=UIConstants.FONT_HEADING, text_color=UIConstants.TEXT_PRIMARY)
        self.month_label.pack(side="left", expand=True)
        ctk.CTkButton(cal_nav, text="▶", width=40, fg_color=UIConstants.BG_COLOR, hover_color=UIConstants.SIDEBAR_BG, command=self.next_month).pack(side="right")
        
        self.cal_grid = ctk.CTkFrame(self.cal_card, fg_color="transparent")
        self.cal_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        # Selection info and action row
        action_card = ctk.CTkFrame(self, fg_color=UIConstants.CARD_BG, corner_radius=12)
        action_card.pack(fill="x", pady=(0, 15))
        
        a_inner = ctk.CTkFrame(action_card, fg_color="transparent")
        a_inner.pack(fill="x", padx=20, pady=15)
        
        self.sel_label = ctk.CTkLabel(a_inner, text="Select Start Date on the calendar above.", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.WARNING)
        self.sel_label.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))
        
        ctk.CTkLabel(a_inner, text="Available Leaves:", font=UIConstants.FONT_SMALL).grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.leaves_entry = ctk.CTkEntry(a_inner, width=100)
        self.leaves_entry.insert(0, str(self.user.available_leaves))
        self.leaves_entry.grid(row=1, column=1)
        
        hack_btn = ctk.CTkButton(
            a_inner, text="🔥 HACK MY CALENDAR", font=UIConstants.FONT_BODY_BOLD,
            fg_color=UIConstants.PRIMARY, text_color="#000", hover_color=UIConstants.PRIMARY_HOVER,
            command=self.run_hack
        )
        hack_btn.grid(row=1, column=2, padx=(20, 0))

        self.refresh_calendar()



        # Scrollable area for Hack Results
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_calendar()
        
    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_calendar()
        
    def select_date(self, d):
        if self.start_date and self.end_date:
            self.start_date = d
            self.end_date = None
        elif self.start_date and not self.end_date:
            if d < self.start_date:
                self.end_date = self.start_date
                self.start_date = d
            else:
                self.end_date = d
        else:
            self.start_date = d
            self.end_date = None
            
        if self.start_date and self.end_date:
            self.sel_label.configure(text=f"Range: {self.start_date} to {self.end_date}", text_color=UIConstants.SUCCESS)
        elif self.start_date:
            self.sel_label.configure(text=f"Start Date: {self.start_date}. Now select End Date.", text_color=UIConstants.PRIMARY)
        else:
            self.sel_label.configure(text="Select Start Date on the calendar above.", text_color=UIConstants.WARNING)
            
        self.refresh_calendar()

    def refresh_calendar(self):
        for widget in self.cal_grid.winfo_children():
            widget.destroy()
            
        month_name = calendar.month_name[self.current_month]
        self.month_label.configure(text=f"{month_name} {self.current_year}")
        
        for i in range(7):
            self.cal_grid.grid_columnconfigure(i, weight=1)
            
        days_of_week = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, dow in enumerate(days_of_week):
            lbl = ctk.CTkLabel(self.cal_grid, text=dow, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_SECONDARY)
            lbl.grid(row=0, column=i, pady=(0, 5))
            
        _, num_days = calendar.monthrange(self.current_year, self.current_month)
        first_date = date(self.current_year, self.current_month, 1)
        start_dow = first_date.weekday()
        
        row = 1
        col = start_dow
        
        for day in range(1, num_days + 1):
            curr_date = date(self.current_year, self.current_month, day)
            
            is_start = (curr_date == self.start_date)
            is_end = (curr_date == self.end_date)
            in_range = False
            if self.start_date and self.end_date and self.start_date <= curr_date <= self.end_date:
                in_range = True
                
            bg_color = UIConstants.CARD_BG
            text_color = UIConstants.TEXT_PRIMARY
            hover = UIConstants.CARD_BG_HOVER
            
            if is_start or is_end:
                bg_color = UIConstants.PRIMARY
                text_color = "#000000"
                hover = UIConstants.PRIMARY_HOVER
            elif in_range:
                bg_color = UIConstants.SECONDARY_HOVER
                
            btn = ctk.CTkButton(
                self.cal_grid, 
                text=str(day), 
                height=35,
                fg_color=bg_color,
                text_color=text_color,
                hover_color=hover,
                font=UIConstants.FONT_BODY,
                command=lambda d=curr_date: self.select_date(d)
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            
            col += 1
            if col > 6:
                col = 0
                row += 1

    def run_hack(self):
        if not self.start_date or not self.end_date:
            messagebox.showwarning("Range Error", "Please select both a Start Date and an End Date from the calendar.")
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

        # Huge consecutive days label
        days_lbl = ctk.CTkLabel(
            t_inner, text=f"{best_strat.total_days} CONSECUTIVE DAYS OFF",
            font=UIConstants.FONT_HUGE, text_color=UIConstants.SUCCESS
        )
        days_lbl.pack(anchor="w", pady=(8, 4))

        meta_txt = (
            f"From {best_strat.start_date} to {best_strat.end_date}   •   "
            f"Leaves Used: {best_strat.leaves_needed} / {self.user.available_leaves}   •   "
            f"Efficiency: {best_strat.efficiency:.1f}× ({get_efficiency_label(best_strat.efficiency)})"
        )
        ctk.CTkLabel(t_inner, text=meta_txt, font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 10))

        # Recommended leave days
        if best_strat.leave_dates:
            ctk.CTkLabel(t_inner, text="📌 Take Leave On:", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.WARNING).pack(anchor="w", pady=(4, 2))
            recs_frame = ctk.CTkFrame(t_inner, fg_color="transparent")
            recs_frame.pack(fill="x", pady=(0, 10))
            for d in best_strat.leave_dates:
                ctk.CTkLabel(recs_frame, text=f"• {d.strftime('%Y-%m-%d (%A)')}", font=UIConstants.FONT_SMALL, text_color=UIConstants.CAL_RECOMMENDED).pack(anchor="w", padx=10)

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

        # Random humor quote
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
                top_line, text=f"Option {idx+1}: {strategy.start_date} to {strategy.end_date}",
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
            plan_name=f"Break {strat.start_date} ({strat.total_days}d)",
            start_date=strat.start_date,
            end_date=strat.end_date,
            leaves_used=strat.leaves_needed,
            consecutive_days=strat.total_days,
            efficiency=strat.efficiency,
            recommended_dates=strat.leave_dates
        )
        self.plan_service.save_plan(plan)
        messagebox.showinfo("Saved", "Holiday Plan successfully saved! 🏖️")