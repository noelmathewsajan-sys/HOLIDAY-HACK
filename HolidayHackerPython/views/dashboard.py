import customtkinter as ctk
from datetime import date, timedelta
from views.ui_constants import UIConstants
from views.calendar_view import CalendarView
from views.hacker_view import HackerView
from views.plans_view import PlansView
from views.quick_hacks_view import QuickHacksView
from typing import Callable

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, user, holiday_service, leave_service, plan_service, auth_service, on_logout: Callable):
        super().__init__(master, fg_color=UIConstants.BG_COLOR)
        self.user = user
        self.holiday_service = holiday_service
        self.leave_service = leave_service
        self.plan_service = plan_service
        self.auth_service = auth_service
        self.on_logout = on_logout
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Build Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=UIConstants.SIDEBAR_BG)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # Brand
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🏖️ HOLIDAY HACKER", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 6), sticky="w")

        # User
        self.user_label = ctk.CTkLabel(self.sidebar_frame, text=f"👤 {self.user.name}", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY)
        self.user_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Nav Buttons list
        self.nav_buttons = {}
        items = [
            ("Calendar", "📅 Calendar", self.show_calendar),
            ("Find Holidays", "🔍 Find Holidays", self.show_hacker),
            ("Quick Hacks", "⚡ Quick Hacks", self.show_quick_hacks),
            ("Holiday Plans", "📋 Holiday Plans", self.show_plans),
        ]

        for idx, (key, label, cmd) in enumerate(items, start=2):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=label, command=cmd,
                fg_color="transparent", text_color=UIConstants.TEXT_PRIMARY,
                anchor="w", font=UIConstants.FONT_BODY, height=36
            )
            btn.grid(row=idx, column=0, pady=3, padx=14, sticky="ew")
            self.nav_buttons[key] = btn

        # Content Container
        self.content_frame = ctk.CTkFrame(self, fg_color=UIConstants.BG_COLOR)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Initialize subviews
        self.calendar_view = CalendarView(self.content_frame, self.user, self.holiday_service, self.leave_service)
        self.hacker_view = HackerView(self.content_frame, self.user, self.holiday_service, self.leave_service, self.plan_service, self)
        self.quick_hacks_view = QuickHacksView(self.content_frame, self.user, self.holiday_service, self.leave_service, self.plan_service, self)
        self.plans_view = PlansView(self.content_frame, self.user, self.plan_service, self)

        # Start with Calendar
        self.show_calendar()

    def _reset_btn_colors(self):
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent")

    def _hide_all(self):
        self.calendar_view.grid_forget()
        self.hacker_view.grid_forget()
        self.quick_hacks_view.grid_forget()
        self.plans_view.grid_forget()

    def show_calendar(self):
        self._reset_btn_colors()
        self.nav_buttons["Calendar"].configure(fg_color=UIConstants.CARD_BG)
        self._hide_all()
        self.calendar_view.refresh_grid()
        self.calendar_view.grid(row=0, column=0, sticky="nsew")

    def show_hacker(self):
        self._reset_btn_colors()
        self.nav_buttons["Find Holidays"].configure(fg_color=UIConstants.CARD_BG)
        self._hide_all()
        self.hacker_view.grid(row=0, column=0, sticky="nsew")

    def show_plans(self):
        self._reset_btn_colors()
        self.nav_buttons["Holiday Plans"].configure(fg_color=UIConstants.CARD_BG)
        self._hide_all()
        self.plans_view.refresh_plans()
        self.plans_view.grid(row=0, column=0, sticky="nsew")

    def show_quick_hacks(self):
        self._reset_btn_colors()
        self.nav_buttons["Quick Hacks"].configure(fg_color=UIConstants.CARD_BG)
        self._hide_all()
        self.quick_hacks_view.refresh_hacks()
        self.quick_hacks_view.grid(row=0, column=0, sticky="nsew")
