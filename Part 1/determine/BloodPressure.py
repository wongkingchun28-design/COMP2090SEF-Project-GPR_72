from .BaseAnalyzer import HealthAnalyzer
class blood_pressure(HealthAnalyzer):
    def __init__(self):
        self.history_records = []
    
    def _interpret_bp(self, sbp, dbp):
        if sbp < 120 and dbp < 80:
            return 'NORMAL'
        elif 120 <= sbp <= 129 and dbp < 80:
            return 'ELEVATED'
        elif 130 <= sbp <= 139 or 80 <= dbp <= 89:
            return 'STAGE 1 HYPERTENSION'
        elif 140 <= sbp <= 180 or 90 <= dbp <= 120:
            return 'STAGE 2 HYPERTENSION'
        else:
            return 'SEVERE HYPERTENSION (Emergency!)'


    def analyze(self, data):
        try:
            clean_data = data.replace("mmHg", "").strip()
            sbp_str, dbp_str = clean_data.split("/")
            sbp, dbp = int(sbp_str), int(dbp_str)
            status = self._interpret_bp(sbp, dbp)
            self.history_records.append({"sbp": sbp, "dbp": dbp, "status": status})

            return f"Blood Pressure: {sbp}/{dbp} mmHg. Result: {status}."
        except Exception:
            return "Invalid format. Please use 'Systolic/Diastolic' (e.g., 120/80)."

    def get_status_level(self, value):
        try:
            sbp = int(value.split("/")[0])
            if sbp < 120: return "Normal"
            if sbp < 140: return "Warning"
            return "Danger"
        except:
            return "Warning"
