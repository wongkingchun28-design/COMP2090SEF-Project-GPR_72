from .BaseAnalyzer import HealthAnalyzer

class weight(HealthAnalyzer):
    def __init__(self, gender, height): 
        self.gender = gender 
        self.height_m = height / 100 
        self.body_mass = 0
        self.BMI = 0

    def BMI_value(self):
        if self.height_m > 0:
            self.BMI = round(self.body_mass / (self.height_m ** 2), 2)
        return self.BMI
    
    def BMI_category(self):
        if self.BMI < 18.5:
            return 'You are Underweight' 
        if 18.5 <= self.BMI < 25:
            return 'You are Normal'
        if 25 <= self.BMI < 30:
            return 'You are Overweight'
        return 'You are Obese'

    def analyze(self, data):
        try:
            self.body_mass = float(data)
            bmi = self.BMI_value()
            status = self.BMI_category()
            return f"Weight: {self.body_mass}kg, BMI: {bmi}. Status: {status}."
        except:
            return "Invalid weight data."

    def get_status_level(self, value):
        try:
            self.body_mass = float(value)
            bmi = self.BMI_value()
            if 18.5 <= bmi < 25:
                return "Normal"
            return "Danger"
        except:
            return "Warning"
