import rumps
import json
import os
from datetime import datetime

class WaterTrackerApp(rumps.App):
    def __init__(self):

        self.load_data()

        try:
            self.last_reset_date = datetime.strptime(self.last_reset_date, "%Y-%m-%d").date()
        except TypeError:
            self.last_reset_date = datetime.now().date()
        
        self.last_reminder_hour = datetime.now().hour
        self.last_reminder_interval = datetime.now()

        # Initialize the app with default title
        super(WaterTrackerApp, self).__init__(
            "WaterTracker", 
            menu=[
                "Drink Water",          
                "Reset",       
                None,
                ("History", ["View Full Report"]), 
                None,                 
                ("Settings", ["Set Goal", "Auto Reminder", "Interval Reminder"])
            ]
        )


        self.reset_timer = rumps.Timer(self.check_daily_reset, 5)
        self.reset_timer.start()

        self.reminder_timer = rumps.Timer(self.check_reminder_hour, 60)
        self.reminder_timer.start()

        self.reminder_interval_timer = rumps.Timer(self.check_reminder_interval, self.interval_time)
        self.reminder_interval_timer.start()

        self.menu["Settings"]["Auto Reminder"].state = self.auto_reminder_on
        self.menu["Settings"]["Interval Reminder"].state = self.interval_reminder_on

        self.menu["Drink Water"].title = "🥤 咕噜咕噜 (+1)"
        self.menu["Reset"].title = "💥 清空今日进度"
        self.menu["History"].title = "📊 历史记录"
        self.menu["History"]["View Full Report"].title = "📈 查看完整报告..."
        self.menu["Settings"].title = "🧰 偏好设置"
        self.menu["Settings"]["Set Goal"].title = "🏆 设定喝水目标"
        self.menu["Settings"]["Auto Reminder"].title = "⏰ 整点智能提醒"
        self.menu["Settings"]["Interval Reminder"].title = "⏱️ 间隔周期提醒"

        self.update_title()
        self.update_history_menu()

    def check_daily_reset(self, _):
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            yesterday_str = str(self.last_reset_date)
            self.history[yesterday_str] = self.current_cups

            self.current_cups = 0
            self.last_reset_date = current_date

            self.update_title()
            self.update_history_menu()
            self.save_data()
            rumps.notification(
                title="New Day!☀️", 
                subtitle="Water Progress has been reset", 
                message="Remember to stay hydrated today!"
            )

    def check_reminder_hour(self, _):
        if not self.menu["Settings"]["Auto Reminder"].state:
            return
        current_time = datetime.now()

        if current_time.minute == 0 and current_time.hour != self.last_reminder_hour:
            self.last_reminder_hour = current_time.hour
            rumps.notification(
                title="Hydration Time! 💧",
                subtitle="Hourly Water Reminder",
                message="Take a short break and drink a glass of water."
            )

    def check_reminder_interval(self, _):
        if not self.menu["Settings"]["Interval Reminder"].state:
            return
        current_time = datetime.now()

        if current_time != self.last_reminder_interval:
            self.last_reminder_interval = current_time
            rumps.notification(
                title="Hydration Time! 💧",
                subtitle="Hourly Water Reminder",
                message="Take a short break and drink a glass of water."
            )

    @rumps.clicked("Drink Water")
    def drink_water(self, _):
        # Increment the counter
        self.current_cups += 1
        self.update_title()
        self.save_data()
        
        # Trigger notification when target is reached
        if self.current_cups == self.target_cups:
            rumps.notification(
                title="Goal Reached! 🎉", 
                subtitle="Great job!", 
                message="You have drank all your water for today."
            )

    @rumps.clicked("Reset")
    def reset_counter(self, _):
        # Reset the counter back to 0
        self.current_cups = 0
        self.update_title()
        self.save_data()

    # --- NEW FEATURE: Settings ---
    @rumps.clicked("Settings", "Set Goal")
    def set_target(self, _):
        # Create a simple input window
        window = rumps.Window(
            message="Enter your daily goal (number of cups):",
            title="Settings",
            default_text=str(self.target_cups),
            dimensions=(200, 20) # Width, Height of the input box
        )
        response = window.run()
        
        # Check if user clicked OK (response.clicked is True)
        if response.clicked:
            try:
                # Convert input to integer
                new_target = int(response.text)
                if new_target > 0:
                    self.target_cups = new_target
                    self.update_title()
                    self.save_data()
                else:
                    # Show an alert if number is 0 or negative
                    rumps.alert("Invalid Input", "Please enter a number greater than 0.")
            except ValueError:
                # Show an alert if input is not a number (e.g., text)
                rumps.alert("Invalid Input", "Please enter a valid number.")
    
    @rumps.clicked("Settings", "Auto Reminder")
    def set_auto_reminder(self, sender):
        if sender.state == 1:
            return
        sender.state = 1
        self.menu["Settings"]["Interval Reminder"].state = 0
        self.save_data()


    @rumps.clicked("Settings", "Interval Reminder")
    def set_interval_reminder(self, sender):
        if sender.state == 1:
            return
        sender.state = 1
        # Create a simple input window
        window = rumps.Window(
            message="Enter your new interval:",
            title="Interval Setting",
            default_text=str(self.interval_time),
            dimensions=(200, 20) # Width, Height of the input box
        )
        response = window.run()
        
        # Check if user clicked OK (response.clicked is True)
        if response.clicked:
            try:
                # Convert input to integer
                new_interval_time = int(response.text)
                if new_interval_time > 0:
                    self.interval_time = new_interval_time
                    self.reminder_interval_timer.interval = self.interval_time
                else:
                    # Show an alert if number is 0 or negative
                    rumps.alert("Invalid Input", "Please enter a number greater than 0.")
            except ValueError:
                # Show an alert if input is not a number (e.g., text)
                rumps.alert("Invalid Input", "Please enter a valid number.")
        self.menu["Settings"]["Auto Reminder"].state = 0
        self.save_data()

    @rumps.clicked("History", "View Full Report")
    def show_history_dialog(self, _):
        if not self.history:
            rumps.alert(title="历史报告", message="目前还没有历史数据哦，今天多喝点水吧！")
            return
        
        total_days = len(self.history)
        total_cups_all_time = sum(self.history.values())
        avg_cups = round(total_cups_all_time / total_days, 1)

        report_text = (
            f"📅 记录天数: {total_days} 天\n"
            f"🌊 累计饮水: {total_cups_all_time} 杯\n"
            f"⚖️ 日均饮水: {avg_cups} 杯/天\n\n"
            f"Keep up the good work! 🚀"
        )
        
        rumps.alert(title="📊 饮水历史报告", message=report_text)

    def update_title(self):
        # Dynamically update the text shown on the menu bar
        self.title = f"🥤 {self.current_cups}/{self.target_cups}"

    def load_data(self):
        self.data_file = os.path.expanduser("~/.watertracker.json")

        self.current_cups = 0
        self.target_cups = 3
        self.last_reset_date = str(datetime.now().date())
        self.interval_time = 3600
        self.auto_reminder_on = 1
        self.interval_reminder_on = 0
        self.history = {}

        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_cups = data.get("current_cups", self.current_cups)
                    self.target_cups = data.get("target_cups", self.target_cups)
                    self.last_reset_date = data.get("last_reset_date", self.last_reset_date)
                    self.interval_time = data.get("interval_time", self.interval_time)
                    self.auto_reminder_on = data.get("auto_reminder_on", self.auto_reminder_on)
                    self.interval_reminder_on = data.get("interval_reminder_on", self.interval_reminder_on)
                    self.history = data.get("history", self.history)
            except Exception as e:
                print(f"Failed to load date: {e}")

    def save_data(self):
        data = {
            "current_cups": self.current_cups,
            "target_cups": self.target_cups,
            "last_reset_date": str(self.last_reset_date),
            "auto_reminder_on": self.menu["Settings"]["Auto Reminder"].state,
            "interval_reminder_on": self.menu["Settings"]["Interval Reminder"].state,
            "history": self.history
        }

        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save data: {e}")

    def update_history_menu(self):
        for item in list(self.menu["History"].keys()):
            if item != "View Full Report":
                del self.menu["History"][item]

        if not self.history:
            self.menu["History"].add(rumps.MenuItem("暂无记录(No data yet)"))
            return

        self.menu["History"].add(rumps.separator)

        sorted_dates = sorted(self.history.keys(), reverse=True)[:7]

        for date_str in sorted_dates:
            cups = self.history[date_str]
            short_date = date_str[-5:]

            item_title = f"{short_date}: 💧 {cups} 杯"

            menu_item = rumps.MenuItem(item_title, callback=None)
            self.menu["History"].add(menu_item)


if __name__ == "__main__":
    print("⏳ Starting WaterTracker with settings menu...")
    WaterTrackerApp().run()