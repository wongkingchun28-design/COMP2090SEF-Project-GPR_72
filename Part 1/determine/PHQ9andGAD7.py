from abc import ABC, abstractmethod 

class PHQ9Answers:
    def __init__(self, q1, q2, q3, q4, q5, q6, q7, q8, q9):
        self._q1 = q1
        self._q2 = q2
        self._q3 = q3
        self._q4 = q4
        self._q5 = q5
        self._q6 = q6
        self._q7 = q7
        self._q8 = q8
        self._q9 = q9

class GAD7Answers:
    def __init__(self, q1, q2, q3, q4, q5, q6, q7):
        self._q1 = q1
        self._q2 = q2
        self._q3 = q3
        self._q4 = q4
        self._q5 = q5
        self._q6 = q6
        self._q7 = q7
        
class Component(ABC):
    @abstractmethod
    def compute(self, answers):
        pass

    @abstractmethod
    def interpret(self, answers):
        pass

class PHQ9Score(Component):
    def compute(self, answers: PHQ9Answers):
        return int(answers._q1 + answers._q2 + answers._q3 + answers._q4 + answers._q5 + answers._q6 + answers._q7 + answers._q8 + answers._q9)

    def interpret(self, answers: PHQ9Answers):
        score = self.compute(answers)
        if score <= 4:
            severity = "Minimal or none"
            comment = "Your score suggests you are experiencing few or no symptoms of depression. "
        elif score <= 9:
            severity = "Mild"
            comment = "Your score suggests mild symptoms of depression.\nYou might consider talking to someone you trust or a healthcare provider "
        elif score <= 14:
            severity = "Moderate"
            comment = "Your score suggests moderate symptoms of depression.\nIt may be helpful to speak with a healthcare provider about how you're feeling. "
        elif score <= 19:
            severity = "Moderately severe"
            comment = "Your score suggests moderately severe symptoms of depression.\nYou are recommended reaching out to a healthcare provider or mental health professional to discuss your symptoms and get support."
        else:  # 20-27
            severity = "Severe"
            comment = "Your score suggests severe symptoms of depression.\nIt is important to seek help from a healthcare provider or mental health professional as soon as possible. "
        result = {"score": score, "severity": severity, "comment": comment}
        
        if answers._q9 > 0:
            result["suicide_risk"] = True
            result["critical_action"] = "You indicated having thoughts of being better off dead or hurting yourself.\nThis is a serious symptom, and it's very important to talk to a healthcare provider or crisis line."
        else:
            result["suicide_risk"] = False
        
        return result
class GAD7Score(Component):
    def compute(self, answers: GAD7Answers):
        return int(answers._q1 + answers._q2 + answers._q3 + answers._q4 + answers._q5 + answers._q6 +  answers._q7)
    
    def interpret(self, answers: GAD7Answers):
        score = self.compute(answers)
        if score <= 4:
            severity = "Minimal or none"
            comment = "Your score suggests minimal anxiety symptoms."
        elif score <= 9:
            severity = "Mild"
            comment = "Your score suggests mild anxiety.\nIt might help to practice relaxation techniques or talk to someone if you feel worried. "
        elif score <= 14:
            severity = "Moderate"
            comment = "Your score suggests moderate anxiety.\nConsider speaking with a healthcare provider to discuss your feelings and learn ways to manage anxiety "
        else:  # 15-21
            severity = "Severe"
            comment = "Your score suggests severe anxiety.\nWe encourage you to reach out to a healthcare provider or mental health professional for support. "

        return {"score": score, "severity": severity, "comment": comment}
    
# Example usage
if __name__ == "__main__":
    phq = PHQ9Answers(2, 2, 1, 3, 0, 2, 1, 2, 2)
    phq_scorer = PHQ9Score()
    print(phq_scorer.interpret(phq))

    gad = GAD7Answers(2, 1, 2, 2, 1, 2, 2)
    gad_scorer = GAD7Score()
    print(gad_scorer.interpret(gad))

    
    
