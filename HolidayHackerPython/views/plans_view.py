import customtkinter as ctk
from views.ui_constants import UIConstants
from humor_utils import get_efficiency_label
import tkinter.messagebox as messagebox

class PlansView(ctk.CTkFrame):
    def __init__(self, master, user, plan_service, main_app):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.plan_service = plan_service
        self.main_app = main_app

        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(header, text="📋 Saved Holiday Plans", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        title.pack(side="left")

        self.count_label = ctk.CTkLabel(header, text="", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY)
        self.count_label.pack(side="left", padx=15, pady=(5, 0))

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

    def refresh_plans(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        plans = self.plan_service.get_user_plans(self.user.id)
        self.count_label.configure(text=f"({len(plans)} plans saved)")

        if not plans:
            ctk.CTkLabel(self.list_frame, text="No saved plans yet. Use Find Holidays to plan your vacation!", font=UIConstants.FONT_BODY).pack(pady=40)
            return

        for plan in plans:
            card = ctk.CTkFrame(self.list_frame, fg_color=UIConstants.CARD_BG, corner_radius=12)
            card.pack(fill="x", pady=8)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=20, pady=16)

            # Top row: title & delete
            top_row = ctk.CTkFrame(inner, fg_color="transparent")
            top_row.pack(fill="x")

            lbl = ctk.CTkLabel(top_row, text=f"🏖️ {plan.plan_name}", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.PRIMARY)
            lbl.pack(side="left")

            def delete_it(p_id=plan.id, p_name=plan.plan_name):
                if messagebox.askyesno("Confirm Delete", f"Delete holiday plan '{p_name}'?"):
                    self.plan_service.delete_plan(p_id)
                    self.refresh_plans()

            del_btn = ctk.CTkButton(
                top_row, text="🗑 Delete", width=80, height=26,
                font=UIConstants.FONT_SMALL, fg_color=UIConstants.DANGER,
                hover_color=UIConstants.DANGER_HOVER, command=delete_it
            )
            del_btn.pack(side="right")

            # Dates
            date_str = f"📅 {plan.start_date.strftime('%b %d, %Y')}  ➔  {plan.end_date.strftime('%b %d, %Y')}"
            ctk.CTkLabel(inner, text=date_str, font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(6, 2))

            # Stats line
            stats_str = (
                f"🏆 {plan.consecutive_days} days off   |   "
                f"🌴 {plan.leaves_used} leaves used   |   "
                f"⚡ {plan.efficiency:.1f}× efficiency  •  {get_efficiency_label(plan.efficiency)}"
            )
            ctk.CTkLabel(inner, text=stats_str, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 6))

            # Recommended dates
            if plan.recommended_dates:
                rec_str = "📌 Leaves: " + ", ".join([d.strftime("%b %d") for d in plan.recommended_dates])
                ctk.CTkLabel(inner, text=rec_str, font=UIConstants.FONT_SMALL, text_color=UIConstants.CAL_RECOMMENDED).pack(anchor="w", pady=(0, 8))

            # Bottom actions row
            bottom_row = ctk.CTkFrame(inner, fg_color="transparent")
            bottom_row.pack(fill="x")

            if plan.created_at:
                c_txt = f"Created: {plan.created_at.strftime('%Y-%m-%d %H:%M')}"
                ctk.CTkLabel(bottom_row, text=c_txt, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(side="left")

            def view_on_cal(p=plan):
                self.main_app.calendar_view.set_recommended_dates(p.recommended_dates)
                self.main_app.show_calendar()

            btn = ctk.CTkButton(
                bottom_row, text="📅 View on Calendar", width=140, height=28,
                font=UIConstants.FONT_SMALL, fg_color=UIConstants.PRIMARY,
                text_color="#000000", hover_color=UIConstants.PRIMARY_HOVER,
                command=view_on_cal
            )
            btn.pack(side="right")
