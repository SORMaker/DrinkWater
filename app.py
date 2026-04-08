import rumps

class WaterTrackerApp(rumps.App):
    def __init__(self):
        # Initialize the app with default title
        super(WaterTrackerApp, self).__init__("WaterTracker", title="🥤 0/7")
        
        # Initialize data variables for tracking
        self.current_cups = 0
        self.target_cups = 7

    @rumps.clicked("➕ 喝一杯水")
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

    @rumps.clicked("🔄 重置今日进度")
    def reset_counter(self, _):
        # Reset the counter back to 0
        self.current_cups = 0
        self.update_title()

    # --- NEW FEATURE: Settings ---
    @rumps.clicked("⚙️ 设置目标")
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

    def update_title(self):
        # Dynamically update the text shown on the menu bar
        self.title = f"🥤 {self.current_cups}/{self.target_cups}"

if __name__ == "__main__":
    print("⏳ Starting WaterTracker with settings menu...")
    WaterTrackerApp().run()