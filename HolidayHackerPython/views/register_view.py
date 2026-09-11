import customtkinter as ctk
from views.ui_constants import UIConstants
from services import AuthService
from typing import Callable
import tkinter.messagebox as messagebox

class RegisterView(ctk.CTkFrame):
    def __init__(self, master, on_register_success: Callable, on_switch_to_login: Callable):
        super().__init__(master, fg_color=UIConstants.BG_COLOR)
        self.on_register_success = on_register_success
        self.on_switch_to_login = on_switch_to_login
        self.auth_service = AuthService()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_ui()

    def build_ui(self):
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0)

        card = ctk.CTkFrame(center_frame, fg_color=UIConstants.CARD_BG, corner_radius=16, width=420)
        card.pack(padx=20, pady=20)

        ctk.CTkLabel(card, text="🏖️", font=("Segoe UI Emoji", 40)).pack(pady=(25, 2))
        ctk.CTkLabel(card, text="CREATE ACCOUNT", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY).pack(pady=(0, 2))
        ctk.CTkLabel(card, text="Join the Holiday Hacker club", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(pady=(0, 20))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=35, pady=(0, 10))

        ctk.CTkLabel(form, text="Full Name", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.name_entry = ctk.CTkEntry(form, height=38, font=UIConstants.FONT_BODY, placeholder_text="e.g. Alex Hacker")
        self.name_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="Username / Email", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.email_entry = ctk.CTkEntry(form, height=38, font=UIConstants.FONT_BODY, placeholder_text="e.g. alex")
        self.email_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="Password", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.password_entry = ctk.CTkEntry(form, height=38, font=UIConstants.FONT_BODY, show="●", placeholder_text="At least 4 characters")
        self.password_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="Confirm Password", font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.confirm_entry = ctk.CTkEntry(form, height=38, font=UIConstants.FONT_BODY, show="●", placeholder_text="Re-type password")
        self.confirm_entry.pack(fill="x", pady=(0, 10))
        self.confirm_entry.bind("<Return>", lambda event: self.handle_register())

        self.error_label = ctk.CTkLabel(form, text="", font=UIConstants.FONT_SMALL, text_color=UIConstants.DANGER)
        self.error_label.pack(anchor="w", pady=(0, 10))

        reg_btn = ctk.CTkButton(
            form, text="Create Account", height=42,
            font=UIConstants.FONT_BODY_BOLD, fg_color=UIConstants.SUCCESS,
            text_color="#000000", hover_color="#00C853",
            command=self.handle_register
        )
        reg_btn.pack(fill="x", pady=(5, 12))

        back_btn = ctk.CTkButton(
            form, text="Already have an account? Sign In", height=32,
            font=UIConstants.FONT_SMALL, fg_color="transparent",
            text_color=UIConstants.PRIMARY, hover_color=UIConstants.CARD_BG_HOVER,
            command=self.on_switch_to_login
        )
        back_btn.pack(fill="x", pady=(0, 25))

    def handle_register(self):
        self.error_label.configure(text="")
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        pwd = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not name or not email or not pwd:
            self.error_label.configure(text="All fields are required.")
            return

        if pwd != confirm:
            self.error_label.configure(text="Passwords do not match.")
            return

        try:
            user = self.auth_service.register(name, email, pwd)
            if user:
                messagebox.showinfo("Success", "Account created successfully! 🎉 You have 10 available leaves.")
                self.on_register_success(user)
        except ValueError as e:
            self.error_label.configure(text=str(e))
        except Exception as e:
            self.error_label.configure(text=f"Registration failed: {e}")
