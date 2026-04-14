from abc import ABC, abstractmethod

class BodyOutput(ABC):
    @abstractmethod
    def is_normal(self):
        pass

    @abstractmethod
    def description(self):
        pass

    def __str__(self):
        status = "normal" if self.is_normal() else "abnormal"
        return f"{self.__class__.__name__}: {self.description()} ({status})"


class Urine(BodyOutput):
    ColourCauses = { 
        "clear to pale yellow": ("Normal hydration", None),
        "red or pink": ("Blood, foods (beets, blackberries), medications", 
                        ["UTI", "kidney stones", "enlarged prostate", "cancer"]),
        "orange": ("Medications, vitamins, dehydration", 
                   ["liver/bile duct problems"]),
        "blue or green": ("Dyes, medications", 
                          ["familial benign hypercalcemia", "certain bacterial UTI"]),
        "dark brown or cola-colored": ("Foods (fava beans), medications, extreme exercise", 
                                       ["liver/kidney disorders", "hemorrhage", "porphyria"]),
        "cloudy or murky": (None, ["UTI", "kidney stones"])
    }

    def __init__(self, color):
        self.color = color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value.lower()
        self._causes, self._health_issues = self._get_causes_and_issues()

    def _get_causes_and_issues(self):
        for key, (causes, issues) in self.ColourCauses.items():
            if key in self._color:
                return causes, issues
        return "Unknown cause", None

    @property
    def causes(self):
        return self._causes

    @property
    def health_issues(self):
        return self._health_issues

    def is_normal(self):
        return "pale yellow" in self._color or "clear" in self._color

    def description(self):
        base = f"color: {self._color}"
        if self._causes:
            base += f", possible causes: {self._causes}"
        if self._health_issues:
            base += f", possible health issues: {', '.join(self._health_issues)}"
        return base


class Stool(BodyOutput):
    
    BristonTypes = {
        1: "Separate hard lumps (severe constipation)",
        2: "Lumpy and sausage-like (mild constipation)",
        3: "Sausage-shaped with cracks (normal)",
        4: "Smooth and soft (normal)",
        5: "Soft blobs with clear edges (lacking fiber)",
        6: "Mushy consistency (mild diarrhea)",
        7: "Liquid consistency (severe diarrhea)"
    }

    def __init__(self, bristol_type):
        self.bristol_type = bristol_type 

    @property
    def bristol_type(self):
        return self._bristol_type

    @bristol_type.setter
    def bristol_type(self, value):
        self._bristol_type = value
        self._desc = self.BristonTypes[value]

    @property
    def desc(self):
        return self._desc

    def is_normal(self):
        return self._bristol_type in (3, 4)

    def description(self):
        return f"type {self._bristol_type}: {self._desc}"

class Person:
    def __init__(self, urine_color, stool_type):
        self.urine = Urine(urine_color)
        self.stool = Stool(stool_type)

    def health_summary(self):
        summary = "Health summary:\n"
        summary += f"- {self.urine}\n"
        if not self.urine.is_normal() and self.urine.health_issues:
            summary += f"  Possible health issues: {', '.join(self.urine.health_issues)}\n"
        summary += f"- {self.stool}\n"
        if not self.stool.is_normal():
            summary += f"  This stool type indicates: {self.stool.desc}\n"
        return summary
