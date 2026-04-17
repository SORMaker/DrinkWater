import rumps
import json
import os
from datetime import datetime

class WaterTrackerApp(rumps.App):
    def __init__(self):

        # Initialize the app with default title
        super(WaterTrackerApp, self).__init__(
            "WaterTracker", 
            menu=[
                "Drink Water",          # 第1位
                "Reset",        # 第2位
                None,                  # 🌟 魔法：写入 None 会在菜单里生成一条灰色的分割线！
                ("Settings", ["Set Goal", "Auto Reminder", "Interval Reminder"]) # 排在最后
            ]
        )

        # Initialize data variables for tracking
        self.current_cups = 0
        self.target_cups = 3

        self.last_reset_date = datetime.now().date()
        self.last_reminder_hour = datetime.now().hour
        self.last_reminder_interval = datetime.now()

        self.reset_timer = rumps.Timer(self.check_daily_reset, 5)
        self.reset_timer.start()

        self.reminder_timer = rumps.Timer(self.check_reminder_hour, 60)
        self.reminder_timer.start()

        self.interval_time = 3600
        self.reminder_interval_timer = rumps.Timer(self.check_reminder_interval, self.interval_time)
        self.reminder_interval_timer.start()

        self.menu["Settings"]["Auto Reminder"].state = 1
        self.menu["Settings"]["Interval Reminder"].state = 0

        self.menu["Drink Water"].title = "🥤 咕噜咕噜 (+1)"
        self.menu["Reset"].title = "💥 清空今日进度"
        self.menu["Settings"].title = "🧰 偏好设置"
        self.menu["Settings"]["Set Goal"].title = "🏆 设定喝水目标"
        self.menu["Settings"]["Auto Reminder"].title = "⏰ 整点智能提醒"
        self.menu["Settings"]["Interval Reminder"].title = "⏱️ 间隔周期提醒"


        self.update_title()

    def check_daily_reset(self, _):
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.current_cups = 0
            self.last_reset_date = current_date
            self.update_title()
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

    def update_title(self):
        # Dynamically update the text shown on the menu bar
        self.title = f"🥤 {self.current_cups}/{self.target_cups}"

if __name__ == "__main__":
    print("⏳ Starting WaterTracker with settings menu...")
    WaterTrackerApp().run()