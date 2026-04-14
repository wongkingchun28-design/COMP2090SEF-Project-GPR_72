import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(BASE_DIR, "user_profile.json")

class Base:
    def __init__(self, Name="User", Age=25, Gender="Male", Height=175, AthletesStatus=False, HealthGoals=500):
        self.Name = Name
        self.Age = Age
        self.Gender = Gender
        self.Height = Height
        self.AthletesStatus = AthletesStatus
        self.HealthGoals = HealthGoals

    def save(self):
        data = {
            "Name": self.Name,
            "Age": self.Age,
            "Gender": self.Gender,
            "Height": self.Height,
            "AthletesStatus": self.AthletesStatus,
            "HealthGoals": self.HealthGoals
        }
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load():
        if os.path.exists(PROFILE_PATH):
            try:
                with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    return Base(d["Name"], d["Age"], d["Gender"], d["Height"], d["AthletesStatus"], d["HealthGoals"])
            except Exception as e:
                print(f"Error loading profile: {e}")
        
        return Base("User", 25, "Male", 175, False, 500)