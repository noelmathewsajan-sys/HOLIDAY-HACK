import customtkinter as ctk
from views.ui_constants import UIConstants
from services import AuthService
import tkinter.messagebox as messagebox

class SettingsView(ctk.CTkFrame):
    def __init__(self, master, user, auth_service, main_app):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.auth_service = auth_service
        self.main_app = main_app

        self.build_ui()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(header, text="⚙️ Settings", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        title.pack(side="left")

        scroll_content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_content.pack(fill="both", expand=True)

        # 1. Appearance Card
        appear_card = ctk.CTkFrame(scroll_content, fg_color=UIConstants.CARD_BG, corner_radius=12)
        appear_card.pack(fill="x", pady=(0, 15))

        a_inner = ctk.CTkFrame(appear_card, fg_color="transparent")
        a_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(a_inner, text="🎨 Appearance", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 10))

        theme_row = ctk.CTkFrame(a_inner, fg_color="transparent")
        theme_row.pack(fill="x")

        ctk.CTkLabel(theme_row, text="Theme Mode:", font=UIConstants.FONT_BODY, text_color=UIConstants.TEXT_SECONDARY).pack(side="left")

        current_mode = ctk.get_appearance_mode()
        self.theme_switch_var = ctk.StringVar(value="Dark" if current_mode.lower() == "dark" else "Light")

        def toggle_theme():
            mode = self.theme_switch_var.get()
            ctk.set_appearance_mode(mode)

        theme_seg = ctk.CTkSegmentedButton(
            theme_row, values=["Dark", "Light"],
            variable=self.theme_switch_var, command=lambda v: toggle_theme()
        )
        theme_seg.pack(side="left", padx=(15, 0))

        # 2. Profile Card
        profile_card = ctk.CTkFrame(scroll_content, fg_color=UIConstants.CARD_BG, corner_radius=12)
        profile_card.pack(fill="x", pady=(0, 15))

        p_inner = ctk.CTkFrame(profile_card, fg_color="transparent")
        p_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(p_inner, text="👤 Profile Settings", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 12))

        p_grid = ctk.CTkFrame(p_inner, fg_color="transparent")
        p_grid.pack(fill="x")

        ctk.CTkLabel(p_grid, text="Full Name:", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=6)
        self.name_entry = ctk.CTkEntry(p_grid, width=280)
        self.name_entry.insert(0, self.user.name)
        self.name_entry.grid(row=0, column=1, padx=15, pady=6, sticky="w")

        ctk.CTkLabel(p_grid, text="Username / Email:", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).grid(row=1, column=0, sticky="w", pady=6)
        self.email_entry = ctk.CTkEntry(p_grid, width=280)
        self.email_entry.insert(0, self.user.email)
        self.email_entry.grid(row=1, column=1, padx=15, pady=6, sticky="w")

        ctk.CTkLabel(p_grid, text="Available Leaves:", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=6)
        self.leaves_entry = ctk.CTkEntry(p_grid, width=120)
        self.leaves_entry.insert(0, str(self.user.available_leaves))
        self.leaves_entry.grid(row=2, column=1, padx=15, pady=6, sticky="w")

        save_btn = ctk.CTkButton(
            p_inner, text="💾 Save Profile Changes", width=180, height=36,
            font=UIConstants.FONT_BODY_BOLD, fg_color=UIConstants.PRIMARY,
            text_color="#000000", hover_color=UIConstants.PRIMARY_HOVER,
            command=self.handle_save_profile
        )
        save_btn.pack(anchor="w", pady=(15, 0))

        # 3. About Card
        about_card = ctk.CTkFrame(scroll_content, fg_color=UIConstants.CARD_BG, corner_radius=12)
        about_card.pack(fill="x", pady=(0, 15))

        ab_inner = ctk.CTkFrame(about_card, fg_color="transparent")
        ab_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(ab_inner, text="ℹ️ About Holiday Hacker", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))
        desc_text = (
            "Holiday Hacker Python Edition (v2.0)\n\n"
            "\"Work smarter. Holiday longer.\"\n\n"
            "A smart holiday-planning desktop application that finds the maximum number of consecutive days off "
            "by strategically leveraging weekends and public holidays using minimal leave balance.\n\n"
            "Built with 🐍 Python, CustomTkinter, and MySQL."
        )
        ctk.CTkLabel(ab_inner, text=desc_text, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY, justify="left").pack(anchor="w")

    def handle_save_profile(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        try:
            leaves = int(self.leaves_entry.get().strip())
            if leaves < 0:
                messagebox.showwarning("Warning", "Leaves cannot be negative.")
                return
        except ValueError:
            messagebox.showerror("Error", "Available leaves must be an integer.")
            return

        if not name or not email:
            messagebox.showwarning("Warning", "Name and username/email are required.")
            return

        try:
            self.auth_service.update_profile(self.user.id, name, email)
            self.auth_service.update_leaves(self.user.id, leaves)
            self.user.name = name
            self.user.email = email
            self.user.available_leaves = leaves

            # Update sidebar username
            if hasattr(self.main_app, "user_label"):
                self.main_app.user_label.configure(text=f"👤 {self.user.name}")

            messagebox.showinfo("Success", "Profile updated successfully! ✅")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update profile: {e}")
