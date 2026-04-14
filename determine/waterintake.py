from .BaseAnalyzer import HealthAnalyzer
class water_intake(HealthAnalyzer):
    def __init__(self, weight, exercise_mins=0):
        self.weight = weight
        self.exercise = exercise_mins
        self.goal = weight * 30 + (exercise_mins / 30) * 350

    def analyze(self, data):
        try:
            current_intake = float(data)
            if current_intake >= self.goal:
                return f"Great! You've reached your goal of {self.goal:.0f}ml. (Current: {current_intake}ml)"
            else:
                deficit = self.goal - current_intake
                return f"Hydration needed: You are {deficit:.0f}ml short of your daily goal ({self.goal:.0f}ml)."
        except:
            return "Invalid input. Please enter a number for water intake."

    def get_status_level(self, value):
        try:
            if float(value) >= self.goal:
                return "Normal"
            return "Warning"
        except:
            return "Warning"
