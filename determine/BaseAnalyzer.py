from abc import ABC, abstractmethod

class HealthAnalyzer(ABC):
    @abstractmethod
    def analyze(self, data):
        pass

    @abstractmethod
    def get_status_level(self, value):
        pass