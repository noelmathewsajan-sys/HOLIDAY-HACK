import customtkinter as ctk
import calendar
from datetime import date, timedelta
from views.ui_constants import UIConstants
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog

class CalendarView(ctk.CTkFrame):
    def __init__(self, master, user, holiday_service, leave_service):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.holiday_service = holiday_service
        self.leave_service = leave_service
        
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        
        self.recommended_dates = set()
        
        self.build_ui()
        
    def set_recommended_dates(self, dates, highlight_range=None):
        self.recommended_dates.clear()
        if dates:
            self.recommended_dates.update(dates)
        self.highlight_range = highlight_range
        self.refresh_grid()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(header, text="📅 Calendar", font=UIConstants.FONT_HEADING, text_color=UIConstants.PRIMARY)
        title.pack(side="left")
        
        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right")
        
        prev_btn = ctk.CTkButton(nav, text="◀ Prev", width=70, fg_color=UIConstants.CARD_BG, hover_color=UIConstants.SIDEBAR_BG, command=self.prev_month)
        prev_btn.pack(side="left", padx=4)
        
        self.month_label = ctk.CTkLabel(nav, text="", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_PRIMARY)
        self.month_label.pack(side="left", padx=8)
        
        next_btn = ctk.CTkButton(nav, text="Next ▶", width=70, fg_color=UIConstants.CARD_BG, hover_color=UIConstants.SIDEBAR_BG, command=self.next_month)
        next_btn.pack(side="left", padx=4)

        today_btn = ctk.CTkButton(nav, text="Today", width=60, fg_color=UIConstants.PRIMARY, text_color="#000", hover_color=UIConstants.PRIMARY_HOVER, command=self.go_today)
        today_btn.pack(side="left", padx=6)

        # Today & Next Holiday Banner
        today = date.today()
        all_holidays = self.holiday_service.get_all_holidays()
        upcoming = [h for h in all_holidays if h.holiday_date >= today]
        upcoming.sort(key=lambda h: h.holiday_date)

        is_weekend = today.weekday() >= 5
        today_h = next((h for h in all_holidays if h.holiday_date == today), None)
        if today_h:
            t_status = f"🎉 Today is {today_h.holiday_name}!"
        elif is_weekend:
            t_status = "🛌 Weekend (Day Off)"
        else:
            t_status = "💼 Working Day"

        if upcoming:
            next_h = upcoming[0]
            days_left = (next_h.holiday_date - today).days
            count_txt = "Today! 🎉" if days_left == 0 else ("Tomorrow! 🚀" if days_left == 1 else f"in {days_left} days")
            next_txt = f"🎉 Next Holiday: {next_h.holiday_name} ({count_txt})"
        else:
            next_txt = "No more upcoming holidays recorded this year."

        banner_frame = ctk.CTkFrame(self, fg_color=UIConstants.CARD_BG, corner_radius=8)
        banner_frame.pack(fill="x", pady=(0, 12))
        b_inner = ctk.CTkFrame(banner_frame, fg_color="transparent")
        b_inner.pack(fill="x", padx=14, pady=8)

        ctk.CTkLabel(b_inner, text=f"📅 Today: {today.strftime('%A, %d %B %Y')} • {t_status}", font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.SUCCESS).pack(side="left")
        ctk.CTkLabel(b_inner, text=next_txt, font=UIConstants.FONT_BODY, text_color=UIConstants.PRIMARY).pack(side="right")
        
        # Legend
        legend = ctk.CTkFrame(self, fg_color="transparent")
        legend.pack(fill="x", side="bottom", pady=10)
        
        def create_legend_item(parent, text, color):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(side="left", padx=10)
            swatch = ctk.CTkFrame(f, width=16, height=16, fg_color=color, corner_radius=4)
            swatch.pack(side="left")
            lbl = ctk.CTkLabel(f, text=text, font=UIConstants.FONT_SMALL, text_color=UIConstants.TEXT_SECONDARY)
            lbl.pack(side="left", padx=(5, 0))
            
        create_legend_item(legend, "Working Day", UIConstants.CAL_WORKING)
        create_legend_item(legend, "Weekend", UIConstants.CAL_WEEKEND)
        create_legend_item(legend, "Public Holiday", UIConstants.CAL_HOLIDAY)
        create_legend_item(legend, "Recommended", UIConstants.CAL_RECOMMENDED)
        create_legend_item(legend, "Existing Leave", UIConstants.CAL_EXISTING)
        
        # Grid Container
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        
        self.refresh_grid()
        
    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_grid()
        
    def go_today(self):
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
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
        
        # Configure columns
        for i in range(7):
            self.grid_frame.grid_columnconfigure(i, weight=1)
            
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, dow in enumerate(days_of_week):
            lbl = ctk.CTkLabel(self.grid_frame, text=dow, font=UIConstants.FONT_BODY_BOLD, text_color=UIConstants.TEXT_SECONDARY)
            lbl.grid(row=0, column=i, pady=(0, 10))
            
        # Get data
        _, num_days = calendar.monthrange(self.current_year, self.current_month)
        first_date = date(self.current_year, self.current_month, 1)
        last_date = date(self.current_year, self.current_month, num_days)
        
        holidays = self.holiday_service.get_holidays_in_range(first_date, last_date)
        holiday_map = {h.holiday_date: h.holiday_name for h in holidays}
        
        leaves = self.leave_service.get_user_leaves(self.user.id, first_date, last_date)
        leave_map = {l.leave_date: l.id for l in leaves}
        
        start_dow = first_date.weekday() # 0 = Mon
        
        row = 1
        col = start_dow
        
        today = date.today()

        for day in range(1, num_days + 1):
            curr_date = date(self.current_year, self.current_month, day)
            is_today = (curr_date == today)
            
            color = UIConstants.CAL_WORKING
            if curr_date in self.recommended_dates:
                color = UIConstants.CAL_RECOMMENDED
            elif curr_date in leave_map:
                color = UIConstants.CAL_EXISTING
            elif curr_date in holiday_map:
                color = UIConstants.CAL_HOLIDAY
            elif curr_date.weekday() >= 5:
                color = UIConstants.CAL_WEEKEND
                
            border_w = 0
            border_c = UIConstants.BG_COLOR
            if hasattr(self, 'highlight_range') and self.highlight_range:
                if self.highlight_range[0] <= curr_date <= self.highlight_range[1]:
                    border_w = 2
                    border_c = UIConstants.SUCCESS
            elif is_today:
                border_w = 2
                border_c = UIConstants.PRIMARY
                
            cell = ctk.CTkFrame(self.grid_frame, fg_color=color, border_width=border_w, border_color=border_c, corner_radius=8, height=60)
            cell.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            cell.grid_propagate(False)
            
            lbl_txt = f"{day}\nTODAY" if is_today else str(day)
            lbl_color = UIConstants.PRIMARY if is_today else UIConstants.TEXT_PRIMARY
            lbl = ctk.CTkLabel(cell, text=lbl_txt, font=UIConstants.FONT_BODY_BOLD, text_color=lbl_color)
            lbl.place(relx=0.5, rely=0.5, anchor="center")
            
            # Click event bindings
            def on_click(event, d=curr_date):
                self.handle_click(d, leave_map, holiday_map)
                
            cell.bind("<Button-1>", on_click)
            lbl.bind("<Button-1>", on_click)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
                
    def handle_click(self, d: date, leave_map: dict, holiday_map: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Date Info")
        dialog.geometry("300x200")
        dialog.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(dialog, text=f"Date: {d.strftime('%Y-%m-%d')}", font=UIConstants.FONT_BODY_BOLD)
        lbl.pack(pady=10)
        
        if d in leave_map:
            def remove():
                self.leave_service.delete_leave(leave_map[d])
                dialog.destroy()
                self.refresh_grid()
            btn = ctk.CTkButton(dialog, text="Remove Leave", fg_color=UIConstants.CAL_RECOMMENDED, command=remove)
            btn.pack(pady=10)
        elif d in holiday_map:
            txt = holiday_map.get(d, "")
            ctk.CTkLabel(dialog, text=txt, text_color=UIConstants.CAL_HOLIDAY).pack()
            def remove_hol():
                holidays = self.holiday_service.get_holidays_in_range(d, d)
                if holidays:
                    self.holiday_service.delete_holiday(holidays[0].id)
                dialog.destroy()
                self.refresh_grid()
            btn = ctk.CTkButton(dialog, text="Remove Holiday", fg_color=UIConstants.DANGER, command=remove_hol)
            btn.pack(pady=10)
        elif d.weekday() < 5:
            def add_leave():
                try:
                    self.leave_service.add_leave(self.user.id, d)
                    dialog.destroy()
                    self.refresh_grid()
                except Exception as ex:
                    messagebox.showwarning("Notice", str(ex))

            def add_holiday():
                dialog.attributes("-topmost", False) # So simpledialog works correctly
                name = simpledialog.askstring("Add Holiday", "Enter Holiday Name:", parent=self)
                if name:
                    try:
                        self.holiday_service.add_holiday(name, d)
                        dialog.destroy()
                        self.refresh_grid()
                    except Exception as ex:
                        messagebox.showwarning("Notice", str(ex))
                else:
                    dialog.attributes("-topmost", True)

            btn = ctk.CTkButton(dialog, text="Add Personal Leave", fg_color=UIConstants.SUCCESS, text_color="#000000", hover_color="#00C853", command=add_leave)
            btn.pack(pady=5)
            btn2 = ctk.CTkButton(dialog, text="Add Public Holiday", fg_color=UIConstants.CAL_HOLIDAY, text_color="#000000", command=add_holiday)
            btn2.pack(pady=5)
        else:
            ctk.CTkLabel(dialog, text="Weekend").pack()
            ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=10)
