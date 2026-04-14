import os
import datetime
import tempfile
from fpdf import FPDF, XPos, YPos
from matplotlib.figure import Figure

class HealthReportPDF:
    def __init__(self, user_name, profile, plotter_data):
        self.user_name = user_name
        self.profile = profile
        self.data = plotter_data
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def calculate_sleep_duration(self, time_range):
        try:
            if "-" not in str(time_range): return 0
            start_s, end_s = str(time_range).split("-")
            def get_min(s):
                parts = s.strip().split(":")
                return int(parts[0]) * 60 + int(parts[1])
            diff = get_min(end_s) - get_min(start_s)
            if diff < 0: diff += 1440
            return round(diff / 60.0, 2)
        except: return 0

    def generate(self, output_path):
        self.pdf.add_page()
        
        self.pdf.set_font("Helvetica", "B", 24)
        self.pdf.set_text_color(46, 125, 50) 
        self.pdf.cell(0, 20, "Health Tracking Summary Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.pdf.set_fill_color(240, 240, 240)
        self.pdf.set_font("Helvetica", "B", 14)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(0, 10, " USER PROFILE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L", fill=True)
        self.pdf.set_font("Helvetica", "", 11)
        self.pdf.ln(2)
        info_line1 = f"Name: {self.user_name}  |  Gender: {self.profile.get('Gender')}  |  Age: {self.profile.get('Age')}"
        info_line2 = f"Height: {self.profile.get('Height')} cm  |  Daily Goal: {self.profile.get('HealthGoals')}"
        info_line3 = f"Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        self.pdf.cell(0, 7, info_line1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.cell(0, 7, info_line2, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.cell(0, 7, info_line3, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(10)

        if not self.data:
            self.pdf.cell(0, 10, "No tracking data found.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            for category, points in self.data.items():
                if not points or category == "Daily Photo Log": continue
                points.sort(key=lambda x: x[0])

                self.pdf.set_draw_color(200, 200, 200)
                self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
                self.pdf.ln(5)

                self.pdf.set_font("Helvetica", "B", 16)
                self.pdf.set_text_color(25, 118, 210) # 藍色標題
                self.pdf.cell(0, 10, f"Item: {category}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

                is_plottable = self._check_if_plottable(category, points)
                
                if is_plottable:
                    self._add_graph_to_pdf(category, points)
                else:
                    self.pdf.set_font("Helvetica", "I", 10)
                    self.pdf.set_text_color(120, 120, 120)
                    self.pdf.cell(0, 8, "  (Text-based records, no trend graph available)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self._add_data_list_to_pdf(category, points)

        self.pdf.set_y(-15)
        self.pdf.set_font("Helvetica", "I", 8)
        self.pdf.cell(0, 10, "End of Health Report - Healthcare Tracking System", align="C")

        self.pdf.output(output_path)

    def _check_if_plottable(self, category, points):
        if not points: return False
        numeric_categories = ["Heart Rate", "Blood Pressure", "Hydration", 
                            "Physical Activity & METs", "Body Composition & BMI", 
                            "Sleep Quality", "Mental Wellbeing"]
        
        if category not in numeric_categories:
            return False
            
        val = points[0][1]
        return isinstance(val, (int, float, tuple))
    def _add_graph_to_pdf(self, category, points):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            tmp_name = tmpfile.name
            fig = Figure(figsize=(8, 3.5))
            ax = fig.add_subplot(111)
            times = [p[0] for p in points]
            raw_vals = [p[1] for p in points]
            
            try:
                if category == "Blood Pressure":
                    sys_vals = [float(v[0]) if isinstance(v, tuple) else float(v) for v in raw_vals]
                    dia_vals = [float(v[1]) if isinstance(v, tuple) else 0 for v in raw_vals]
                    ax.plot(times, sys_vals, '-o', label="Systolic", color='#FF5252')
                    ax.plot(times, dia_vals, '-s', label="Diastolic", color='#448AFF')
                    ax.legend()
                    ax.set_ylabel("mmHg")
                elif category == "Sleep Quality":
                    durations = [self.calculate_sleep_duration(str(v)) for v in raw_vals]
                    ax.plot(times, durations, '-o', color='#7C4DFF')
                    ax.set_ylabel("Hours Slept")
                else:
                    plot_vals = []
                    for v in raw_vals:
                        if isinstance(v, tuple): plot_vals.append(float(v[0]))
                        else: plot_vals.append(float(v))
                    ax.plot(times, plot_vals, '-o', color='#2E7D32')

                fig.autofmt_xdate()
                ax.grid(True, linestyle='--', alpha=0.6)
                fig.savefig(tmp_name, dpi=100)
                self.pdf.image(tmp_name, x=15, w=180)
                self.pdf.ln(2)
            except Exception as e:
                print(f"PDF Plot Error: {e}")
        
        if os.path.exists(tmp_name): os.remove(tmp_name)

    def _add_data_list_to_pdf(self, category, points):
        self.pdf.set_font("Helvetica", "B", 10)
        self.pdf.set_text_color(50, 50, 50)
        self.pdf.cell(0, 8, f"  Detailed Records:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.pdf.set_font("Courier", "", 9)
        self.pdf.set_text_color(80, 80, 80)
        
        for dt, val in points:
            if category == "Blood Pressure" and isinstance(val, tuple):
                display_val = f"{val[0]}/{val[1]} mmHg"
            elif category == "Body Composition & BMI" and isinstance(val, tuple):
                display_val = f"Weight: {val[0]}kg, BMI: {val[1]}"
            elif category == "Sleep Quality":
                if isinstance(val, str):
                    hrs = self.calculate_sleep_duration(val)
                    display_val = f"{val} ({hrs} hrs)"
                else:
                    display_val = f"{val} hrs"
            else:
                display_val = str(val).replace("\n", " | ")

            date_str = dt.strftime('%Y-%m-%d %H:%M')
            self.pdf.multi_cell(0, 5, f"    > {date_str} : {display_val}", 
                                new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(5)