# 🏖️ Holiday Hacker

[![GitHub Release](https://img.shields.io/badge/Release-v1.0.0-00f0ff?style=for-the-badge&logo=github)](https://github.com/noelmathewsajan-sys/HOLIDAY-HACK/releases/latest)
[![Live Web App](https://img.shields.io/badge/Live_App-PWA-00ff66?style=for-the-badge&logo=googlechrome&logoColor=white)](https://noelmathewsajan-sys.github.io/HOLIDAY-HACK/)
[![Windows EXE](https://img.shields.io/badge/Windows-Standalone_EXE-0078D6?style=for-the-badge&logo=windows)](https://github.com/noelmathewsajan-sys/HOLIDAY-HACK/releases/download/v1.0.0/HolidayHacker.exe)

Welcome to **Holiday Hacker** — the ultimate productivity-avoidance tool! 
This application is designed to help you legally hack your calendar. By analyzing public holidays, weekends, and your available leave balance, Holiday Hacker finds the absolute best strategies to take the longest consecutive breaks while using the fewest possible leaves.

### 🚀 Direct App Downloads & Links:
- 💻 **[Download Standalone Windows App (HolidayHacker.exe)](https://github.com/noelmathewsajan-sys/HOLIDAY-HACK/releases/download/v1.0.0/HolidayHacker.exe)** *(Double-click to run on any PC! No Python or setup required)*
- 🌐 **[Open Live Web & Mobile App (PWA)](https://noelmathewsajan-sys.github.io/HOLIDAY-HACK/)** *(Open in any browser on Mobile or PC, or click "Install App")*
- 📦 **[Download Windows Release ZIP](https://github.com/noelmathewsajan-sys/HOLIDAY-HACK/releases/download/v1.0.0/HolidayHacker-v1.0.0-Windows.zip)**

---

## ✨ Features

- **⚡ Quick Hacks**: Zero-effort planning! Automatically scans the entire year and finds the absolute best "bang for your buck" holiday strategies using 2 leaves or less. Instantly book leaves with a single click.
- **🔍 Find Holidays**: Got a specific month in mind? Use the embedded interactive calendar grid to select a date range and discover custom holiday strategies for that period.
- **📅 Interactive Calendar**: A beautifully designed, full-screen calendar view to track all Working Days, Weekends, Public Holidays, and your Existing Leaves.
- **💾 Holiday Plans**: Save your favorite strategies and review them later.
- **📊 Admin Dashboard**: Manage users, oversee public holidays, and review company-wide leave schedules.
- **😎 Hacker Aesthetics**: A premium, custom-built UI featuring deep ink backgrounds with vibrant Neon Cyan, Green, and Purple accents powered by `CustomTkinter`.

---

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3.9+ and MySQL Server installed.

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   - Start your MySQL service (e.g., via XAMPP or native MySQL).
   - Import the database schema and sample data:
     ```bash
     mysql -u root -p < schema.sql
     ```
   - Default database credentials are configured in `HolidayHackerPython/database.py` (`localhost`, database: `holiday_hacker`, user: `root`, password: `""`).

---

## 💻 Running the Application

1. Navigate to the Python application directory:
   ```bash
   cd HolidayHackerPython
   ```
2. Start the application:
   ```bash
   python main.py
   ```
   *(Alternatively, on Windows double-click `HolidayHackerPython/run.bat`)*

3. **Default Credentials**:
   - **User**: `testuser` / `test123`
   - **Admin**: `admin` / `adminpassword`

---

## 💡 How It Works

The core algorithm (`HolidayOptimizer`) cross-references public holidays with weekends. It calculates the **Efficiency** of a break by dividing the total consecutive days off by the number of leaves you have to take. 

$$\text{Efficiency} = \frac{\text{Total Consecutive Days Off}}{\text{Leaves Used}}$$

If you take 1 leave to bridge a weekend and a public holiday for 4 days off, your efficiency is `4.0x`. The higher the efficiency, the better the hack!

---

*Disclaimer: We are not responsible for any side eyes you receive from HR.*
