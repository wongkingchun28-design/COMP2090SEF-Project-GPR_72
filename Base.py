from datetime import datetime
class Base:
    def __init__(self, Name , Age , Gender, Height, AthletesStatus , HealthGoals):
        self.Name = Name
        self.Age = Age
        self.Gender = Gender
        self.Height = Height
        self.AthletesStatus = AthletesStatus
        self.HealthGoals = HealthGoals
        self.TimeStamp = datetime.now()