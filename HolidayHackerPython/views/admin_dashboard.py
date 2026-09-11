import customtkinter as ctk
from datetime import datetime, date
from views.ui_constants import UIConstants
from services import HolidayService, PlanService, UserService, AuthService
from humor_utils import get_efficiency_label
from typing import Callable
import tkinter.messagebox as messagebox

class AdminDashboardView(ctk.CTkFrame):
    def __init__(self, master, admin_user, on_logout: Callable):
        super().__init__(master, fg_color=UIConstants.BG_COLOR)
        self.admin = admin_user
        self.on_logout = on_logout

        self.holiday_service = HolidayService()
        self.plan_service = PlanService()
        self.user_service = UserService()
        self.auth_service = AuthService()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Build Admin Sidebar (Crimson Accent)
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#171226")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # Brand
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="🛡️ ADMIN PANEL",
            font=UIConstants.FONT_HEADING, text_color=UIConstants.DANGER
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 6), sticky="w")

        # Admin user info
        self.admin_label = ctk.CTkLabel(
            self.sidebar_frame, text=f"👤 {self.admin.name}",
            font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY
        )
        self.admin_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Nav Buttons
        self.nav_buttons = {}
        items = [
            ("Dashboard", "📊 Dashboard", self.show_dashboard),
            ("Users", "👥 Users", self.show_users),
            ("Public Holidays", "🎉 Public Holidays", self.show_holidays),
            ("Holiday Plans", "📋 Holiday Plans", self.show_plans),
            ("Settings", "⚙️ Settings", self.show_settings),
        ]

        for idx, (key, label, cmd) in enumerate(items, start=2):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=label, command=cmd,
                fg_color="transparent", text_color=UIConstants.TEXT_PRIMARY,
                anchor="w", font=UIConstants.FONT_BODY, height=36
            )
            btn.grid(row=idx, column=0, pady=4, padx=14, sticky="ew")
            self.nav_buttons[key] = btn

        # Logout at bottom
        logout_btn = ctk.CTkButton(
            self.sidebar_frame, text="🚪 Logout", command=self.on_logout,
            fg_color="transparent", text_color=UIConstants.DANGER,
            hover_color=UIConstants.CARD_BG_HOVER, anchor="w",
            font=UIConstants.FONT_BODY, height=36
        )
        logout_btn.grid(row=8, column=0, pady=(0, 20), padx=14, sticky="ew")

        # Content Area
        self.content_frame = ctk.CTkFrame(self, fg_color=UIConstants.BG_COLOR)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.current_content = None
        self.show_dashboard()

    def _reset_btn_colors(self):
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent")

    def _set_active_page(self, key: str, widget: ctk.CTkFrame):
        self._reset_btn_colors()
        self.nav_buttons[key].configure(fg_color=UIConstants.CARD_BG)
        if self.current_content:
            self.current_content.grid_forget()
            self.current_content.destroy()
        self.current_content = widget
        self.current_content.grid(row=0, column=0, sticky="nsew")

    # 1. Admin Dashboard Overview
    def show_dashboard(self):
        page = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        # Header
        header = ctk.CTkFrame(page, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text="🛡️ System Overview", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY).pack(anchor="w")

        # Stats cards row
        user_count = self.user_service.count_users()
        holiday_count = self.holiday_service.get_holiday_count()
        plan_count = self.plan_service.count_all_plans()
        avg_eff = self.plan_service.get_average_efficiency()

        grid = ctk.CTkFrame(page, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        for i in range(4):
            grid.grid_columnconfigure(i, weight=1)

        admin_kpis = [
            ("👥 Total Users", str(user_count), UIConstants.SECONDARY),
            ("🎉 Public Holidays", str(holiday_count), UIConstants.WARNING),
            ("📋 Total Plans", str(plan_count), UIConstants.PRIMARY),
            ("⚡ Avg Efficiency", f"{avg_eff:.1f}×" if avg_eff > 0 else "—", UIConstants.SUCCESS),
        ]

        for idx, (lbl, val, accent) in enumerate(admin_kpis):
            c = ctk.CTkFrame(grid, fg_color=UIConstants.CARD_BG, corner_radius=12, height=100)
            c.grid(row=0, column=idx, padx=6, pady=6, sticky="nsew")
            c.grid_propagate(False)

            top_bar = ctk.CTkFrame(c, fg_color=accent, height=4, corner_radius=2)
            top_bar.pack(fill="x", side="top")

            c_inner = ctk.CTkFrame(c, fg_color="transparent")
            c_inner.pack(fill="both", expand=True, padx=14, pady=10)
            ctk.CTkLabel(c_inner, text=lbl, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w")
            ctk.CTkLabel(c_inner, text=val, font=UIConstants.FONT_HEADING, text_color=accent).pack(anchor="w", pady=(4, 0))

        # Best Plan Showcase Card
        best_plan = self.plan_service.get_best_plan()
        if best_plan:
            best_card = ctk.CTkFrame(page, fg_color=UIConstants.CARD_BG, corner_radius=14)
            best_card.pack(fill="x", pady=(0, 20))

            b_inner = ctk.CTkFrame(best_card, fg_color="transparent")
            b_inner.pack(fill="x", padx=24, pady=18)

            ctk.CTkLabel(b_inner, text="🏆 Top Performing Break Plan Across Users", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.PRIMARY).pack(anchor="w")
            b_text = (
                f"Plan: {best_plan.plan_name} (User ID: {best_plan.user_id})\n"
                f"Dates: {best_plan.start_date} to {best_plan.end_date}   •   "
                f"{best_plan.consecutive_days} Days Off with {best_plan.leaves_used} Leaves Used   •   "
                f"Efficiency: {best_plan.efficiency:.1f}× ({get_efficiency_label(best_plan.efficiency)})"
            )
            ctk.CTkLabel(b_inner, text=b_text, font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_PRIMARY, justify="left").pack(anchor="w", pady=(6, 0))

        # Quick Actions Card
        actions_card = ctk.CTkFrame(page, fg_color=UIConstants.CARD_BG, corner_radius=14)
        actions_card.pack(fill="x", pady=(0, 20))

        a_inner = ctk.CTkFrame(actions_card, fg_color="transparent")
        a_inner.pack(fill="x", padx=24, pady=18)

        ctk.CTkLabel(a_inner, text="⚡ Quick Admin Navigation", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 10))
        btn_row = ctk.CTkFrame(a_inner, fg_color="transparent")
        btn_row.pack(anchor="w")

        ctk.CTkButton(btn_row, text="🎉 Manage Holidays", command=self.show_holidays, fg_color=UIConstants.PRIMARY, text_color="#000", font=UIConstants.FONT_BODY).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="👥 View Users", command=self.show_users, fg_color=UIConstants.CARD_BG_HOVER, font=UIConstants.FONT_BODY).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="📋 All Holiday Plans", command=self.show_plans, fg_color=UIConstants.CARD_BG_HOVER, font=UIConstants.FONT_BODY).pack(side="left")

        self._set_active_page("Dashboard", page)

    # 2. Registered Users Management
    def show_users(self):
        page = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        header = ctk.CTkFrame(page, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text="👥 Registered Users", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY).pack(side="left")

        users = self.user_service.find_all_users()
        ctk.CTkLabel(header, text=f"({len(users)} users registered)", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(side="left", padx=15, pady=(5, 0))

        # Table Header
        tbl_header = ctk.CTkFrame(page, fg_color=UIConstants.SIDEBAR_BG, corner_radius=8, height=38)
        tbl_header.pack(fill="x", pady=(0, 6))

        for col_idx, (col_name, weight) in enumerate([("ID", 1), ("Name", 3), ("Email / Username", 3), ("Available Leaves", 2), ("Role", 2)]):
            tbl_header.grid_columnconfigure(col_idx, weight=weight)
            lbl = ctk.CTkLabel(tbl_header, text=col_name, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_SECONDARY)
            lbl.grid(row=0, column=col_idx, padx=10, pady=8, sticky="w")

        # Table Rows
        for idx, u in enumerate(users):
            row_bg = UIConstants.CARD_BG if idx % 2 == 0 else UIConstants.SIDEBAR_BG
            row_frame = ctk.CTkFrame(page, fg_color=row_bg, corner_radius=6, height=40)
            row_frame.pack(fill="x", pady=2)

            for col_idx, (val, weight) in enumerate([(str(u.id), 1), (u.name, 3), (u.email, 3), (str(u.available_leaves), 2), (u.role.upper(), 2)]):
                row_frame.grid_columnconfigure(col_idx, weight=weight)
                color = UIConstants.PRIMARY if col_idx == 1 else UIConstants.TEXT_PRIMARY
                lbl = ctk.CTkLabel(row_frame, text=val, font=UIConstants.FONT_BODY, text_color=color)
                lbl.grid(row=0, column=col_idx, padx=10, pady=8, sticky="w")

        self._set_active_page("Users", page)

    # 3. Public Holidays CRUD
    def show_holidays(self):
        page = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        header = ctk.CTkFrame(page, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text="🎉 Manage Public Holidays", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY).pack(anchor="w")

        # Add Holiday Card Form
        add_card = ctk.CTkFrame(page, fg_color=UIConstants.CARD_BG, corner_radius=12)
        add_card.pack(fill="x", pady=(0, 15))

        a_inner = ctk.CTkFrame(add_card, fg_color="transparent")
        a_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(a_inner, text="➕ Add New Public Holiday", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 10))

        grid = ctk.CTkFrame(a_inner, fg_color="transparent")
        grid.pack(fill="x")

        ctk.CTkLabel(grid, text="Name:", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=4)
        name_entry = ctk.CTkEntry(grid, width=200, placeholder_text="e.g. Diwali")
        name_entry.grid(row=0, column=1, padx=(5, 20), pady=4, sticky="w")

        ctk.CTkLabel(grid, text="Date (YYYY-MM-DD):", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).grid(row=0, column=2, sticky="w", pady=4)
        date_entry = ctk.CTkEntry(grid, width=140, placeholder_text="YYYY-MM-DD")
        date_entry.grid(row=0, column=3, padx=(5, 20), pady=4, sticky="w")

        ctk.CTkLabel(grid, text="Description:", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).grid(row=0, column=4, sticky="w", pady=4)
        desc_entry = ctk.CTkEntry(grid, width=220, placeholder_text="Optional notes")
        desc_entry.grid(row=0, column=5, padx=5, pady=4, sticky="w")

        def add_holiday_action():
            name = name_entry.get().strip()
            date_str = date_entry.get().strip()
            desc = desc_entry.get().strip()
            try:
                h_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                self.holiday_service.add_holiday(name, h_date, desc)
                messagebox.showinfo("Success", f"Holiday '{name}' added successfully! 🎉")
                self.show_holidays()
            except ValueError as e:
                messagebox.showwarning("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add holiday: {e}")

        add_btn = ctk.CTkButton(
            a_inner, text="➕ Add Holiday", width=140, height=32,
            font=UIConstants.FONT_BODY_BOLD, fg_color=UIConstants.PRIMARY,
            text_color="#000", hover_color=UIConstants.PRIMARY_HOVER,
            command=add_holiday_action
        )
        add_btn.pack(anchor="w", pady=(12, 0))

        # Holidays Table
        holidays = self.holiday_service.get_all_holidays()
        ctk.CTkLabel(page, text=f"Total Holidays ({len(holidays)}):", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(5, 6))

        tbl_header = ctk.CTkFrame(page, fg_color=UIConstants.SIDEBAR_BG, corner_radius=8, height=38)
        tbl_header.pack(fill="x", pady=(0, 6))

        for col_idx, (col_name, weight) in enumerate([("ID", 1), ("Holiday Name", 4), ("Date", 3), ("Day", 3), ("Description", 4), ("Actions", 3)]):
            tbl_header.grid_columnconfigure(col_idx, weight=weight)
            lbl = ctk.CTkLabel(tbl_header, text=col_name, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_SECONDARY)
            lbl.grid(row=0, column=col_idx, padx=10, pady=8, sticky="w")

        days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for idx, h in enumerate(holidays):
            row_bg = UIConstants.CARD_BG if idx % 2 == 0 else UIConstants.SIDEBAR_BG
            row_frame = ctk.CTkFrame(page, fg_color=row_bg, corner_radius=6, height=42)
            row_frame.pack(fill="x", pady=2)

            day_name = days_names[h.holiday_date.weekday()]

            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=4)
            row_frame.grid_columnconfigure(2, weight=3)
            row_frame.grid_columnconfigure(3, weight=3)
            row_frame.grid_columnconfigure(4, weight=4)
            row_frame.grid_columnconfigure(5, weight=3)

            ctk.CTkLabel(row_frame, text=str(h.id), font=UIConstants.FONT_BODY).grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=h.holiday_name, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.WARNING).grid(row=0, column=1, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=h.holiday_date.strftime("%Y-%m-%d"), font=UIConstants.FONT_BODY).grid(row=0, column=2, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=day_name, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).grid(row=0, column=3, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=h.description or "—", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).grid(row=0, column=4, padx=10, pady=8, sticky="w")

            # Actions frame
            act_f = ctk.CTkFrame(row_frame, fg_color="transparent")
            act_f.grid(row=0, column=5, padx=10, pady=6, sticky="w")

            def edit_h(hol=h):
                dialog = ctk.CTkInputDialog(text=f"Enter new Name for '{hol.holiday_name}':", title="Edit Holiday")
                new_n = dialog.get_input()
                if new_n and new_n.strip():
                    self.holiday_service.update_holiday(hol.id, new_n.strip(), hol.holiday_date, hol.description)
                    self.show_holidays()

            def del_h(h_id=h.id, h_name=h.holiday_name):
                if messagebox.askyesno("Confirm Delete", f"Delete public holiday '{h_name}'?"):
                    self.holiday_service.delete_holiday(h_id)
                    self.show_holidays()

            ctk.CTkButton(act_f, text="✏️", width=32, height=28, command=edit_h).pack(side="left", padx=2)
            ctk.CTkButton(act_f, text="🗑", width=32, height=28, fg_color=UIConstants.DANGER, hover_color=UIConstants.DANGER_HOVER, command=del_h).pack(side="left", padx=2)

        self._set_active_page("Public Holidays", page)

    # 4. Global Holiday Plans Oversight
    def show_plans(self):
        page = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        header = ctk.CTkFrame(page, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text="📋 All Holiday Plans (System-wide)", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY).pack(side="left")

        plans = self.plan_service.get_all_plans()
        ctk.CTkLabel(header, text=f"({len(plans)} plans created)", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(side="left", padx=15, pady=(5, 0))

        if not plans:
            ctk.CTkLabel(page, text="No holiday plans created yet.", font=UIConstants.FONT_BODY).pack(pady=40)
            self._set_active_page("Holiday Plans", page)
            return

        tbl_header = ctk.CTkFrame(page, fg_color=UIConstants.SIDEBAR_BG, corner_radius=8, height=38)
        tbl_header.pack(fill="x", pady=(0, 6))

        for col_idx, (col_name, weight) in enumerate([("ID", 1), ("User ID", 2), ("Plan Name", 4), ("Range", 4), ("Break", 2), ("Leaves", 2), ("Efficiency", 2), ("Action", 2)]):
            tbl_header.grid_columnconfigure(col_idx, weight=weight)
            lbl = ctk.CTkLabel(tbl_header, text=col_name, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_SECONDARY)
            lbl.grid(row=0, column=col_idx, padx=10, pady=8, sticky="w")

        for idx, p in enumerate(plans):
            row_bg = UIConstants.CARD_BG if idx % 2 == 0 else UIConstants.SIDEBAR_BG
            row_frame = ctk.CTkFrame(page, fg_color=row_bg, corner_radius=6, height=42)
            row_frame.pack(fill="x", pady=2)

            date_range = f"{p.start_date.strftime('%b %d')} - {p.end_date.strftime('%b %d, %Y')}"

            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=2)
            row_frame.grid_columnconfigure(2, weight=4)
            row_frame.grid_columnconfigure(3, weight=4)
            row_frame.grid_columnconfigure(4, weight=2)
            row_frame.grid_columnconfigure(5, weight=2)
            row_frame.grid_columnconfigure(6, weight=2)
            row_frame.grid_columnconfigure(7, weight=2)

            ctk.CTkLabel(row_frame, text=str(p.id), font=UIConstants.FONT_BODY).grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=f"User #{p.user_id}", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).grid(row=0, column=1, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=p.plan_name, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.PRIMARY).grid(row=0, column=2, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=date_range, font=UIConstants.FONT_SMALL).grid(row=0, column=3, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=f"{p.consecutive_days}d", font=UIConstants.FONT_BODY, text_color=UIConstants.SUCCESS).grid(row=0, column=4, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=str(p.leaves_used), font=UIConstants.FONT_BODY).grid(row=0, column=5, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=f"{p.efficiency:.1f}×", font=UIConstants.FONT_BODY, text_color=UIConstants.ACCENT).grid(row=0, column=6, padx=10, pady=8, sticky="w")

            def del_plan(p_id=p.id):
                if messagebox.askyesno("Confirm Delete", f"Delete holiday plan #{p_id}?"):
                    self.plan_service.delete_plan(p_id)
                    self.show_plans()

            ctk.CTkButton(
                row_frame, text="🗑", width=34, height=28,
                fg_color=UIConstants.DANGER, hover_color=UIConstants.DANGER_HOVER,
                command=del_plan
            ).grid(row=0, column=7, padx=10, pady=6, sticky="w")

        self._set_active_page("Holiday Plans", page)

    # 5. Admin Settings
    def show_settings(self):
        page = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")

        header = ctk.CTkFrame(page, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text="⚙️ Admin Settings", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY).pack(anchor="w")

        # Appearance Card
        appear_card = ctk.CTkFrame(page, fg_color=UIConstants.CARD_BG, corner_radius=12)
        appear_card.pack(fill="x", pady=(0, 15))

        a_inner = ctk.CTkFrame(appear_card, fg_color="transparent")
        a_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(a_inner, text="🎨 Appearance", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 10))

        theme_row = ctk.CTkFrame(a_inner, fg_color="transparent")
        theme_row.pack(fill="x")

        ctk.CTkLabel(theme_row, text="Theme Mode:", font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY).pack(side="left")

        current_mode = ctk.get_appearance_mode()
        theme_seg = ctk.CTkSegmentedButton(
            theme_row, values=["Dark", "Light"],
            command=lambda v: ctk.set_appearance_mode(v)
        )
        theme_seg.set("Dark" if current_mode.lower() == "dark" else "Light")
        theme_seg.pack(side="left", padx=(15, 0))

        # Admin Profile Card
        p_card = ctk.CTkFrame(page, fg_color=UIConstants.CARD_BG, corner_radius=12)
        p_card.pack(fill="x", pady=(0, 15))

        p_inner = ctk.CTkFrame(p_card, fg_color="transparent")
        p_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(p_inner, text="🛡️ Admin Profile Info", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(p_inner, text=f"Admin Name: {self.admin.name}\nEmail / Username: {self.admin.email}\nRole: System Administrator", font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY, justify="left").pack(anchor="w")

        self._set_active_page("Settings", page)
