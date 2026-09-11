import customtkinter as ctk
from views.ui_constants import UIConstants
from services import AuthService
from typing import Callable

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success: Callable, on_switch_to_register: Callable):
        super().__init__(master, fg_color=UIConstants.BG_COLOR)
        self.on_login_success = on_login_success
        self.on_switch_to_register = on_switch_to_register
        self.auth_service = AuthService()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_ui()

    def build_ui(self):
        # Center container
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0)

        # Login card
        card = ctk.CTkFrame(center_frame, fg_color=UIConstants.CARD_BG, corner_radius=16, width=420)
        card.pack(padx=20, pady=20)

        # Icon and title
        ctk.CTkLabel(card, text="🏖️", font=("Segoe UI Emoji", 48)).pack(pady=(30, 5))
        ctk.CTkLabel(card, text="HOLIDAY HACKER", font=UIConstants.FONT_TITLE, text_color=UIConstants.PRIMARY).pack(pady=(0, 2))
        ctk.CTkLabel(card, text="Work smarter. Holiday longer.", font=UIConstants.FONT_SUBTITLE, text_color=UIConstants.TEXT_SECONDARY).pack(pady=(0, 25))

        # Form fields
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=35, pady=(0, 10))

        ctk.CTkLabel(form, text="Username / Email", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))
        self.email_entry = ctk.CTkEntry(form, height=40, font=UIConstants.FONT_BODY, placeholder_text="Enter email or username")
        self.email_entry.pack(fill="x", pady=(0, 15))
        self.email_entry.insert(0, "testuser")

        ctk.CTkLabel(form, text="Password", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))
        self.password_entry = ctk.CTkEntry(form, height=40, font=UIConstants.FONT_BODY, show="●", placeholder_text="Enter password")
        self.password_entry.pack(fill="x", pady=(0, 10))
        self.password_entry.insert(0, "test123")
        self.password_entry.bind("<Return>", lambda event: self.handle_login())

        # Show password & remember me row
        opts_row = ctk.CTkFrame(form, fg_color="transparent")
        opts_row.pack(fill="x", pady=(0, 15))

        self.show_pwd_var = ctk.BooleanVar(value=False)
        self.show_pwd_cb = ctk.CTkCheckBox(
            opts_row, text="Show password", variable=self.show_pwd_var,
            command=self.toggle_show_password, font=UIConstants.FONT_SMALL,
            checkbox_width=18, checkbox_height=18
        )
        self.show_pwd_cb.pack(side="left")

        # Error label
        self.error_label = ctk.CTkLabel(form, text="", font=UIConstants.FONT_SMALL, text_color=UIConstants.DANGER)
        self.error_label.pack(anchor="w", pady=(0, 10))

        # Login button
        login_btn = ctk.CTkButton(
            form, text="Sign In", height=42,
            font=UIConstants.FONT_BODY_BOLD, fg_color=UIConstants.PRIMARY,
            text_color="#000000", hover_color=UIConstants.PRIMARY_HOVER,
            command=self.handle_login
        )
        login_btn.pack(fill="x", pady=(5, 15))

        # Register link
        reg_btn = ctk.CTkButton(
            form, text="Don't have an account? Register", height=32,
            font=UIConstants.FONT_SMALL, fg_color="transparent",
            text_color=UIConstants.PRIMARY, hover_color=UIConstants.CARD_BG_HOVER,
            command=self.on_switch_to_register
        )
        reg_btn.pack(fill="x", pady=(0, 20))

        # Demo credentials hint card
        hint_lbl = ctk.CTkLabel(
            card, text="🔑 Demo Credentials:\nAdmin: admin / admin123   •   User: testuser / test123",
            font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY, justify="center"
        )
        hint_lbl.pack(padx=20, pady=(0, 25))

    def toggle_show_password(self):
        if self.show_pwd_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="●")

    def handle_login(self):
        self.error_label.configure(text="")
        email = self.email_entry.get().strip()
        pwd = self.password_entry.get()

        if not email or not pwd:
            self.error_label.configure(text="Please enter both username/email and password.")
            return

        user = self.auth_service.login(email, pwd)
        if user:
            self.on_login_success(user)
        else:
            self.error_label.configure(text="Invalid credentials. Please try again.")
