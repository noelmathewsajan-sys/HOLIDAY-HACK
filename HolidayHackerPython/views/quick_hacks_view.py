import customtkinter as ctk
import calendar
from datetime import date, timedelta
from views.ui_constants import UIConstants
from algorithm import HolidayOptimizer
from models import HolidayPlan
from humor_utils import get_efficiency_label, get_random_success, get_random_failure
import tkinter.messagebox as messagebox
from services import UserService

class QuickHacksView(ctk.CTkFrame):
    def __init__(self, master, user, holiday_service, leave_service, plan_service, main_app):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.holiday_service = holiday_service
        self.leave_service = leave_service
        self.plan_service = plan_service
        self.main_app = main_app
        
        self.scope_var = ctk.StringVar(value="Current Month")
        self.budget_var = ctk.StringVar(value="All")
        self.sort_var = ctk.StringVar(value="Efficiency")
        
        self.build_ui()
        
    def _get_next_holiday_info(self, today):
        """Retrieve real-time status and upcoming holiday countdown."""
        all_holidays = self.holiday_service.get_all_holidays()
        upcoming = [h for h in all_holidays if h.holiday_date >= today]
        upcoming.sort(key=lambda h: h.holiday_date)

        is_weekend = today.weekday() >= 5
        today_h = next((h for h in all_holidays if h.holiday_date == today), None)
        if today_h:
            t_status = f"🎉 Today is {today_h.holiday_name}!"
        elif is_weekend:
            t_status = "🛌 Weekend (Day Off)"
        else:
            t_status = "💼 Working Day"

        if upcoming:
            next_h = upcoming[0]
            days_left = (next_h.holiday_date - today).days
            count_txt = "Today! 🎉" if days_left == 0 else ("Tomorrow! 🚀" if days_left == 1 else f"in {days_left} days")
            next_txt = f"Next Holiday: 🎉 {next_h.holiday_name} on {next_h.holiday_date.strftime('%d %b %Y')} ({count_txt})"
        else:
            next_txt = "No more upcoming holidays recorded this year."

        return t_status, next_txt

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(header, text="⚡ Quick Hacks — Real-Time Holiday Opportunities", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        title.pack(anchor="w")

        today = date.today()
        t_status, next_txt = self._get_next_holiday_info(today)

        # 1. Real-Time Date & Status Banner
        banner_frame = ctk.CTkFrame(header, fg_color=UIConstants.CARD_BG, corner_radius=10)
        banner_frame.pack(fill="x", pady=(6, 10))
        b_inner = ctk.CTkFrame(banner_frame, fg_color="transparent")
        b_inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(b_inner, text=f"📅 Today: {today.strftime('%A, %d %B %Y')} • {t_status}", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.SUCCESS).pack(side="left")
        ctk.CTkLabel(b_inner, text=next_txt, font=UIConstants.FONT_BODY, text_color=UIConstants.PRIMARY).pack(side="right")

        # 2. Controls Bar: Scope, Leave Budget, and Sorting
        controls_card = ctk.CTkFrame(header, fg_color=UIConstants.CARD_BG, corner_radius=10)
        controls_card.pack(fill="x", pady=(0, 10))
        c_inner = ctk.CTkFrame(controls_card, fg_color="transparent")
        c_inner.pack(fill="x", padx=14, pady=10)

        # Scope Selector (Current Month default!)
        ctk.CTkLabel(c_inner, text="📍 Scope:", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.PRIMARY).pack(side="left", padx=(0, 6))
        
        current_month_name = today.strftime("%B %Y")
        scope_options = [
            f"📍 This Month ({current_month_name})",
            "🚀 Next Month",
            "🗓️ Next 3 Months",
            "🌐 Full Year"
        ]
        self.scope_map = {
            scope_options[0]: "Current Month",
            scope_options[1]: "Next Month",
            scope_options[2]: "Next 3 Months",
            scope_options[3]: "Full Year"
        }
        self.scope_menu = ctk.CTkOptionMenu(
            c_inner, values=scope_options,
            command=self.on_scope_change,
            fg_color=UIConstants.SIDEBAR_BG, button_color=UIConstants.PRIMARY, button_hover_color=UIConstants.PRIMARY_HOVER,
            text_color=UIConstants.TEXT_PRIMARY, width=220
        )
        self.scope_menu.set(scope_options[0])
        self.scope_menu.pack(side="left", padx=(0, 16))

        # Budget Filter
        ctk.CTkLabel(c_inner, text="Leave Budget:", font=UIConstants.FONT_BODY_BOLD).pack(side="left", padx=(0, 6))
        budget_options = ["All Budgets", "0 Leaves (Free)", "1 Leave", "2 Leaves", "3 Leaves"]
        self.budget_map = {
            "All Budgets": "All",
            "0 Leaves (Free)": "0",
            "1 Leave": "1",
            "2 Leaves": "2",
            "3 Leaves": "3"
        }
        self.budget_menu = ctk.CTkOptionMenu(
            c_inner, values=budget_options,
            command=self.on_budget_change,
            fg_color=UIConstants.SIDEBAR_BG, button_color=UIConstants.CARD_BG, button_hover_color=UIConstants.PRIMARY_HOVER,
            width=140
        )
        self.budget_menu.set(budget_options[0])
        self.budget_menu.pack(side="left", padx=(0, 16))

        # Sort Menu
        ctk.CTkLabel(c_inner, text="Sort By:", font=UIConstants.FONT_BODY_BOLD).pack(side="left", padx=(0, 6))
        self.sort_menu = ctk.CTkOptionMenu(
            c_inner, values=["Efficiency", "Duration", "Chronological"],
            variable=self.sort_var, command=self.on_sort_change,
            fg_color=UIConstants.SIDEBAR_BG, button_color=UIConstants.CARD_BG, button_hover_color=UIConstants.PRIMARY_HOVER,
            width=130
        )
        self.sort_menu.pack(side="left")

        # 3. Active Scope & Count Summary Badge
        self.summary_bar = ctk.CTkFrame(header, fg_color="transparent")
        self.summary_bar.pack(fill="x", pady=(2, 0))
        self.summary_lbl = ctk.CTkLabel(self.summary_bar, text="", font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY)
        self.summary_lbl.pack(anchor="w")

        # Scrollable container for strategy cards
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)

        self.refresh_hacks()

    def on_scope_change(self, choice):
        self.scope_var.set(self.scope_map.get(choice, "Current Month"))
        self.refresh_hacks()

    def on_budget_change(self, choice):
        self.budget_var.set(self.budget_map.get(choice, "All"))
        self.refresh_hacks()

    def on_sort_change(self, choice):
        self.refresh_hacks()

    def _get_date_range_for_scope(self):
        today = date.today()
        scope = self.scope_var.get()

        if scope == "Current Month":
            _, last_day = calendar.monthrange(today.year, today.month)
            start_date = today
            # If month ends mid-week, bridge to adjacent weekend for complete hacks
            end_date = date(today.year, today.month, last_day)
            label = f"CURRENT MONTH ({today.strftime('%B %Y')}) from {start_date.strftime('%d %b')} to {end_date.strftime('%d %b %Y')}"
            return start_date, end_date, label

        elif scope == "Next Month":
            if today.month == 12:
                nm_year = today.year + 1
                nm_month = 1
            else:
                nm_year = today.year
                nm_month = today.month + 1
            _, last_day = calendar.monthrange(nm_year, nm_month)
            start_date = date(nm_year, nm_month, 1)
            end_date = date(nm_year, nm_month, last_day)
            label = f"NEXT MONTH ({start_date.strftime('%B %Y')}) from {start_date.strftime('%d %b')} to {end_date.strftime('%d %b %Y')}"
            return start_date, end_date, label

        elif scope == "Next 3 Months":
            start_date = today
            end_date = today + timedelta(days=90)
            label = f"NEXT 3 MONTHS from {start_date.strftime('%d %b')} to {end_date.strftime('%d %b %Y')}"
            return start_date, end_date, label

        else: # Full Year
            start_date = today
            end_date = today + timedelta(days=365)
            label = f"FULL YEAR from {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
            return start_date, end_date, label

    def refresh_hacks(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        start_date, end_date, scope_label = self._get_date_range_for_scope()

        holidays = self.holiday_service.get_holidays_in_range(start_date, end_date)
        user_leaves = self.leave_service.get_user_leaves_in_range(self.user.id, start_date, end_date)

        optimizer = HolidayOptimizer()
        # Find strategies with up to 3 leaves
        strategies = optimizer.find_best_strategies(start_date, end_date, holidays, user_leaves, 3)

        # Filter by budget
        b_filter = self.budget_var.get()
        if b_filter != "All":
            target_budget = int(b_filter)
            strategies = [s for s in strategies if s.leaves_needed == target_budget]

        # Sort
        sort_val = self.sort_var.get()
        if sort_val == "Chronological":
            strategies.sort(key=lambda s: s.start_date)
        elif sort_val == "Duration":
            strategies.sort(key=lambda s: s.total_days, reverse=True)
        else: # Efficiency
            strategies.sort(key=lambda s: (s.efficiency, s.total_days), reverse=True)

        # Update Summary Label
        self.summary_lbl.configure(text=f"🎯 Showing hacks for {scope_label} • {len(strategies)} viable deals found")

        if not strategies:
            msg = f"😭 {get_random_failure()}\nNo holiday deals matching this budget in the selected timeframe."
            ctk.CTkLabel(self.results_frame, text=msg, font=UIConstants.FONT_HEADING, text_color=UIConstants.DANGER).pack(pady=40)
            return

        for idx, strategy in enumerate(strategies):
            s_card = ctk.CTkFrame(self.results_frame, fg_color=UIConstants.CARD_BG, corner_radius=12)
            s_card.pack(fill="x", pady=8, padx=4)

            s_inner = ctk.CTkFrame(s_card, fg_color="transparent")
            s_inner.pack(fill="x", padx=20, pady=16)

            top_line = ctk.CTkFrame(s_inner, fg_color="transparent")
            top_line.pack(fill="x")

            title_text = f"🔥 Top Deal #{idx+1}" if idx < 3 else f"Deal #{idx+1}"
            title_color = UIConstants.WARNING if idx < 3 else UIConstants.TEXT_PRIMARY

            lbl = ctk.CTkLabel(
                top_line, text=f"{title_text}: {strategy.start_date.strftime('%b %d')} to {strategy.end_date.strftime('%b %d, %Y')}",
                font=UIConstants.FONT_BODY_BOLD, text_color=title_color
            )
            lbl.pack(side="left")

            badge = ctk.CTkLabel(
                top_line, text=get_efficiency_label(strategy.efficiency),
                font=UIConstants.FONT_SMALL, text_color=UIConstants.PRIMARY
            )
            badge.pack(side="right")

            days_lbl = ctk.CTkLabel(
                s_inner, text=f"{strategy.total_days} Consecutive Days Off",
                font=UIConstants.FONT_HEADING, text_color=UIConstants.SUCCESS
            )
            days_lbl.pack(anchor="w", pady=(6, 2))

            leaves_txt = "0 leaves needed (Free Long Weekend!)" if strategy.leaves_needed == 0 else f"Only takes {strategy.leaves_needed} leave{'s' if strategy.leaves_needed > 1 else ''}!"
            stats_line = f"{leaves_txt}  •  Efficiency: {strategy.efficiency:.1f}×  •  Available: {self.user.available_leaves} leaves"
            ctk.CTkLabel(s_inner, text=stats_line, font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 6))

            funny_quote = f"💬 {get_random_success()}"
            ctk.CTkLabel(s_inner, text=funny_quote, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.ACCENT).pack(anchor="w", pady=(0, 8))

            # Recommended leaves breakdown
            if strategy.leave_dates:
                ctk.CTkLabel(s_inner, text="📌 Take leave on:", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 2))
                rec_row = ctk.CTkFrame(s_inner, fg_color="transparent")
                rec_row.pack(anchor="w", pady=(0, 6))
                for d in strategy.leave_dates:
                    ctk.CTkLabel(rec_row, text=f"• {d.strftime('%b %d (%A)')}", font=UIConstants.FONT_SMALL, text_color=UIConstants.CAL_RECOMMENDED).pack(side="left", padx=(0, 12))

            # Visual timeline sequence preview
            if strategy.sequence:
                seq_frame = ctk.CTkFrame(s_inner, fg_color=UIConstants.SIDEBAR_BG, corner_radius=8)
                seq_frame.pack(fill="x", pady=(4, 10))
                seq_inner = ctk.CTkFrame(seq_frame, fg_color="transparent")
                seq_inner.pack(fill="x", padx=10, pady=6)

                for cd in strategy.sequence[:12]:
                    chip_color = UIConstants.CAL_RECOMMENDED if cd.status.name == "RECOMMENDED_LEAVE" else (UIConstants.CAL_HOLIDAY if cd.status.name == "PUBLIC_HOLIDAY" else UIConstants.CAL_WEEKEND)
                    chip = ctk.CTkFrame(seq_inner, fg_color=chip_color, corner_radius=4)
                    chip.pack(side="left", padx=3, pady=2)
                    c_txt = f"{cd.date.strftime('%d %b')}\n{cd.get_emoji()}"
                    ctk.CTkLabel(chip, text=c_txt, font=UIConstants.FONT_SMALL, text_color="#000" if chip_color != UIConstants.CAL_WEEKEND else "#FFF").pack(padx=6, pady=2)

                if len(strategy.sequence) > 12:
                    ctk.CTkLabel(seq_inner, text=f"+{len(strategy.sequence)-12} more days", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(side="left", padx=6)

            # Action Buttons
            row_btns = ctk.CTkFrame(s_inner, fg_color="transparent")
            row_btns.pack(anchor="e", pady=(4, 0))

            def save_this(strat=strategy):
                self.save_strategy_plan(strat)

            def view_this(strat=strategy):
                self.main_app.calendar_view.set_recommended_dates(strat.leave_dates, highlight_range=(strat.start_date, strat.end_date))
                self.main_app.calendar_view.current_year = strat.start_date.year
                self.main_app.calendar_view.current_month = strat.start_date.month
                self.main_app.calendar_view.refresh_grid()
                self.main_app.show_calendar()

            def book_leaves(strat=strategy):
                if strat.leaves_needed == 0:
                    messagebox.showinfo("Free Holiday", "This deal doesn't require any leaves! Enjoy your long weekend! 🎉")
                    return
                if self.user.available_leaves < strat.leaves_needed:
                    messagebox.showerror("Not Enough Leaves", f"You only have {self.user.available_leaves} leaves left, but this requires {strat.leaves_needed}.")
                    return
                try:
                    for d in strat.leave_dates:
                        self.leave_service.add_leave(self.user.id, d)
                    
                    self.user.available_leaves -= strat.leaves_needed
                    UserService().update_leaves(self.user.id, self.user.available_leaves)
                    
                    messagebox.showinfo("Success", f"Successfully booked {strat.leaves_needed} leaves! Your holiday is locked in! 🏖️")
                    self.refresh_hacks()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            ctk.CTkButton(row_btns, text="🎟️ Book Leaves", width=120, height=32, font=UIConstants.FONT_BODY_BOLD, fg_color=UIConstants.WARNING, text_color="#000", hover_color="#FFD700", command=book_leaves).pack(side="left", padx=5)
            ctk.CTkButton(row_btns, text="💾 Save Plan", width=100, height=32, font=UIConstants.FONT_BODY_BOLD, fg_color=UIConstants.SUCCESS, text_color="#000", hover_color="#00C853", command=save_this).pack(side="left", padx=5)
            ctk.CTkButton(row_btns, text="📅 View on Calendar", width=140, height=32, font=UIConstants.FONT_BODY_BOLD, fg_color=UIConstants.PRIMARY, text_color="#000", hover_color=UIConstants.PRIMARY_HOVER, command=view_this).pack(side="left", padx=5)

    def save_strategy_plan(self, strat):
        plan = HolidayPlan(
            id=0,
            user_id=self.user.id,
            plan_name=f"Quick Hack {strat.start_date.strftime('%b %d')} ({strat.total_days}d)",
            start_date=strat.start_date,
            end_date=strat.end_date,
            leaves_used=strat.leaves_needed,
            consecutive_days=strat.total_days,
            efficiency=strat.efficiency,
            recommended_dates=strat.leave_dates
        )
        self.plan_service.save_plan(plan)
        messagebox.showinfo("Saved", "Holiday Plan successfully saved! 🏖️")
