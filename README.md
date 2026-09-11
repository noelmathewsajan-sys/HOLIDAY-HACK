# 🏖️ Holiday Hacker

Welcome to **Holiday Hacker** — the ultimate productivity-avoidance tool! 
This application is designed to help you legally hack your calendar. By analyzing public holidays, weekends, and your available leave balance, Holiday Hacker finds the absolute best strategies to take the longest consecutive breaks while using the fewest possible leaves.

## ✨ Features

- **⚡ Quick Hacks**: Zero-effort planning! Automatically scans the entire year and finds the absolute best "bang for your buck" holiday strategies using 2 leaves or less. Instantly book leaves with a single click.
- **🔍 Find Holidays**: Got a specific month in mind? Use the embedded interactive calendar grid to select a date range and discover custom holiday strategies for that period.
- **📅 Interactive Calendar**: A beautifully designed, full-screen calendar view to track all Working Days, Weekends, Public Holidays, and your Existing Leaves.
- **💾 Holiday Plans**: Save your favorite strategies and review them later.
- **😎 Hacker Aesthetics**: A premium, custom-built UI featuring deep ink backgrounds and striking Neon Cyan, Green, and Purple accents. 

## 🚀 Getting Started

The latest version of the application is built in Python using the `CustomTkinter` UI framework.

### Prerequisites

Make sure you have Python installed, along with the required libraries:

```bash
pip install customtkinter mysql-connector-python
```

### Running the App

1. Navigate to the Python application directory:
   ```bash
   cd HolidayHackerPython
   ```
2. Run the main file:
   ```bash
   python main.py
   ```

*(Note: There is also a legacy Java version of the application in the `HolidayHacker/` directory).*

## 💡 How It Works

The core algorithm (`HolidayOptimizer`) cross-references public holidays with weekends. It calculates the "Efficiency" of a break by dividing the total consecutive days off by the number of leaves you have to take. 

If you take 1 leave to bridge a weekend and a public holiday for 4 days off, your efficiency is `4.0x`. The higher the efficiency, the better the hack!

---
*Disclaimer: We are not responsible for any side eyes you receive from HR.*
