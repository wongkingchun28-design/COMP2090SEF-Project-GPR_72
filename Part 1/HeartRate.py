from Base import Base
import json
class HeartRate(Base) :
    def __init__(self,bpm, Age, Gender):
        super().__init__(Age, Gender)
        self.bpm = bpm
        with open('HeartRateStatus.json', 'r') as file:
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
