import json
import os
from .BaseAnalyzer import HealthAnalyzer
class HeartRate(HealthAnalyzer):
    def __init__(self, Age, Gender):
        self.Age = Age
        self.Gender = Gender
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'HeartRateStatus.json')
        with open(json_path, 'r') as file:
            self.data = json.load(file)["resting_heart_rate_charts"]

    def GetAge(self):
        if 18 <= self.Age <= 25: 
            return "18-25"
        if 26 <= self.Age <= 35: 
            return "26-35"
        if 36 <= self.Age <= 45:
            return "36-45"
        if 46 <= self.Age <= 55: 
            return "46-55"
        if 56 <= self.Age <= 65: 
            return "56-65"
        else:
            return "65+"

    def GetStatus(self):
        GenderKey = "women" if self.Gender.lower() in ["female", "women"] else "men"
        AgeList = self.data[GenderKey]
        TargetAge = self.GetAge()
        AgeDict = next(rating for rating in AgeList if rating["age_range"] == TargetAge)
        if not AgeDict:
            return "Age range not found"

        def get_limit(value_str):
            if '-' in value_str:
                return int(value_str.split('-')[1])
            elif '+' in value_str:
                return 999 
            return int(value_str)
        
        if self.bpm <= int(AgeDict["athlete"].split('-')[1]): 
            return "Athlete"
        if self.bpm <= int(AgeDict["excellent"].split('-')[1]): 
            return "Excellent"
        if self.bpm <= int(AgeDict["good"].split('-')[1]): 
            return "Good"
        if self.bpm <= int(AgeDict["above_average"].split('-')[1]): 
            return "Above Average"
        if self.bpm <= int(AgeDict["average"].split('-')[1]): 
            return "Average"
        if self.bpm <= int(AgeDict["below_average"].split('-')[1]): 
            return "Below Average"
        else:
            return "Poor"
        

    def analyze(self, value):
        self.bpm = int(value)
        status = self.GetStatus() 
        return f"Your Heart Rate is {self.bpm} BPM. Status: {status}"

    def get_status_level(self, value):
        self.bpm = int(value)
        status = self.GetStatus()
        if status in ["Athlete", "Excellent", "Good"]:
            return "Normal"
        elif status in ["Above Average", "Average"]:
            return "Warning"
        else:
            return "Danger"
