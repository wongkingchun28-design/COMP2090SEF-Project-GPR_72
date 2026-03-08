from abc import ABC, abstractmethod

class PSQIAnswers:
    def __init__(self, q1, q2, q3, q4, q5a, q5b, q5c, q5d, q5e, q5f, q5g, q5h, q5i, q5j, q6, q7, q8, q9):
        self._q1 = q1
        self._q2 = q2
        self._q3 = q3
        self._q4 = q4
        self._q5a = q5a
        self._q5b = q5b
        self._q5c = q5c
        self._q5d = q5d
        self._q5e = q5e
        self._q5f = q5f
        self._q5g = q5g
        self._q5h = q5h
        self._q5i = q5i
        self._q5j = q5j
        self._q6 = q6
        self._q7 = q7
        self._q8 = q8
        self._q9 = q9

    @property
    def q5j(self):
        return self._q5j

    @q5j.setter
    def q5j(self, value):
        if value is None or value == '':
            self._q5j = 0
        else:
            self._q5j = value


class PSQIComponent(ABC):        
    @abstractmethod
    def compute(self, answers):       
        pass

class PSQIDURAT(PSQIComponent):
    def compute(self, answers):
        q4 = float(answers._q4)
        if q4 >= 7:
            return 0
        elif q4 >= 6:
            return 1
        elif q4 >= 5:
            return 2
        else:
            return 3

class PSQIDISTB(PSQIComponent):
    def compute(self, answers):
        q5_values = [int(answers._q5b), int(answers._q5c), int(answers._q5d),
                    int(answers._q5e), int(answers._q5f), int(answers._q5g),
                    int(answers._q5h), int(answers._q5i), int(answers._q5j)]
        total = sum(q5_values)
        if total == 0:
            return 0
        elif total <= 9:
            return 1
        elif total <= 18:
            return 2
        else:
            return 3

class PSQILATEN(PSQIComponent):
    def compute(self, answers):
        q2 = int(answers._q2)
        q5a = int(answers._q5a)
        if q2 <= 15:
            q2_new = 0
        elif q2 <= 30:
            q2_new = 1
        elif q2 <= 60:
            q2_new = 2
        else:
            q2_new = 3
        total = q2_new + q5a
        if total == 0:
            return 0
        elif total <= 2:
            return 1
        elif total <= 4:
            return 2
        else:
            return 3

class PSQIDAYDYS(PSQIComponent):
    def compute(self, answers):
        q8 = int(answers._q8)
        q9 = int(answers._q9)
        total = q8 + q9
        if total == 0:
            return 0
        elif total <= 2:
            return 1
        elif total <= 4:
            return 2
        else:
            return 3

class PSQIHSE(PSQIComponent):
    def TimeDifference(self, start, end):
        StartHH, StartMM = map(int, start.split(':'))
        EndHH, EndMM = map(int, end.split(':'))
        StartTime = StartHH + StartMM / 60
        EndTime = EndHH + EndMM / 60
        diff = EndTime - StartTime
        if diff < 0:
            diff += 24
        return diff

    def compute(self, answers):
        q1 = answers._q1
        q3 = answers._q3
        q4 = float(answers._q4)
        sleeping_time = self.TimeDifference(q1, q3)
        tmphse = (q4 / sleeping_time) * 100
        if tmphse >= 85:
            return 0
        elif tmphse >= 75:
            return 1
        elif tmphse >= 65:
            return 2
        else:
            return 3

class PSQISLPQUAL(PSQIComponent):
    def compute(self, answers):
        return int(answers._q6)

class PSQIMEDS(PSQIComponent):
    def compute(self, answers):
        return int(answers._q7)

class PSQIScore:
    def __init__(self):
        self._components = [
            PSQIDURAT(), PSQIDISTB(), PSQILATEN(),
            PSQIDAYDYS(), PSQIHSE(), PSQISLPQUAL(),
            PSQIMEDS()
        ]

    def calculate(self, answers):       
        total = sum(comp.compute(answers) for comp in self._components)
        return total


        


    
