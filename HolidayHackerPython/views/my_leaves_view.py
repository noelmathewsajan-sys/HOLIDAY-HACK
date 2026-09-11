import customtkinter as ctk
from datetime import datetime, date
from views.ui_constants import UIConstants
import tkinter.messagebox as messagebox

class MyLeavesView(ctk.CTkFrame):
    def __init__(self, master, user, leave_service, auth_service, main_app):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.leave_service = leave_service
        self.auth_service = auth_service
        self.main_app = main_app

        self.build_ui()
        self.refresh_data()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(header, text="🌴 My Leaves", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        title.pack(anchor="w")

        self.summary_label = ctk.CTkLabel(
            header, text="", font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY
        )
        self.summary_label.pack(anchor="w", pady=(4, 0))

        # Action card (Add Leave & Update Available)
        action_card = ctk.CTkFrame(self, fg_color=UIConstants.CARD_BG, corner_radius=12)
        action_card.pack(fill="x", pady=(0, 15))

        grid = ctk.CTkFrame(action_card, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=15)

        # Add leave
        ctk.CTkLabel(grid, text="Add Leave Date (YYYY-MM-DD):", font=UIConstants.FONT_SMALL).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.new_date_entry = ctk.CTkEntry(grid, width=140, placeholder_text="YYYY-MM-DD")
        self.new_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.new_date_entry.grid(row=0, column=1, padx=5, pady=5)

        add_btn = ctk.CTkButton(
            grid, text="➕ Add Leave", width=120,
            font=UIConstants.FONT_BODY_BOLD, fg_color=UIConstants.SUCCESS,
            text_color="#000000", hover_color="#00C853",
            command=self.handle_add_leave
        )
        add_btn.grid(row=0, column=2, padx=(10, 25), pady=5)

        # Available leaves balance update
        ctk.CTkLabel(grid, text="Total Available Leaves:", font=UIConstants.FONT_SMALL).grid(row=0, column=3, padx=(15, 10), pady=5, sticky="w")
        self.avail_entry = ctk.CTkEntry(grid, width=70)
        self.avail_entry.insert(0, str(self.user.available_leaves))
        self.avail_entry.grid(row=0, column=4, padx=5, pady=5)

        update_btn = ctk.CTkButton(
            grid, text="Update", width=90,
            font=UIConstants.FONT_BODY, fg_color=UIConstants.SECONDARY,
            text_color="#000000", hover_color="#9FA5B9",
            command=self.handle_update_balance
        )
        update_btn.grid(row=0, column=5, padx=10, pady=5)

        # Leaves Table / Scrollable Frame
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

    def refresh_data(self):
        used = self.leave_service.get_used_leave_count(self.user.id)
        remaining = max(0, self.user.available_leaves - used)
        self.summary_label.configure(
            text=f"Total: {self.user.available_leaves}   |   Used: {used}   |   Remaining: {remaining}"
        )
        self.avail_entry.delete(0, "end")
        self.avail_entry.insert(0, str(self.user.available_leaves))

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        leaves = self.leave_service.get_user_leaves(self.user.id)

        if not leaves:
            ctk.CTkLabel(self.list_frame, text="No leaves booked yet. Plan ahead with the Holiday Hacker!", font=UIConstants.FONT_BODY).pack(pady=40)
            return

        # Table Header
        tbl_header = ctk.CTkFrame(self.list_frame, fg_color=UIConstants.SIDEBAR_BG, corner_radius=8, height=38)
        tbl_header.pack(fill="x", pady=(0, 6))

        for col_idx, (col_name, weight) in enumerate([("#", 1), ("Date", 3), ("Day of Week", 3), ("Status", 3), ("Action", 2)]):
            tbl_header.grid_columnconfigure(col_idx, weight=weight)
            lbl = ctk.CTkLabel(tbl_header, text=col_name, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_SECONDARY)
            lbl.grid(row=0, column=col_idx, padx=10, pady=8, sticky="w")

        # Table Rows
        days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for idx, lv in enumerate(leaves):
            row_bg = UIConstants.CARD_BG if idx % 2 == 0 else UIConstants.SIDEBAR_BG
            row_frame = ctk.CTkFrame(self.list_frame, fg_color=row_bg, corner_radius=6, height=42)
            row_frame.pack(fill="x", pady=2)

            day_name = days_names[lv.leave_date.weekday()]

            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=3)
            row_frame.grid_columnconfigure(2, weight=3)
            row_frame.grid_columnconfigure(3, weight=3)
            row_frame.grid_columnconfigure(4, weight=2)

            ctk.CTkLabel(row_frame, text=str(idx + 1), font=UIConstants.FONT_BODY).grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=lv.leave_date.strftime("%Y-%m-%d"), font=UIConstants.FONT_BODY_BOLD).grid(row=0, column=1, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=day_name, font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY).grid(row=0, column=2, padx=10, pady=8, sticky="w")
            
            # Status chip
            status_lbl = ctk.CTkLabel(row_frame, text=lv.status.capitalize(), font=UIConstants.FONT_SMALL, text_color=UIConstants.SUCCESS)
            status_lbl.grid(row=0, column=3, padx=10, pady=8, sticky="w")

            def delete_it(leave_id=lv.id, l_date=lv.leave_date):
                if messagebox.askyesno("Confirm Delete", f"Remove leave on {l_date}?"):
                    self.leave_service.delete_leave(leave_id)
                    self.refresh_data()
                    self.main_app.calendar_view.refresh_grid()

            del_btn = ctk.CTkButton(
                row_frame, text="🗑 Delete", width=80, height=28,
                font=UIConstants.FONT_SMALL, fg_color=UIConstants.DANGER,
                hover_color=UIConstants.DANGER_HOVER, command=delete_it
            )
            del_btn.grid(row=0, column=4, padx=10, pady=6, sticky="w")

    def handle_add_leave(self):
        try:
            d = datetime.strptime(self.new_date_entry.get().strip(), "%Y-%m-%d").date()
        except Exception:
            messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
            return

        try:
            self.leave_service.add_leave(self.user.id, d)
            messagebox.showinfo("Success", f"Leave on {d} successfully booked!")
            self.refresh_data()
            self.main_app.calendar_view.refresh_grid()
        except ValueError as e:
            messagebox.showwarning("Warning", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add leave: {e}")

    def handle_update_balance(self):
        try:
            val = int(self.avail_entry.get().strip())
            if val < 0:
                messagebox.showwarning("Warning", "Leaves cannot be negative.")
                return
            self.auth_service.update_leaves(self.user.id, val)
            self.user.available_leaves = val
            messagebox.showinfo("Updated", "Available leaves updated!")
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid whole number.")
