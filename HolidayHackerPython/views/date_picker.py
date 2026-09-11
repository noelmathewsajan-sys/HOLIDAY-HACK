import customtkinter as ctk
import calendar
from datetime import date
from views.ui_constants import UIConstants

class DatePickerPopup(ctk.CTkToplevel):
    def __init__(self, master, on_date_selected, initial_date=None):
        super().__init__(master)
        self.title("Select Date")
        self.geometry("320x350")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=UIConstants.BG_COLOR)
        
        self.on_date_selected = on_date_selected
        
        if initial_date:
            self.current_year = initial_date.year
            self.current_month = initial_date.month
            self.selected_date = initial_date
        else:
            today = date.today()
            self.current_year = today.year
            self.current_month = today.month
            self.selected_date = today
            
        self.build_ui()
        
    def build_ui(self):
        # Header
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", pady=(15, 10), padx=10)
        
        prev_btn = ctk.CTkButton(nav, text="◀", width=40, fg_color=UIConstants.CARD_BG, hover_color=UIConstants.SIDEBAR_BG, command=self.prev_month)
        prev_btn.pack(side="left")
        
        self.month_label = ctk.CTkLabel(nav, text="", font=UIConstants.FONT_HEADING, text_color=UIConstants.TEXT_PRIMARY)
        self.month_label.pack(side="left", expand=True)
        
        next_btn = ctk.CTkButton(nav, text="▶", width=40, fg_color=UIConstants.CARD_BG, hover_color=UIConstants.SIDEBAR_BG, command=self.next_month)
        next_btn.pack(side="right")
        
        # Grid Container
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.refresh_grid()
        
    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_grid()
        
    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_grid()
        
    def refresh_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        month_name = calendar.month_name[self.current_month]
        self.month_label.configure(text=f"{month_name} {self.current_year}")
        
        for i in range(7):
            self.grid_frame.grid_columnconfigure(i, weight=1)
            
        days_of_week = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, dow in enumerate(days_of_week):
            lbl = ctk.CTkLabel(self.grid_frame, text=dow, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_SECONDARY)
            lbl.grid(row=0, column=i, pady=(0, 5))
            
        _, num_days = calendar.monthrange(self.current_year, self.current_month)
        first_date = date(self.current_year, self.current_month, 1)
        start_dow = first_date.weekday()
        
        row = 1
        col = start_dow
        
        for day in range(1, num_days + 1):
            curr_date = date(self.current_year, self.current_month, day)
            
            is_selected = (curr_date == self.selected_date)
            bg_color = UIConstants.PRIMARY if is_selected else UIConstants.CARD_BG
            text_color = "#000000" if is_selected else UIConstants.TEXT_PRIMARY
            hover = UIConstants.PRIMARY_HOVER if is_selected else UIConstants.CARD_BG_HOVER
            
            btn = ctk.CTkButton(
                self.grid_frame, 
                text=str(day), 
                width=35, height=35,
                fg_color=bg_color,
                text_color=text_color,
                hover_color=hover,
                font=UIConstants.FONT_BODY,
                command=lambda d=curr_date: self.select_date(d)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
                
    def select_date(self, d: date):
        self.selected_date = d
        date_str = d.strftime("%Y-%m-%d")
        if self.on_date_selected:
            self.on_date_selected(date_str)
        self.destroy()
