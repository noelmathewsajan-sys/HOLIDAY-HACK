import customtkinter as ctk
from datetime import date
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
        
        self.build_ui()
        
    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(header, text="⚡ Quick Hacks — Upcoming Best Holiday Deals", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        title.pack(anchor="w")
        
        today = date.today()
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

        banner_frame = ctk.CTkFrame(header, fg_color=UIConstants.CARD_BG, corner_radius=8)
        banner_frame.pack(fill="x", pady=(5, 10))
        b_inner = ctk.CTkFrame(banner_frame, fg_color="transparent")
        b_inner.pack(fill="x", padx=14, pady=8)

        ctk.CTkLabel(b_inner, text=f"📅 Today: {today.strftime('%A, %d %B %Y')} • {t_status}", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.SUCCESS).pack(side="left")
        ctk.CTkLabel(b_inner, text=next_txt, font=UIConstants.FONT_BODY, text_color=UIConstants.PRIMARY).pack(side="right")

        desc = ctk.CTkLabel(header, text="Automatically calculated upcoming holiday strategies starting from TODAY for the next 12 months (2 leaves or less).", font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY)
        desc.pack(anchor="w", pady=(0, 10))

        sort_frame = ctk.CTkFrame(header, fg_color="transparent")
        sort_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(sort_frame, text="Sort By:", font=UIConstants.FONT_BODY_BOLD).pack(side="left", padx=(0, 10))
        self.sort_var = ctk.StringVar(value="Efficiency")
        self.sort_menu = ctk.CTkOptionMenu(
            sort_frame, values=["Efficiency", "Chronological", "Duration"], 
            variable=self.sort_var, command=self.on_sort_change,
            fg_color=UIConstants.CARD_BG, button_color=UIConstants.SIDEBAR_BG, button_hover_color=UIConstants.PRIMARY_HOVER
        )
        self.sort_menu.pack(side="left")

        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)
        
    def on_sort_change(self, choice):
        self.refresh_hacks()

    def refresh_hacks(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        today = date.today()
        start_date = today
        end_date = today + timedelta(days=365)
        
        holidays = self.holiday_service.get_holidays_in_range(start_date, end_date)
        user_leaves = self.leave_service.get_user_leaves_in_range(self.user.id, start_date, end_date)

        optimizer = HolidayOptimizer()
        strategies = optimizer.find_best_strategies(start_date, end_date, holidays, user_leaves, 2)
        
        sort_val = self.sort_var.get()
        if sort_val == "Chronological":
            strategies.sort(key=lambda s: s.start_date)
        elif sort_val == "Duration":
            strategies.sort(key=lambda s: s.total_days, reverse=True)
        else: # Efficiency
            strategies.sort(key=lambda s: (s.efficiency, s.total_days), reverse=True)
        
        if not strategies:
            msg = f"😭 {get_random_failure()}"
            ctk.CTkLabel(self.results_frame, text=msg, font=UIConstants.FONT_HEADING, text_color=UIConstants.DANGER).pack(pady=40)
            return
            
        for idx, strategy in enumerate(strategies):
            s_card = ctk.CTkFrame(self.results_frame, fg_color=UIConstants.CARD_BG, corner_radius=12)
            s_card.pack(fill="x", pady=8, padx=5)

            s_inner = ctk.CTkFrame(s_card, fg_color="transparent")
            s_inner.pack(fill="x", padx=20, pady=16)

            top_line = ctk.CTkFrame(s_inner, fg_color="transparent")
            top_line.pack(fill="x")

            title_text = f"🔥 Best Deal #{idx+1}" if idx < 3 else f"Option #{idx+1}"
            title_color = UIConstants.WARNING if idx < 3 else UIConstants.TEXT_PRIMARY

            lbl = ctk.CTkLabel(
                top_line, text=f"{title_text}: {strategy.start_date.strftime('%b %d')} to {strategy.end_date.strftime('%b %d')}",
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
            days_lbl.pack(anchor="w", pady=(8, 2))

            stats_line = f"Only takes {strategy.leaves_needed} leaves!  •  Efficiency: {strategy.efficiency:.1f}×"
            ctk.CTkLabel(s_inner, text=stats_line, font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 5))
            
            funny_quote = f"💬 {get_random_success()}"
            ctk.CTkLabel(s_inner, text=funny_quote, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.ACCENT).pack(anchor="w", pady=(0, 10))

            if strategy.leave_dates:
                ctk.CTkLabel(s_inner, text="Take leave on:", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 2))
                for d in strategy.leave_dates:
                    ctk.CTkLabel(s_inner, text=f"• {d.strftime('%b %d (%A)')}", font=UIConstants.FONT_SMALL, text_color=UIConstants.CAL_RECOMMENDED).pack(anchor="w", padx=10)

            row_btns = ctk.CTkFrame(s_inner, fg_color="transparent")
            row_btns.pack(anchor="e", pady=(10, 0))

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
                    messagebox.showinfo("Free Holiday", "This deal doesn't require any leaves! Enjoy! 🎉")
                    return
                if self.user.available_leaves < strat.leaves_needed:
                    messagebox.showerror("Not Enough Leaves", f"You only have {self.user.available_leaves} leaves left, but this requires {strat.leaves_needed}.")
                    return
                try:
                    for d in strat.leave_dates:
                        self.leave_service.add_leave(self.user.id, d)
                    
                    self.user.available_leaves -= strat.leaves_needed
                    UserService().update_leaves(self.user.id, self.user.available_leaves)
                    
                    messagebox.showinfo("Success", f"Successfully booked {strat.leaves_needed} leaves! Your holiday is now locked in! 🏖️")
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
