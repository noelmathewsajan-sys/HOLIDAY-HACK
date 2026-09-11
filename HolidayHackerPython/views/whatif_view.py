import customtkinter as ctk
from datetime import date, datetime
from views.ui_constants import UIConstants
from algorithm import HolidayOptimizer
from humor_utils import get_efficiency_label
import tkinter.messagebox as messagebox

class WhatIfView(ctk.CTkFrame):
    def __init__(self, master, user, holiday_service, leave_service, main_app, default_start=None, default_end=None, default_leaves=None):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.holiday_service = holiday_service
        self.leave_service = leave_service
        self.main_app = main_app

        self.start_date = default_start or date.today()
        self.end_date = default_end or date.today().replace(month=12, day=31)
        self.leaves = default_leaves or self.user.available_leaves

        self.build_ui()
        self.run_simulation()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(header, text="🤔 What-If Simulator", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        title.pack(side="left")

        sub = ctk.CTkLabel(header, text="See how much break you get with 1, 2, 3... or more leaves!", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY)
        sub.pack(side="left", padx=15, pady=(5, 0))

        # Parameters Card
        ctrl_card = ctk.CTkFrame(self, fg_color=UIConstants.CARD_BG, corner_radius=12)
        ctrl_card.pack(fill="x", pady=(0, 15))

        ctrl_grid = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        ctrl_grid.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(ctrl_grid, text="Start Date:", font=UIConstants.FONT_SMALL).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.start_entry = ctk.CTkEntry(ctrl_grid, width=130)
        self.start_entry.insert(0, self.start_date.strftime("%Y-%m-%d"))
        self.start_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(ctrl_grid, text="End Date:", font=UIConstants.FONT_SMALL).grid(row=0, column=2, sticky="w", padx=(20, 5), pady=5)
        self.end_entry = ctk.CTkEntry(ctrl_grid, width=130)
        self.end_entry.insert(0, self.end_date.strftime("%Y-%m-%d"))
        self.end_entry.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(ctrl_grid, text="Max Leaves:", font=UIConstants.FONT_SMALL).grid(row=0, column=4, sticky="w", padx=(20, 5), pady=5)
        self.leaves_entry = ctk.CTkEntry(ctrl_grid, width=80)
        self.leaves_entry.insert(0, str(self.leaves))
        self.leaves_entry.grid(row=0, column=5, padx=5, pady=5)

        sim_btn = ctk.CTkButton(
            ctrl_grid, text="⚡ Simulate", width=120,
            font=UIConstants.FONT_BODY_BOLD, fg_color=UIConstants.PRIMARY,
            text_color="#000000", hover_color=UIConstants.PRIMARY_HOVER,
            command=self.run_simulation
        )
        sim_btn.grid(row=0, column=6, padx=(25, 5), pady=5)

        # Best Value Highlight Frame
        self.best_card = ctk.CTkFrame(self, fg_color=UIConstants.CARD_BG, corner_radius=12)
        self.best_card.pack(fill="x", pady=(0, 15))

        # Results Scrollable Frame
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)

    def set_params(self, start_date: date, end_date: date, leaves: int):
        self.start_entry.delete(0, "end")
        self.start_entry.insert(0, start_date.strftime("%Y-%m-%d"))
        self.end_entry.delete(0, "end")
        self.end_entry.insert(0, end_date.strftime("%Y-%m-%d"))
        self.leaves_entry.delete(0, "end")
        self.leaves_entry.insert(0, str(leaves))
        self.run_simulation()

    def run_simulation(self):
        try:
            start = datetime.strptime(self.start_entry.get().strip(), "%Y-%m-%d").date()
            end = datetime.strptime(self.end_entry.get().strip(), "%Y-%m-%d").date()
            leaves = int(self.leaves_entry.get().strip())
            if end < start:
                messagebox.showwarning("Range Error", "End date must be after start date.")
                return
            if leaves <= 0:
                messagebox.showwarning("Input Error", "Max leaves must be at least 1.")
                return
        except Exception:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        holidays = self.holiday_service.get_holidays_in_range(start, end)
        user_leaves = self.leave_service.get_user_leaves_in_range(self.user.id, start, end)

        optimizer = HolidayOptimizer()
        strategies = optimizer.find_best_strategies(start, end, holidays, user_leaves, leaves)

        # Update best card
        for widget in self.best_card.winfo_children():
            widget.destroy()

        # Update results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not strategies:
            ctk.CTkLabel(self.results_frame, text="No valid combinations found for this range.", font=UIConstants.FONT_BODY).pack(pady=30)
            return

        # Find best value (highest efficiency with leaves_needed > 0)
        paid_strategies = [s for s in strategies if s.leaves_needed > 0]
        best_strat = max(paid_strategies, key=lambda s: s.efficiency, default=strategies[0])

        b_content = ctk.CTkFrame(self.best_card, fg_color="transparent")
        b_content.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(b_content, text="⭐ BEST VALUE OPTION", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.PRIMARY).pack(anchor="w")
        best_text = (
            f"Use {best_strat.leaves_needed} leave(s) ➔ {best_strat.total_days} consecutive days off  |  "
            f"{best_strat.efficiency:.1f}× efficiency  •  {get_efficiency_label(best_strat.efficiency)}"
        )
        ctk.CTkLabel(b_content, text=best_text, font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(4, 0))

        # Table Header
        tbl_header = ctk.CTkFrame(self.results_frame, fg_color=UIConstants.SIDEBAR_BG, corner_radius=8, height=40)
        tbl_header.pack(fill="x", pady=(0, 6))

        for col_idx, (col_name, weight) in enumerate([("Leave Used", 2), ("Maximum Break", 2), ("Efficiency", 2), ("Rating", 3)]):
            tbl_header.grid_columnconfigure(col_idx, weight=weight)
            lbl = ctk.CTkLabel(tbl_header, text=col_name, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_SECONDARY)
            lbl.grid(row=0, column=col_idx, padx=10, pady=8, sticky="w")

        # Table Rows
        # Sort strategies by leaves needed ascending for clean comparison
        display_strategies = sorted(strategies, key=lambda s: s.leaves_needed)
        for idx, strat in enumerate(display_strategies):
            row_bg = UIConstants.CARD_BG if idx % 2 == 0 else UIConstants.SIDEBAR_BG
            row_frame = ctk.CTkFrame(self.results_frame, fg_color=row_bg, corner_radius=6, height=40)
            row_frame.pack(fill="x", pady=2)

            leaves_txt = f"{strat.leaves_needed} leave" if strat.leaves_needed == 1 else f"{strat.leaves_needed} leaves"
            break_txt = f"{strat.total_days} days off"
            eff_txt = f"{strat.efficiency:.2f}×"
            rating_txt = get_efficiency_label(strat.efficiency)

            for col_idx, (val, weight) in enumerate([(leaves_txt, 2), (break_txt, 2), (eff_txt, 2), (rating_txt, 3)]):
                row_frame.grid_columnconfigure(col_idx, weight=weight)
                color = UIConstants.PRIMARY if (strat == best_strat and strat.leaves_needed > 0) else UIConstants.TEXT_PRIMARY
                lbl = ctk.CTkLabel(row_frame, text=val, font=UIConstants.FONT_BODY, text_color=color)
                lbl.grid(row=0, column=col_idx, padx=10, pady=8, sticky="w")
