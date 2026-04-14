import matplotlib.pyplot as plt
import os
import re
from datetime import datetime

class HealthGraphPlotter:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.data = {} 

    def parse_csv(self):
        if not os.path.exists(self.csv_path):
            print("CSV file not found.")
            return

        with open(self.csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines[2:]:
            line = line.strip()
            if not line: continue

            date_part = line.split("|")[0].strip()

            entries = line.split("|")[1:]
            
            for entry in entries:
                match = re.search(r"(.+?):\s*(.+?)\((.+?)\)", entry)
                if match:
                    category = match.group(1).strip()
                    value_str = match.group(2).strip()
                    time_str = match.group(3).strip()

                    try:
                        dt = datetime.strptime(f"{date_part} {time_str}", "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        continue

                    if category not in self.data:
                        self.data[category] = []

                    parsed_val = self.process_value(category, value_str)
                    if parsed_val is not None:
                        self.data[category].append((dt, parsed_val))

    def process_value(self, category, val_str):

        try:
            if category == "Blood Pressure":
                if "/" in val_str:
                    s, d = map(float, val_str.split("/"))
                    return s, d
                return None
            
            if category == "Body Composition & BMI":
                parts = val_str.split()
                if len(parts) >= 2:
                    return float(parts[0]), float(parts[1])
                return float(parts[0])

            if "Score" in val_str:
                score_match = re.search(r"Score:\s*(\d+)", val_str)
                if score_match:
                    return int(score_match.group(1))
            return float(val_str)
            
        except:
            return val_str

    def plot_all(self):
        if not self.data:
            print("No data to plot.")
            return

        for category, points in self.data.items():
            if not points: continue
            points.sort(key=lambda x: x[0])
            times = [p[0] for p in points]
            values = [p[1] for p in points]

            plt.figure(figsize=(10, 5))
            
            if category == "Blood Pressure":
                sys_vals = [v[0] for v in values]
                dia_vals = [v[1] for v in values]
                plt.plot(times, sys_vals, marker='o', label="Systolic (High)", color='red')
                plt.plot(times, dia_vals, marker='s', label="Diastolic (Low)", color='blue')
                plt.ylabel("mmHg")
            
            elif category == "Body Composition & BMI":
                weights = [v[0] if isinstance(v, tuple) else v for v in values]
                plt.plot(times, weights, marker='o', label="Weight (kg)", color='orange')
                plt.ylabel("Weight (kg)")

            else:
                plt.plot(times, values, marker='o', color='green', linestyle='-')
                plt.ylabel("Value")

            plt.title(f"Trend Analysis: {category}")
            plt.xlabel("Date & Time")
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.show()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(current_dir, "user_health_data.csv")
    
    plotter = HealthGraphPlotter(csv_file)
    plotter.parse_csv()
    plotter.plot_all()
