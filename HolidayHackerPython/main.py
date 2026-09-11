import customtkinter as ctk
from database import DatabaseConnection
from services import HolidayService, LeaveService, PlanService, AuthService
from views.dashboard import DashboardFrame
import tkinter.messagebox as messagebox
import tkinter as tk
import sys

class HolidayHackerApp:
    def __init__(self):
        # 1. Test DB Connection
        db = DatabaseConnection()
        if not db.test_connection():
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Database Error",
                "Cannot connect to MySQL database 'holiday_hacker'.\n"
                "Please ensure MySQL is running (e.g. XAMPP) and accessible at localhost:3306."
            )
            sys.exit(1)

        # 2. Configure CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Holiday Hacker — Desktop Edition")
        self.root.geometry("1220x760")
        self.root.minsize(960, 620)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Initialize core services
        self.holiday_service = HolidayService()
        self.leave_service = LeaveService()
        self.plan_service = PlanService()
        self.auth_service = AuthService()

        self.current_frame = None

        # Fetch or create guest user
        users = self.auth_service.user_service.find_all_users()
        guest_user = next((u for u in users if u.email == "guest@holidayhacker.local"), None)
        
        if not guest_user:
            try:
                guest_user = self.auth_service.register("Guest", "guest@holidayhacker.local", "1234")
            except Exception:
                guest_user = self.auth_service.login("guest@holidayhacker.local", "1234")
                
        self.show_dashboard(guest_user)

    def _clear_current_frame(self):
        if self.current_frame:
            self.current_frame.grid_forget()
            self.current_frame.destroy()
            self.current_frame = None

    def show_dashboard(self, user):
        self._clear_current_frame()
        self.current_frame = DashboardFrame(
            self.root,
            user=user,
            holiday_service=self.holiday_service,
            leave_service=self.leave_service,
            plan_service=self.plan_service,
            auth_service=self.auth_service,
            on_logout=lambda: None
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def run(self):
        self.root.mainloop()

def main():
    app = HolidayHackerApp()
    app.run()

if __name__ == "__main__":
    main()
