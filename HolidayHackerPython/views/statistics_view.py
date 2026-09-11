import customtkinter as ctk
from datetime import date, timedelta
from views.ui_constants import UIConstants
from humor_utils import get_hacker_title, get_uselessness_meter

class StatisticsView(ctk.CTkFrame):
    def __init__(self, master, user, holiday_service, leave_service, plan_service):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.holiday_service = holiday_service
        self.leave_service = leave_service
        self.plan_service = plan_service

        self.build_ui()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(header, text="📈 Holiday Statistics", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        title.pack(side="left")

        # Scrollable container for stats
        scroll_content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_content.pack(fill="both", expand=True)

        # Compute stats
        today = date.today()
        year = today.year
        start_year = date(year, 1, 1)
        end_year = date(year, 12, 31)

        # Count weekends in year
        weekends_count = 0
        curr = start_year
        while curr <= end_year:
            if curr.weekday() >= 5:
                weekends_count += 1
            curr += timedelta(days=1)

        total_holidays = self.holiday_service.get_holiday_count()
        avail_leaves = self.user.available_leaves
        used_leaves = self.leave_service.get_used_leave_count(self.user.id)
        plans = self.plan_service.get_user_plans(self.user.id)
        hacks_found = len(plans)

        longest_break = max([p.consecutive_days for p in plans], default=0)
        avg_break = (sum([p.consecutive_days for p in plans]) / len(plans)) if plans else 0.0
        best_eff = max([p.efficiency for p in plans], default=0.0)

        # 8 KPI Stat Cards in 2x4 Grid
        grid_frame = ctk.CTkFrame(scroll_content, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 20))

        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)

        stats_meta = [
            ("🎉 Public Holidays", str(total_holidays), UIConstants.WARNING),
            ("🛌 Total Weekends", str(weekends_count), UIConstants.SECONDARY),
            ("🌴 Available Leaves", str(avail_leaves), UIConstants.PRIMARY),
            ("✅ Leaves Used", str(used_leaves), UIConstants.DANGER),
            ("🏆 Longest Break", f"{longest_break} days" if longest_break > 0 else "—", UIConstants.SUCCESS),
            ("📊 Avg Break", f"{avg_break:.1f} days" if avg_break > 0 else "—", UIConstants.PRIMARY),
            ("⚡ Best Efficiency", f"{best_eff:.1f}×" if best_eff > 0 else "—", UIConstants.ACCENT),
            ("🔍 Hacks Found", str(hacks_found), UIConstants.SUCCESS),
        ]

        for idx, (label, val, accent) in enumerate(stats_meta):
            row = idx // 4
            col = idx % 4

            card = ctk.CTkFrame(grid_frame, fg_color=UIConstants.CARD_BG, corner_radius=12, height=95)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            card.grid_propagate(False)

            # Accent indicator bar at top
            bar = ctk.CTkFrame(card, fg_color=accent, height=4, corner_radius=2)
            bar.pack(fill="x", side="top")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=14, pady=10)

            ctk.CTkLabel(inner, text=label, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w")
            ctk.CTkLabel(inner, text=val, font=UIConstants.FONT_HEADING, text_color=accent).pack(anchor="w", pady=(4, 0))

        # Hacker Title Card
        title_card = ctk.CTkFrame(scroll_content, fg_color=UIConstants.CARD_BG, corner_radius=12)
        title_card.pack(fill="x", pady=(0, 15))

        t_inner = ctk.CTkFrame(title_card, fg_color="transparent")
        t_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(t_inner, text="Your Holiday Hacker Title:", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w")
        ctk.CTkLabel(t_inner, text=get_hacker_title(hacks_found), font=UIConstants.FONT_TITLE, text_color=UIConstants.PRIMARY).pack(anchor="w", pady=(2, 0))

        # Leave Breakdown Progress Bars Card
        chart_card = ctk.CTkFrame(scroll_content, fg_color=UIConstants.CARD_BG, corner_radius=12)
        chart_card.pack(fill="x", pady=(0, 15))

        c_inner = ctk.CTkFrame(chart_card, fg_color="transparent")
        c_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(c_inner, text="📊 Leave Breakdown", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 12))

        remaining_leaves = max(0, avail_leaves - used_leaves)
        breakdown_items = [
            ("Public Holidays", total_holidays, 30, UIConstants.WARNING),
            ("Weekends", weekends_count, 120, UIConstants.SECONDARY),
            ("Leaves Used", used_leaves, max(avail_leaves, 1), UIConstants.DANGER),
            ("Leaves Remaining", remaining_leaves, max(avail_leaves, 1), UIConstants.SUCCESS),
        ]

        for b_name, b_val, b_max, b_color in breakdown_items:
            row_f = ctk.CTkFrame(c_inner, fg_color="transparent")
            row_f.pack(fill="x", pady=4)

            pct = min(1.0, b_val / b_max) if b_max > 0 else 0.0

            lbl_f = ctk.CTkFrame(row_f, fg_color="transparent")
            lbl_f.pack(fill="x")
            ctk.CTkLabel(lbl_f, text=b_name, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(side="left")
            ctk.CTkLabel(lbl_f, text=str(b_val), font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_PRIMARY).pack(side="right")

            pb = ctk.CTkProgressBar(row_f, height=10, progress_color=b_color, fg_color=UIConstants.SIDEBAR_BG)
            pb.pack(fill="x", pady=(2, 6))
            pb.set(pct)

        # Uselessness Meter Card
        meter_card = ctk.CTkFrame(scroll_content, fg_color=UIConstants.CARD_BG, corner_radius=12)
        meter_card.pack(fill="x", pady=(0, 15))

        m_inner = ctk.CTkFrame(meter_card, fg_color="transparent")
        m_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(m_inner, text="🎯 Uselessness Meter", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 10))

        meter_lines = get_uselessness_meter(best_eff, used_leaves, avail_leaves)
        for line in meter_lines:
            ctk.CTkLabel(m_inner, text=line, font=UIConstants.FONT_MONO, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=2)
