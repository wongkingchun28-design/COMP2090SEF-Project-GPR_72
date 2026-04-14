import sys, os, csv, datetime, shutil, time, cv2, subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QSizePolicy, QLabel, QFrame, QStackedWidget,QDialog, QLineEdit, QDialogButtonBox,QProgressBar,QMessageBox,QButtonGroup,QRadioButton,QInputDialog, QScrollArea, QLayout, QGraphicsDropShadowEffect, QFileDialog, QListWidget
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QFont, QPainterPath, QBrush, QLinearGradient, QPolygonF, QFontMetrics
from PySide6.QtCore import Qt, QRect, QEasingCurve, QVariantAnimation, QPointF
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from Base import Base
from question import SURVEY_OPTIONS, PHQ9_QUESTIONS, GAD7_QUESTIONS
from determine.BloodPressure import blood_pressure
from determine.HeartRate import HeartRate
from determine.PHQ9andGAD7 import PHQ9Answers, PHQ9Score, GAD7Answers, GAD7Score
from determine.StoolAndUrine import Person
from determine.waterintake import water_intake
from determine.weight import weight as WeightCalc
from PlotGraph import HealthGraphPlotter
from ReportGenerator import HealthReportPDF

GUI_DIR = os.path.dirname(os.path.abspath(__file__))  #the directory of the current file

class HeartBeatChart(QWidget):               #The heart shape chart for heart rate which will bump all the time
    def __init__(self, value, color, goal=None):    
        super().__init__()
        self.value = value
        self.color = QColor(color)
        self.setMinimumSize(100, 100)
        
        # Animation for the bump effect
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.9)  # Scale down
        self.anim.setEndValue(1.2)    # Scale up
        self.anim.setDuration(800)    # Speed of one beat
        self.anim.setEasingCurve(QEasingCurve.OutElastic)
        self.anim.setLoopCount(-1)    # Loop forever
        
        self.scale_factor = 1.0
        self.anim.valueChanged.connect(self.update_scale)   # Connect animation value to scale update
        self.anim.start()

    def update_scale(self, value):
        self.scale_factor = value
        self.update() # Triggers paintEvent

    def paintEvent(self, event):    # To draw the heart and the text
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate available size
        w, h = self.width(), self.height()
        side = min(w, h)
        
        # Move origin to center
        painter.translate(w / 2, h / 2-10)
        
        # Apply the beating scale
        painter.scale(self.scale_factor, self.scale_factor)

        # Draw a proper Heart Shape
        path = QPainterPath()
        base_s = side * 0.45   # Adjust this multiplier 
        path.moveTo(0, base_s * 1.0) 
        
        # Left side of heart
        path.cubicTo(-base_s * 1.5, base_s * 0.3,   # arc that goes left and up
                     -base_s * 1.0, -base_s * 1.2,  # arc that goes back down to the top point
                     0, -base_s * 0.3)              # top point of the heart
        # right side of heart
        path.cubicTo(base_s * 1.0, -base_s * 1.2,   # arc that goes right and up
                     base_s * 1.5, base_s * 0.3,    # arc that goes back down to the bottom point
                     0, base_s * 1.0)               # Back to bottom tip
        
        # Fill heart
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)
        painter.scale(1/self.scale_factor, 1/self.scale_factor)
        painter.setPen(QColor("white"))
        font = QFont("Arial", 16, QFont.Bold)  #font for the BPM value
        painter.setFont(font)
        
        # Position text of heart
        painter.drawText(QRect(-50, -10, 100, 30), Qt.AlignCenter, f"{int(self.value)}")
        
        # Unit label
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(QRect(-50, 15, 100, 20), Qt.AlignCenter, "BPM")

class RingChart(QWidget):       #The ring chart for weight and blood pressure
    def __init__(self, value, color, goal):
        super().__init__()
        self.value, self.color, self.goal = value, color, goal
        self.setMinimumSize(80, 80)

    def paintEvent(self, event):    # To draw the ring and the text
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)   
        side = min(rect.width(), rect.height())
        draw_rect = QRect(rect.center().x() - side//2, rect.center().y() - side//2, side, side)     #The area where the ring will be drawn

        painter.setPen(QPen(QColor("#333333"), 5))  #background ring color
        painter.drawEllipse(draw_rect)
        pen = QPen(QColor(self.color), 5)       #progress ring color
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)     
        if self.goal <= 0:
            progress = 0.01
        else:
            progress = max(0.01, min(self.value / self.goal, 1.0))
        painter.drawArc(draw_rect, 90 * 16, -int(progress * 360 * 16))  #Draw the progress arc based on the value and goal
        painter.setPen(QColor("white")) #text color
        painter.drawText(draw_rect, Qt.AlignCenter, f"{int(self.value)}")   #Draw the value text in ring

class KcalRingChart(QWidget):   #The ring chart for Met
    def __init__(self, value, color, goal):
        super().__init__()
        self.value, self.color, self.goal = value, color, goal
        self.setMinimumSize(80, 80)

    def paintEvent(self, event):    # To draw the ring and the text 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)
        side = min(rect.width(), rect.height())
        draw_rect = QRect(rect.center().x() - side//2, rect.center().y() - side//2, side, side) 


        painter.setPen(QPen(QColor("#333333"), 5))  #background ring color
        painter.drawEllipse(draw_rect)
        
        pen = QPen(QColor(self.color), 5)       #progress ring color
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        progress = min(float(self.value) / self.goal, 1.0) if self.goal > 0 else 0
        painter.drawArc(draw_rect, 90 * 16, -int(progress * 360 * 16))
        
        #Draw text and unit
        painter.setPen(QColor("white"))     
        val_str = str(int(float(self.value)))
        unit_str = " kcal"
        
        val_font = QFont("Arial", 14, QFont.Bold)
        unit_font = QFont("Arial", 9, QFont.Normal)
        fm_val = QFontMetrics(val_font)
        fm_unit = QFontMetrics(unit_font)
        
        total_w = fm_val.horizontalAdvance(val_str) + fm_unit.horizontalAdvance(unit_str)   #Calculate total width of value and unit for centering
        start_x = draw_rect.center().x() - (total_w / 2)
        text_y = draw_rect.center().y() + (fm_val.ascent() / 2) - 2
        
        painter.setFont(val_font)          
        painter.drawText(start_x, text_y, val_str)
        painter.setFont(unit_font)
        painter.drawText(start_x + fm_val.horizontalAdvance(val_str), text_y, unit_str)

class HydrationRingChart(QWidget):      #The ring chart for water intake 
    def __init__(self, value, color, goal):
        super().__init__()
        self.value, self.color, self.goal = value, color, goal
        self.setMinimumSize(80, 80)

    def paintEvent(self, event):        # To draw the ring and the text for water intake
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)
        side = min(rect.width(), rect.height())
        draw_rect = QRect(rect.center().x() - side//2, rect.center().y() - side//2, side, side)

        # background ring  
        painter.setPen(QPen(QColor("#333333"), 5))
        painter.drawEllipse(draw_rect)
        # progress ring
        pen = QPen(QColor(self.color), 5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        progress = min(self.value / self.goal, 1.0) if self.goal > 0 else 0
        painter.drawArc(draw_rect, 90 * 16, -int(progress * 360 * 16))
        # text
        painter.setPen(QColor("white"))
        painter.drawText(draw_rect, Qt.AlignCenter, f"{int(self.value)}ml")


class BarChart(QWidget):    #The bar chart for sleep duration
    def __init__(self, value, color, goal):
        super().__init__()
        self.value, self.color, self.goal = value, color, goal
        self.setMinimumSize(120, 80)

    def paintEvent(self, event):    # To draw the bar and the text for Mental health score
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        #Setup dimensions and progress
        margin = 15
        bar_height = 12
        progress = min(self.value / self.goal, 1.0) if self.goal > 0 else 0
        
        # Draw area for the bar
        bar_rect = QRect(margin, self.height() // 2, self.width() - (margin * 2), bar_height)
        
        # Create the Gradient 
        gradient = QLinearGradient(bar_rect.topLeft(), bar_rect.topRight())
        gradient.setColorAt(0.0, QColor("#4CAF50"))  
        gradient.setColorAt(0.5, QColor("#FFEB3B"))  
        gradient.setColorAt(1.0, QColor("#F44336")) 
        
        # Draw the background bar 
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bar_rect, 6, 6)
        
        # Calculate Arrow Position
        arrow_x = bar_rect.left() + (bar_rect.width() * progress)           # the horizontal point based on value
        arrow_top_y = bar_rect.top() - 2  # Tip of the arrow touches the bar 
        
        # Draw the Arrow 
        arrow_size = 8
        arrow_points = [
            QPointF(arrow_x, arrow_top_y),                        # Tip 
            QPointF(arrow_x - arrow_size, arrow_top_y - arrow_size), # Top Left
            QPointF(arrow_x + arrow_size, arrow_top_y - arrow_size)  # Top Right
        ]
        arrow_poly = QPolygonF(arrow_points)
        
        painter.setBrush(QColor("white"))
        painter.setPen(QPen(QColor("black"), 1))
        painter.drawPolygon(arrow_poly)
        
        # Draw Value Text 
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        
        # Draw the current value above the arrow
        text_rect = QRect(0, 0, self.width(), bar_rect.top() - 12)
        painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignBottom, f"{int(self.value)}")
        
        # Draw the label below the bar
        label_rect = QRect(0, bar_rect.bottom() + 5, self.width(), 20)
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QColor("#AAAAAA"))
        painter.drawText(label_rect, Qt.AlignCenter, f"Maximum: {self.goal}")

class TimeRangeBarChart(QWidget):       #The time bar chart for sleep duration
    def __init__(self, start_time, end_time, color, date):
        super().__init__()
        self.start_time = start_time  # "HH:MM"
        self.end_time = end_time
        self.color = color
        self.setMinimumSize(120, 80)
        self.date = date

    def time_to_hours(self, t):
        try:
            if isinstance(t, str) and ":" in t: #set "HH:MM" to hours in float
                parts = t.split(":")
                h = int(parts[0])
                m = int(parts[1])
                return h + m / 60.0
        except Exception:
            pass
        return 0.0

    def paintEvent(self, event):    # To draw the time range bar and the text for sleep duration
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(
            self.rect().adjusted(0, 5, 0, -self.height()//2),
            Qt.AlignHCenter,
            self.date
        )
        bar_height = 12
        y = self.height() // 2 
        left_margin = 10
        total_width = self.width() - 20

        # Draw background bar
        painter.setBrush(QColor("#333333"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(left_margin, y, total_width, bar_height, 6, 6)

        # Calculate start and end in hours
        start_h = self.time_to_hours(self.start_time)
        end_h = self.time_to_hours(self.end_time)

        total_width = self.width() - 20
        left_margin = 10

        painter.setBrush(QColor(self.color))

        if end_h >= start_h:    # same day
            start_ratio = start_h / 24
            duration_ratio = (end_h - start_h) / 24

            start_x = left_margin + int(total_width * start_ratio)
            width = int(total_width * duration_ratio)

            painter.drawRoundedRect(start_x, y, width, bar_height, 6, 6)

        else:  #when two day
            start_ratio = start_h / 24
            width1 = int(total_width * ((24 - start_h) / 24))
            start_x1 = left_margin + int(total_width * start_ratio)
            painter.drawRoundedRect(start_x1, y, width1, bar_height, 6, 6)
            width2 = int(total_width * (end_h / 24))
            start_x2 = left_margin
            painter.drawRoundedRect(start_x2, y, width2, bar_height, 6, 6)

        # draw time text
        painter.setPen(QColor("white"))
        text_rect = QRect(left_margin, y, total_width, bar_height)
        text = f"{self.start_time} - {self.end_time}"
        painter.drawText(text_rect, Qt.AlignCenter, text)

class BloodPressureChart(QWidget):      #show the blood pressure
    def __init__(self, UBP, LBP, color):
        super().__init__()
        self.UBP,self.LBP , self.color= UBP, LBP, color
        self.setMinimumSize(80, 80)

    def paintEvent(self, event):    
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # sbp text
        painter.setPen(QColor("white"))
        font_large = QFont("Arial", 30, QFont.Bold)
        painter.setFont(font_large)
        sys_rect = QRect(-30, 10, w, h // 2)
        painter.drawText(sys_rect, Qt.AlignCenter, str(self.UBP))
        
        # middle line
        painter.setPen(QColor("#555555"))
        painter.drawLine(w//2 -15, h//2 + 10, w//2 +15, h//2 -10)
        
        # dbp text
        painter.setPen(QColor(self.color)) 
        font_small = QFont("Arial", 20, QFont.Bold)
        painter.setFont(font_small)
        dia_rect = QRect(10, h // 2 - 5, w, h // 2 - 5)
        painter.drawText(dia_rect, Qt.AlignCenter, str(self.LBP))
        
        # unit text
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QColor("#AAAAAA"))
        painter.drawText(QRect(50, h// 2 + 15, w, h//2+15), Qt.AlignHCenter, "mmHg")

class BMIChart(QWidget):        #show the BMI and weight
    def __init__(self, Weight, BMI, color):
        super().__init__()
        self.Weight,self.BMI , self.color= Weight, BMI, color
        self.setMinimumSize(80, 80)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # weight text
        painter.setPen(QColor("white"))
        font_large = QFont("Arial", 30, QFont.Bold)
        painter.setFont(font_large)
        sys_rect = QRect(-20, -5, w, h // 2)
        painter.drawText(sys_rect, Qt.AlignCenter, str(self.Weight))
        #weight unit
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QColor("#AAAAAA"))
        painter.drawText(QRect(35, 20, w, h//2), Qt.AlignHCenter, "KG")

        # middle line
        painter.setPen(QColor("#555555"))
        painter.drawLine(w//4, h//2 , w//4+70, h//2 )
        
        # BMI text
        painter.setPen(QColor(self.color)) 
        font_small = QFont("Arial", 20, QFont.Bold)
        painter.setFont(font_small)
        dia_rect = QRect(-20, h // 2 +5, w, h // 2 - 5)
        painter.drawText(dia_rect, Qt.AlignCenter, str(self.BMI))
        
        # BMI unit
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QColor("#AAAAAA"))
        painter.drawText(QRect(40, h// 2 + 23, w, h//2+15), Qt.AlignHCenter, "BMI")

class TextDataChart(QWidget):       #chart that is only text
    def __init__(self, value, color):
        super().__init__()
        self.value = value
        self.color = QColor(color)
        self.setMinimumSize(80, 80)

    def paintEvent(self, event):    #text
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        
        painter.setBrush(QBrush(self.color.darker(150)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect.adjusted(5, 5, -5, -5))
        
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, str(self.value))

class ShowPhotoChart(QWidget):  #to show the photo of user
    def __init__(self, value, color):
        super().__init__()
        self.image_path = value
        self.color = QColor(color)
        self.setMinimumSize(80, 80)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        if self.image_path and os.path.exists(self.image_path):     #check if the image path is valid
            pixmap = QPixmap(self.image_path)

            # Scale the pixmap
            pixmap = pixmap.scaled(
                rect.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            painter.drawPixmap(rect, pixmap)
        else:
            painter.setPen(Qt.white)
            painter.drawText(rect, Qt.AlignCenter, "No Photo")

class ExerciseSearchDialog(QDialog):    #The list of exercise for user to choose 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Physical Activity")
        self.resize(500, 600)
        self.setStyleSheet("background-color: #222222; color: white;")
        # Initialize variables 
        self.selected_cal_per_kg = 0
        self.selected_activity = ""
        self.data = []
        self.load_data()

        layout = QVBoxLayout(self)

        # search bar
        layout.addWidget(QLabel("Search Activity:"))
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type to search (e.g., Cycling, Running)...")
        self.search_bar.setStyleSheet("background-color: #333333; color: white; padding: 10px; border: 1px solid #4CAF50;")
        self.search_bar.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_bar)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: #111111; color: white;")
        layout.addWidget(self.list_widget)

        # time input
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Duration (minutes):"))
        self.duration_input = QLineEdit("30")
        self.duration_input.setFixedWidth(60)
        h_layout.addWidget(self.duration_input)
        layout.addLayout(h_layout)

        # confirm button
        self.btn = QPushButton("Confirm")
        self.btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        self.btn.clicked.connect(self.validate_and_accept)
        layout.addWidget(self.btn)

        self.filter_list("") # initially show all exercises

    def load_data(self):            #load the exercise data from CSV file
        csv_path = os.path.join(GUI_DIR, "exercise_dataset.csv")
        try:
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.data.append({
                        "name": row["Activity, Exercise or Sport (1 hour)"],
                        "cal_per_kg": float(row["Calories per kg"])
                    })
        except Exception as e:
            print(f"Error loading CSV: {e}")

    def filter_list(self, text):    #filter for search bar
        self.list_widget.clear()
        for item in self.data:
            if text.lower() in item["name"].lower():
                self.list_widget.addItem(item["name"])

    def validate_and_accept(self):      
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select an activity!")
            return
        
        self.selected_activity = current_item.text()
        # get the calories per kg for the selected activity
        self.selected_cal_per_kg = next(item["cal_per_kg"] for item in self.data if item["name"] == self.selected_activity)
        self.accept()

class CircularButton(QFrame):       #set the btn
    def __init__(self, name, value=20, color="#ffffff", graph_type="circle", goal=100):
        super().__init__()
        self.name = name
        self.value = value
        self.color = color
        self.graph_type = graph_type
        self.goal = goal
        
        self.setMinimumHeight(120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: black;
                border: 2px solid {self.color};
                border-radius: 15px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)
        self.shadow.setColor(QColor(self.color))
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)

        self.anim = QVariantAnimation(self)
        self.anim.setDuration(200)
        self.anim.setStartValue(0)
        self.anim.setEndValue(15) 
        self.anim.valueChanged.connect(lambda v: self.shadow.setBlurRadius(v))
    
        #main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 10, 15, 10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # left layout for name label and input button
        self.left_layout = QVBoxLayout()
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet(f"color: {self.color}; font-weight: bold; font-size: 13px;")
        self.name_label.setWordWrap(True)
        self.left_layout.addWidget(self.name_label, alignment=Qt.AlignTop)
        self.left_layout.addStretch()
        # input button
        self.input_btn = QPushButton("INPUT")
        self.input_btn.setFixedSize(65, 30)
        self.input_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: white; color: {self.color}; }}
        """)
        self.left_layout.addWidget(self.input_btn, alignment=Qt.AlignBottom | Qt.AlignLeft)
        try:
            num_value = float(self.value)
            if num_value <= 0:
                num_value = 0.01   
        except:
            num_value = 0.01

        # based on graph type to choose the chart to show
        if graph_type == "circle":
            self.chart = RingChart(num_value, color, goal)
            
        elif graph_type == "bar":
            self.chart = BarChart(num_value, color, goal)
            
        elif graph_type == "heart":
            self.chart = HeartBeatChart(num_value, color)
            
        elif graph_type == "hydration":
            self.chart = HydrationRingChart(num_value, color, goal)
            
        elif graph_type == "time":
            start, end = "00:00", "00:00"   #expected input format: "HH:MM - HH:MM"
            val_str = str(self.value)
            if "-" in val_str:
                parts = val_str.split("-")
                if len(parts) == 2:
                    start, end = parts[0].strip(), parts[1].strip()
                    
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            self.chart = TimeRangeBarChart(start, end, color, today)
            
        elif graph_type == "blood":
            sbp, dbp = "0", "0"         #expected input format: "SBP/DBP" 
            val_str = str(self.value)
            if "/" in val_str:
                parts = val_str.split("/")
                if len(parts) == 2:
                    sbp, dbp = parts[0].strip(), parts[1].strip()
            self.chart = BloodPressureChart(sbp, dbp, color)
            
        elif graph_type == "BMI":
            weight, bmi = "0", "0"      #expected input format : "weight"
            if self.value and " " in str(self.value):
                parts = str(self.value).split()
                weight = parts[0]
                bmi = parts[1]
            elif self.value:
                weight = str(self.value)
                self.chart = BMIChart(weight, bmi, color)
            
            self.chart = BMIChart(weight, bmi, color)
        elif graph_type == "text_list":
            self.chart = TextDataChart(self.value, color)
        elif graph_type == "photo":
            self.chart = ShowPhotoChart(self.value, color)
        elif graph_type == "kcal_ring":
            self.chart = KcalRingChart(num_value, color, goal)
        else:
            self.chart = QWidget()
        
        # right layout for the chart
        self.main_layout.addLayout(self.left_layout, 2)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.chart, 3)

    def enterEvent(self, event):    #hover effect
        self.anim.setDirection(QVariantAnimation.Forward)
        self.anim.start()
        self.setStyleSheet(self.styleSheet().replace(f"border: 2px solid {self.color}", "border: 2px solid white")) #hover turn white border

    def leaveEvent(self, event):       #leave hover effect
        self.anim.setDirection(QVariantAnimation.Backward)
        self.anim.start()
        self.setStyleSheet(self.styleSheet().replace("border: 2px solid white", f"border: 2px solid {self.color}")) #restore original border color



class SurveyDialog(QDialog):        #The survey dialog for PHQ-9 and GAD-7 questions
    def __init__(self, title, questions, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 400)
        self.setStyleSheet("background-color: #222222; color: white;")
        
        self.questions = questions
        self.button_groups = []
        self.current_index = 0

        # main layout
        self.main_layout = QVBoxLayout(self)
        
        # progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(questions))
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid grey; border-radius: 5px; text-align: center; height: 10px; }
            QProgressBar::chunk { background-color: #FFD740; }
        """)
        self.main_layout.addWidget(self.progress_bar)

        # stacked widget for questions
        self.stacked_widget = QStackedWidget()
        for i, q_text in enumerate(questions):
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(30, 30, 30, 30)
            
            # question label
            q_label = QLabel(q_text)
            q_label.setWordWrap(True) 
            q_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD740; margin-bottom: 20px;")
            page_layout.addWidget(q_label)
            
            # choice buttons
            group = QButtonGroup(page)
            self.button_groups.append(group)
            
            for opt_text, score in SURVEY_OPTIONS:
                rb = QRadioButton(opt_text)
                rb.setStyleSheet("font-size: 14px; padding: 10px; color: #EEEEEE;")
                group.addButton(rb, score)
                page_layout.addWidget(rb)
                rb.clicked.connect(self.next_page)  #go to next page after selected the option
            
            page_layout.addStretch()    
            self.stacked_widget.addWidget(page)
            
        self.main_layout.addWidget(self.stacked_widget)

        # back and next button
        self.nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("Back") #back button
        self.back_btn.setFixedSize(100, 40)
        self.back_btn.setEnabled(False) #no back for first page
        self.back_btn.clicked.connect(self.prev_page)   #go back when click back button
        
        self.next_btn = QPushButton("Next")     #next button
        self.next_btn.setFixedSize(100, 40)
        self.next_btn.clicked.connect(self.next_page)   #go to next page when click next button

        self.nav_layout.addWidget(self.back_btn)
        self.nav_layout.addStretch()
        self.nav_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(self.nav_layout)

    def next_page(self):
        # to check if the user has selected an option before going to next page
        if self.button_groups[self.current_index].checkedId() == -1:
            return # if no option selected, do nothing

        if self.current_index < len(self.questions) - 1:    #go to next page
            self.current_index += 1
            self.stacked_widget.setCurrentIndex(self.current_index)
            self.update_ui()
        else:
            # last page, submit the answer 
            self.accept()

    def prev_page(self):    #go to previous page
        if self.current_index > 0:
            self.current_index -= 1
            self.stacked_widget.setCurrentIndex(self.current_index)
            self.update_ui()

    def update_ui(self):
        # update progress bar
        self.progress_bar.setValue(self.current_index)
        
        # update back button 
        self.back_btn.setEnabled(self.current_index > 0)
        
        # update next button
        if self.current_index == len(self.questions) - 1:
            self.next_btn.setText("Submit")
            self.next_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        else:
            self.next_btn.setText("Next")
            self.next_btn.setStyleSheet("")

    def get_total_score(self):      #calculate the total score 
        return sum(group.checkedId() for group in self.button_groups)
    
class InputDataDialog(QDialog):     #input dialog 
    def __init__(self, title, question, placeholder="", parent=None): 
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet("background-color: #222222; color: white;")
        layout = QVBoxLayout(self)
        
        self.label = QLabel(question)
        self.label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(self.label)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder) 
        self.input_field.setStyleSheet("background-color: #333333; border: 1px solid #555555; color: white; padding: 8px; font-size: 14px;")
        layout.addWidget(self.input_field)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_value(self):        #get the value from user input
        return self.input_field.text()



class HomePage(QWidget):    #Home page
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.grid_container = QGridLayout()
        self.grid_container.setSpacing(20)
        self.big_btn_layout = QVBoxLayout()
        self.layout.addLayout(self.big_btn_layout)
        self.layout.addSpacing(20)
        self.layout.addLayout(self.grid_container)
        self.layout.addStretch(1)

    def refresh_ui(self):         # refresh ui when needed
        self.clear_layout(self.big_btn_layout)
        self.clear_layout(self.grid_container)

        latest_data = self.window().get_latest_health_data()    #To get the latest data form the csv file
        
        # mental health score 
        mental_raw = latest_data.get("Mental Wellbeing", "0")
        mental_score = 0
        mental_max = 27
        if "Score:" in mental_raw:
            try:
                score_part = mental_raw.split("Score:")[1].split("(")[0].strip()    #get the score number 
                mental_score = int(score_part)
                # based on the test type to set the max score for the bar chart
                if "GAD-7" in mental_raw:
                    mental_max = 21
                else:
                    mental_max = 27
            except Exception as e:
                print(f"Error parsing mental health score: {e}")
                mental_score = 0
        digestive_raw = latest_data.get("Digestive Health", "No Record")
        digestive_display = digestive_raw # default display

        if "," in digestive_raw and "Urine:" in digestive_raw:  
            try:
                parts = digestive_raw.split(",")
                urine_val = parts[0].replace("Urine:", "").strip()
                stool_val = parts[1].replace("Stool Type:", "Stool:").strip()
                digestive_display = f"Urine: {urine_val}\nStool: {stool_val}"   #turn it to two lines 
            except:
                pass

        mets_raw = latest_data.get("Physical Activity & METs", "0") #met raw data
        try:
            mets_val = float(mets_raw.split()[0]) if " " in str(mets_raw) else float(mets_raw)  #get the met value as it contain time at the back
        except:
            mets_val = 0.0
        #get user data
        user_data = self.window().user_data
        user_name = user_data.Name
        daily_goal = float(user_data.HealthGoals)
        # big button for physical activity and METs
        big_btn = CircularButton("Physical Activity & METs", mets_val, "#4CAF50", "kcal_ring", daily_goal)
        big_btn.setMinimumHeight(180)
        self.big_btn_layout.addWidget(big_btn)
        big_btn.input_btn.clicked.connect(lambda: self.open_input_dialog({"name": "Physical Activity & METs"}))
        # calculate the water intake goal based on weight and exercise duration
        try:
            u_weight = float(latest_data.get("Body Composition & BMI", "70").split()[0])
        except:
            u_weight = 70.0
        try:
            u_exercise = float(mets_raw.split()[1]) if " " in str(mets_raw) else 0.0
        except:
            u_exercise = 0.0
        water_goal = u_weight * 30 + (u_exercise / 30) * 350
        #configs of the buttons
        dynamic_configs = [
            {"name": "Heart Rate", "value": int(latest_data.get("Heart Rate", 0)), "color": "#FF5252", "graph_type": "heart"},
            {"name": "Blood Pressure", "value": latest_data.get("Blood Pressure", "0/0"), "color": "#448AFF","graph_type" : "blood"},
            {"name": "Sleep Quality", "value": latest_data.get("Sleep Quality", "0"), "color": "#7C4DFF", "graph_type": "time"},
            {"name": "Body Composition & BMI", "value": latest_data.get("Body Composition & BMI", "0"), "color": "#FFAB40", "graph_type": "BMI"},
            {"name": "Hydration", "value": float(latest_data.get("Hydration", 0)), "color": "#4CAF50", "graph_type": "hydration", "goal": water_goal},
            {"name": "Dietary Intake", "value": latest_data.get("Dietary Intake", "No Record"), "color": "#00BCD4", "graph_type": "text_list"},
            {"name": "Medication & Supplements", "value":latest_data.get("Medication & Supplements", "None"), "color": "#2196F3", "graph_type": "text_list"},
            {"name": "Mental Wellbeing", "value": mental_score, "color": "#FFD740", "graph_type": "bar","goal": mental_max},
            {"name": "Digestive Health", "value": digestive_display, "color": "#FF4081", "graph_type": "text_list"},
            {"name": "Daily Photo Log", "value": latest_data.get("Daily Photo Log", ""), "color": "#00E676", "graph_type": "photo"},
        ]

        # 2x5 button layout
        for i, data in enumerate(dynamic_configs):
            btn = CircularButton(data["name"], data["value"], data["color"], data["graph_type"],data.get("goal", 100))
            btn.setMinimumHeight(110)
            self.grid_container.addWidget(btn, i // 2, i % 2)
            btn.input_btn.clicked.connect(lambda checked=False, d=data: self.open_input_dialog(d))

    def clear_layout(self, layout): #clear the layout
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0) 
                widget = item.widget()
                if widget:
                    widget.setParent(None) 
                    widget.deleteLater()

    def open_input_dialog(self, data):      #open the input dialog based on the category of the button
            user_data = self.window().user_data
            cat_name = data["name"]
            
            # get the user data
            latest_data = self.window().get_latest_health_data()
            mets_record = latest_data.get("Physical Activity & METs", "0 0")
            age = int(user_data.Age)
            gender = user_data.Gender.lower()
            height = float(user_data.Height)
            placeholder_map = {
                "Heart Rate": "e.g. 72 (BPM)",
                "Blood Pressure": "e.g. 120/80 (mmHg)",
                "Hydration": "e.g. 500 (ml)",
                "Body Composition & BMI": "e.g. 65.5 (kg)",
                "Sleep Quality": "e.g. 23:00-07:00",
                "Dietary Intake": "e.g. Chicken Salad, 450 kcal",
                "Medication & Supplements": "e.g. Vitamin C, 1 pill"
            }
            # get the exercise time and weight for water intake calculation
            try:
                exercise_mins = float(mets_record.split()[1]) if " " in mets_record else 0.0
            except:
                exercise_mins = 0.0
            try:
                u_weight = float(latest_data.get("Body Composition & BMI", "70").split()[0])
            except:
                u_weight = 70.0

            
            if cat_name == "Daily Photo Log":       #let the user to select a photo
                file_path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg)")
                if file_path:
                    saved_path = self.window().save_photo(file_path)
                    self.window().save_to_csv(cat_name, saved_path)
                    self.refresh_ui()
                return 

            elif cat_name == "Mental Wellbeing":    #show the question to user
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Mental Wellbeing")
                msg_box.setText("Which assessment would you like to take?")
                phq_btn = msg_box.addButton("PHQ-9 (Depression)", QMessageBox.ActionRole)
                gad_btn = msg_box.addButton("GAD-7 (Anxiety)", QMessageBox.ActionRole)
                msg_box.addButton("Cancel", QMessageBox.RejectRole)
                msg_box.exec()
                
                if msg_box.clickedButton() == phq_btn:      #chose the question type
                    self.run_mental_health_survey("PHQ-9 Assessment", PHQ9_QUESTIONS, "PHQ-9")
                elif msg_box.clickedButton() == gad_btn:
                    self.run_mental_health_survey("GAD-7 Assessment", GAD7_QUESTIONS, "GAD-7")
                return

            elif cat_name == "Digestive Health":        #let the user chose the digestive health status with lsitbox
                urine_options = ["Clear to pale yellow", "Red or pink", "Orange", "Blue or green", "Dark brown", "Cloudy"]
                color, ok1 = QInputDialog.getItem(self, "Digestive Health", "Select Urine Color:", urine_options, 0, False)
                if ok1 and color:
                    stool_options = ["1: Severe Constipation", "2: Mild Constipation", "3: Normal", "4: Normal (Soft)", "5: Lacking Fiber", "6: Mild Diarrhea", "7: Severe Diarrhea"]
                    stool_str, ok2 = QInputDialog.getItem(self, "Digestive Health", "Select Stool Type:", stool_options, 2, False)
                    if ok2:
                        stool_type = int(stool_str.split(":")[0])
                        health_person = Person(color, stool_type)
                        summary = health_person.health_summary()
                        self.window().save_to_csv(cat_name, f"Urine: {color}, Stool Type: {stool_type}")
                        QMessageBox.information(self, "Digestive Summary", summary)
                        self.refresh_ui()
                return

            elif cat_name == "Physical Activity & METs":    #let the user enter the exercise type and time 
                dialog = ExerciseSearchDialog(self)
                if dialog.exec() == QDialog.Accepted:
                    try:
                        u_weight = 70.0
                        latest = self.window().get_latest_health_data()
                        if "Body Composition & BMI" in latest:
                            u_weight = float(latest["Body Composition & BMI"].split()[0])
                        minutes = float(dialog.duration_input.text())
                        total_burned = round(u_weight * dialog.selected_cal_per_kg * (minutes / 60), 2)     #calculate the burned calories
                        combined_save_val = f"{total_burned} {minutes}"
                        self.window().save_to_csv(cat_name, combined_save_val)
                        QMessageBox.information(self, "Recorded", f"Burned: {total_burned} kcal")
                        self.refresh_ui()
                    except Exception as e:
                        QMessageBox.warning(self, "Error", str(e))
                return

            # for heart rate, blood pressure, hydration, body composition & BMI
            analyzers = {
                "Heart Rate": HeartRate(age, gender),
                "Blood Pressure": blood_pressure(),
                "Hydration": water_intake(u_weight, exercise_mins), 
                "Body Composition & BMI": WeightCalc(gender, height) 
            }

            analyzer = analyzers.get(cat_name)

            if analyzer:
                # the question
                prompt_map = {
                    "Heart Rate": "Enter your current BPM:",
                    "Blood Pressure": "Enter your Blood Pressure:",
                    "Hydration": "How many ml of water did you drink?",
                    "Body Composition & BMI": "Enter your current weight in kg:",
                    "Sleep Quality": "When did you sleep and wake up?"
                }
                
                # the text in the input field
                q_text = prompt_map.get(cat_name, f"Enter {cat_name}:")
                p_text = placeholder_map.get(cat_name, "")
                dialog = InputDataDialog(cat_name, q_text, p_text, self)
                
                if dialog.exec() == QDialog.Accepted:
                    val = dialog.get_value()
                    if val:
                        
                        self.window().save_to_csv(cat_name, val)
                        
                        if cat_name == "Body Composition & BMI":
                            analyzer.body_mass = float(val)
                            bmi_val = analyzer.BMI_value()
                            status = analyzer.BMI_category()
                            self.window().save_to_csv(cat_name, f"{val} {bmi_val}")
                            QMessageBox.information(self, "BMI Result", f"BMI: {bmi_val}\nStatus: {status}")
                        else: 
                            report = analyzer.analyze(val)
                            QMessageBox.information(self, f"{cat_name} Analysis", report)
                        
                        self.refresh_ui()
                return

            # text input only with do analyze
            
            hint = placeholder_map.get(cat_name, "")
            dialog = InputDataDialog(cat_name, f"Enter details for {cat_name}:", hint, self)
            
            if dialog.exec() == QDialog.Accepted:
                val = dialog.get_value()
                if val:
                    self.window().save_to_csv(cat_name, val)
                    self.refresh_ui()
        

    def run_mental_health_survey(self, title, questions, type_label):   #the mental health survey 
        dialog = SurveyDialog(title, questions, self)
        
        if dialog.exec() == QDialog.Accepted:
            scores = [group.checkedId() for group in dialog.button_groups]  #get the scores
            
            # PHQ-9
            if type_label == "PHQ-9":
                answers = PHQ9Answers(*scores) 
                scorer = PHQ9Score()
            else: # GAD-7
                answers = GAD7Answers(*scores) 
                scorer = GAD7Score()

            result = scorer.interpret(answers)      #get the result with score, severity and recommendation
            
            display_text = (
                f"Total Score: {result['score']}\n"
                f"Severity: {result['severity']}\n\n"
                f"Recommendation:\n{result['comment']}"
            )
            
            if type_label == "PHQ-9" and result.get("suicide_risk"):
                display_text += "NOTE: Suicide risk detected. Please seek help immediately."

            save_value = f"{type_label} Score: {result['score']} ({result['severity']})"
            self.window().save_to_csv("Mental Wellbeing", save_value)
            
            QMessageBox.information(self, f"{type_label} Result", display_text)

class TrendPage(QWidget):       #graph page
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plotter = None
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: black;
                border: none;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #111111;    
                width: 12px;           
                margin: 0px 0px 0px 0px;
            }
            

            QScrollBar::handle:vertical {
                background: #444444;    
                min-height: 30px;
                border-radius: 6px;     
            }
            

            QScrollBar::handle:vertical:hover {
                background: #FFD740;    
            }
            

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.scroll_area.setFocusPolicy(Qt.StrongFocus) # make sure to get form scroll wheel events


        self.container = QWidget()
        self.container.setStyleSheet("background-color: black;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(30, 20, 30, 20)
        self.container_layout.setSpacing(50)
        self.container_layout.setSizeConstraint(QLayout.SetMinimumSize)

        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area)

    def refresh_ui(self):       #refresh UI
        while self.container_layout.count():        #del widget in the layout
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.add_permanent_photo_section()
        # get data form csv file
        csv_path = os.path.join(GUI_DIR, "user_health_data.csv")
        self.plotter = HealthGraphPlotter(csv_path)
        self.plotter.parse_csv()

        if not self.plotter.data:       #if no data, show the message
            msg = QLabel("No health data recorded yet.")
            msg.setStyleSheet("color: white; font-size: 20px;")
            msg.setAlignment(Qt.AlignCenter)
            self.container_layout.addWidget(msg)
            return

        # color for each category
        color_map = {
            "Heart Rate": "#FF5252",
            "Blood Pressure": "#448AFF",
            "Hydration": "#4CAF50",
            "Physical Activity & METs": "#4CAF50",
            "Body Composition & BMI": "#FFAB40",
            "Sleep Quality": "#7C4DFF",
            "Mental Wellbeing": "#FFD740"
        }

        # process each category of data and create graphs
        for category, points in self.plotter.data.items():
            if not points: continue
            points.sort(key=lambda x: x[0]) # sort by date

            #sleep quality
            if category == "Sleep Quality":
                processed = []
                for dt, val in points:
                    hrs = self.calculate_sleep_duration(str(val))
                    if hrs > 0: processed.append((dt, hrs))
                
                if processed:
                    self.add_graph_title(category, color_map["Sleep Quality"])
                    self.add_matplotlib_graph(category, processed, color_map["Sleep Quality"], "Hours Slept")
                continue

            first_val = points[0][1]        #check the type of the value to decide how to display
            if isinstance(first_val, (int, float, tuple)):  #numerical data with line graph
                color = color_map.get(category, "#FFFFFF")
                self.add_graph_title(category, color)
                self.add_matplotlib_graph(category, points, color, "Value")
        self.container_layout.addSpacing(30)        
        export_btn = QPushButton("Export Full Health Report (PDF)")     #button to export the report as PDF
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD740; color: black; border-radius: 10px;
                padding: 20px; font-size: 18px; font-weight: bold;
            }
            QPushButton:hover { background-color: white; }
        """)
        export_btn.clicked.connect(self.export_to_pdf)
        self.container_layout.addWidget(export_btn)
        self.container_layout.addStretch(1)
    def export_to_pdf(self):        #export the report as PDF when click the button
        if self.plotter is None:
            csv_path = os.path.join(GUI_DIR, "user_health_data.csv")
            self.plotter = HealthGraphPlotter(csv_path)
            self.plotter.parse_csv()

        user_data = self.window().user_data
        user_name = user_data.Name
        profile = {
            "Age": user_data.Age,
            "Gender": user_data.Gender,
            "Height": user_data.Height,
            "HealthGoals": user_data.HealthGoals
        }

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"Health_Report_{user_name}.pdf", "PDF Files (*.pdf)")
        if not save_path: return

        try:
            generator = HealthReportPDF(user_name, profile, self.plotter.data)
            generator.generate(save_path)
            
            QMessageBox.information(self, "Success", f"Full Report Exported Successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save PDF: {e}")

    def add_permanent_photo_section(self):
        self.add_graph_title("Daily Photo Log", "#00E676")
        
        video_btn = QPushButton("Generate & Play Photo Recap Video")
        video_btn.setStyleSheet("""
            QPushButton {
                background-color: #111111; 
                color: #00E676; 
                border: 2px solid #00E676;
                padding: 25px; 
                font-size: 18px; 
                border-radius: 10px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #00E676; 
                color: black; 
            }
        """)
        video_btn.clicked.connect(self.handle_video_play)
        self.container_layout.addWidget(video_btn)
    def add_graph_title(self, text, color):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: bold; margin-top: 10px;")
        self.container_layout.addWidget(lbl)

    def add_matplotlib_graph(self, category, points, color, ylabel):
        canvas = self.create_matplotlib_canvas(category, points, color, ylabel)
        canvas.setMinimumHeight(400) 
        self.container_layout.addWidget(canvas)

    def calculate_sleep_duration(self, time_range):
        try:
            if "-" not in time_range: return 0
            start_s, end_s = time_range.split("-")
            def get_min(s):
                h, m = map(int, s.strip().split(":"))
                return h * 60 + m
            diff = get_min(end_s) - get_min(start_s)
            if diff < 0: diff += 1440
            return round(diff / 60.0, 2)
        except: return 0

    def handle_video_play(self):
        final_path = self.window().create_video_from_photos()
        
        if final_path and os.path.exists(final_path):
            try:
                if sys.platform == "win32":
                    os.startfile(final_path)
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, final_path])
            except Exception as e:
                QMessageBox.warning(self, "Playback Error", f"Could not open video player: {e}")
        else:
            QMessageBox.warning(self, "Error", "No photos available to create a video.")

    def create_matplotlib_canvas(self, category, points, color, ylabel):
        times = [p[0] for p in points]
        raw_values = [p[1] for p in points]

        fig = Figure(figsize=(10, 5), facecolor='black', tight_layout=True)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.set_facecolor('#111111')

        try:
            if category == "Blood Pressure":
                sys_vals = [float(v[0]) if isinstance(v, tuple) else float(v) for v in raw_values]
                dia_vals = [float(v[1]) if isinstance(v, tuple) else 0 for v in raw_values]
                ax.plot(times, sys_vals, marker='o', label="Systolic", color='#FF5252', linewidth=3)
                ax.plot(times, dia_vals, marker='s', label="Diastolic", color='#448AFF', linewidth=3)
                ax.legend(facecolor='#333333', labelcolor='white')
                ax.set_ylabel("mmHg", color='white')
            
            elif category == "Body Composition & BMI":
                weight_vals = []
                for v in raw_values:
                    if isinstance(v, tuple): weight_vals.append(float(v[0]))
                    else: weight_vals.append(float(v))
                ax.plot(times, weight_vals, marker='o', color='#FFAB40', linewidth=3, markersize=8)
                ax.set_ylabel("Weight (kg)", color='white')

            else:
                plot_vals = []
                for v in raw_values:
                    if isinstance(v, tuple):
                        plot_vals.append(float(v[0])) 
                    else:
                        try:
                            plot_vals.append(float(v))
                        except:
                            continue 
                
                if plot_vals and len(plot_vals) == len(times):
                    ax.plot(times, plot_vals, marker='o', color=color, linewidth=3, markersize=8)
                ax.set_ylabel(ylabel, color='white')

        except Exception as e:
            print(f"Error on drawing ({category}): {e}")

        ax.tick_params(axis='both', colors='white', labelsize=9)
        ax.grid(True, color='#333333', linestyle='--', alpha=0.5)
        for spine in ax.spines.values():
            spine.set_color('#555555')
        fig.autofmt_xdate() 
        
        return canvas

class EditUserDialog(QDialog):
    def __init__(self, name, current_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Profile: {name}")
        layout = QVBoxLayout(self)
        
        self.inputs = {}
        labels = ["Age", "Gender", "Height", "Status", "Goals"]
        
        for i, label in enumerate(labels):
            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel(label))
            edit = QLineEdit(str(current_data[i]))
            h_layout.addWidget(edit)
            self.inputs[label] = edit
            layout.addLayout(h_layout)
            
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_updated_data(self):
        return [
            self.inputs["Age"].text(),
            self.inputs["Gender"].text(),
            self.inputs["Height"].text(),
            self.inputs["Status"].text(),
            self.inputs["Goals"].text()
        ]

class UserPage(QWidget):
    def __init__(self, user_data, parent=None): 
        super().__init__(parent)
        self.user_data = user_data 
        self.main_layout = QVBoxLayout(self)
        self.refresh_ui()

    def refresh_ui(self):
        self.clear_layout(self.main_layout)

        top_bar = QHBoxLayout()
        user_selector = QLabel(f"Logged in as: <b>{self.user_data.Name}</b>")
        user_selector.setStyleSheet("font-size: 18px; color: #FFD740;")
        top_bar.addWidget(user_selector)
        self.main_layout.addLayout(top_bar)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #444444;")
        self.main_layout.addWidget(line)

        display_fields = [
            ("Age", self.user_data.Age),
            ("Gender", self.user_data.Gender),
            ("Height (cm)", self.user_data.Height),
            ("Health Goals (kcal)", self.user_data.HealthGoals)
        ]

        for label_text, value in display_fields:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            data_label = QLabel(f"{label_text} : {value}")
            data_label.setStyleSheet("font-size: 16px; color: white; padding: 10px;")
            
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedWidth(60)
            edit_btn.setStyleSheet("background-color: #333333; color: #FFD740; border-radius: 5px;")
            
            key = label_text.split(" ")[0] 
            edit_btn.clicked.connect(lambda ch, k=key, v=value: self.edit_single_field(k, v))
            
            row_layout.addWidget(data_label)
            row_layout.addStretch()
            row_layout.addWidget(edit_btn)
            self.main_layout.addWidget(row_widget)

        self.main_layout.addStretch()

    def edit_single_field(self, key, current_value):
        text, ok = QInputDialog.getText(self, f"Edit {key}", f"Enter new value for {key}:", QLineEdit.Normal, str(current_value))
        if ok and text:
            if key == "Age": self.user_data.Age = text
            elif key == "Gender": self.user_data.Gender = text
            elif key == "Height": self.user_data.Height = text
            elif key == "Health": self.user_data.HealthGoals = text 
            self.user_data.save()
            self.refresh_ui()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()


class MainWindow(QMainWindow):  #main window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Healthcare Tracking System")
        self.resize(720, 1080)
        self.user_data = Base.load()
        self.init_csv()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: black;")
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)


        self.setup_top_bar()


        self.stacked_widget = QStackedWidget()
        self.home_page = HomePage()
        self.trend_page = TrendPage()
        self.user_page = UserPage(self.user_data) 
        
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.trend_page)
        self.stacked_widget.addWidget(self.user_page)
        

        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 0, 20, 0)
        content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(content_container)


        self.setup_bottom_bar()

    def setup_top_bar(self):
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        

        top_layout.setContentsMargins(40, 30, 40, 10)
        

        title_label = QLabel("Healthcare Tracking System")
        title_label.setStyleSheet("font-size: 35px; font-weight: bold; color: white;")
        

        
        

        top_layout.addWidget(title_label)
        top_layout.addStretch()

        

        self.main_layout.addWidget(top_widget)

    def switch_page(self, index):

        self.stacked_widget.setCurrentIndex(index)
        self.update_nav_styles(index)
        if index == 1:
            self.trend_page.refresh_ui()

    def update_nav_styles(self, active_index):

        for i, btn in enumerate(self.nav_buttons):
            if i == active_index:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #333333; 
                        color: #FFFFFF; 
                        border-radius: 10px;
                        font-size: 18px;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #888888;
                        border: none;
                        font-size: 18px;
                        font-weight: bold;
                    }
                    QPushButton:hover { color: white; }
                """)
    def setup_bottom_bar(self):
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background-color: #111111; border-top: 1px solid #333333;")
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(20, 10, 20, 20)
        
        self.nav_buttons = []
        nav_data = [
            ("Home", 0),
            ("Trend", 1),
            ("User", 2)
        ]
        
        for name, index in nav_data:
            btn = QPushButton(name)
            btn.setMinimumHeight(60)
            btn.setCheckable(True) 
            self.nav_buttons.append(btn)
            btn.clicked.connect(lambda checked=False, idx=index: self.switch_page(idx))
            bottom_layout.addWidget(btn)
            
        self.main_layout.addWidget(bottom_widget)
        self.update_nav_styles(0)
        self.home_page.refresh_ui()

    def init_csv(self):
        self.csv_file = os.path.join(GUI_DIR, "user_health_data.csv")
        
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', encoding='utf-8') as f:
                user_title = f"Name: {self.user_data.Name}, Gender: {self.user_data.Gender}, Height: {self.user_data.Height}cm, Age: {self.user_data.Age}\n"
                f.write(user_title)
                f.write("-" * 50 + "\n")

    def save_to_csv(self, category, value):
        import datetime
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        timestamp = now.strftime("%H:%M:%S")
        
        lines = []
        if os.path.exists(self.csv_file):
            with open(self.csv_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        found_today_idx = -1
        for i in range(len(lines)-1, -1, -1):
            if lines[i].startswith(current_date):
                found_today_idx = i
                break
        
        final_value = value
        
        if category in ["Hydration", "Physical Activity & METs"] and found_today_idx != -1:
            today_line = lines[found_today_idx].strip()
            parts = today_line.split("|")
            date_prefix = parts[0].strip() 
            
            new_parts = []
            found_old_val_1 = 0.0
            found_old_val_2 = 0.0
            
            for p in parts[1:]:
                p = p.strip()
                if not p: continue
                
                if p.startswith(f"{category}:"):
                    try:
                        raw_content = p.split(":")[1].split("(")[0].strip()
                        if " " in raw_content:
                            v1, v2 = raw_content.split()
                            found_old_val_1, found_old_val_2 = float(v1), float(v2)
                        else:
                            found_old_val_1 = float(raw_content)
                    except:
                        pass 
                else:
                    new_parts.append(p)

            try:
                if " " in str(value):
                    n1, n2 = str(value).split()
                    final_value = f"{round(found_old_val_1 + float(n1), 2)} {round(found_old_val_2 + float(n2), 2)}"
                else:
                    final_value = str(round(found_old_val_1 + float(value), 2))
            except:
                final_value = value 


            new_line = date_prefix
            for part in new_parts:
                new_line += f" | {part}"
            
            lines[found_today_idx] = new_line 
        

        new_entry = f" | {category}: {final_value}({timestamp})"
        
        if found_today_idx != -1:
            current_content = lines[found_today_idx].strip()
            lines[found_today_idx] = current_content + new_entry + "\n"
        else:
            if lines and not lines[-1].endswith("\n"): lines[-1] += "\n"
            lines.append(f"{current_date}{new_entry}\n")

        with open(self.csv_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
            


    def get_latest_health_data(self, target_date=None):
        if target_date is None:
            target_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
        latest_values = {}
        if not os.path.exists(self.csv_file):
            return latest_values

        try:
            with open(self.csv_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line in reversed(lines):
                line = line.strip()
                if line.startswith(target_date):
                    parts = line.split("|")
                    for p in reversed(parts):
                        if ":" in p and "(" in p:
                            kv_part = p.split("(")[0]
                            if ":" in kv_part:
                                k, v = kv_part.split(":", 1)
                                key = k.strip()
                                val = v.strip()
                                if key not in latest_values:
                                    latest_values[key] = val
                    break 
                                
        except Exception as e:
            print(f"Error on reading CSV: {e}")
            
        return latest_values
    
    def save_photo(self, file_path):
        # Create folder if not exist
        photo_dir = os.path.join(GUI_DIR, "photos")
        os.makedirs(photo_dir, exist_ok=True)

        # Create unique filename using timestamp
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(file_path)[1]
        new_name = f"photo_{now}{ext}"

        new_path = os.path.join(photo_dir, new_name)

        # Copy photo into folder
        shutil.copy(file_path, new_path)

        print(f"Photo saved: {new_path}")
        return new_path
    
    def create_video_from_photos(self):

        photo_dir = os.path.join(GUI_DIR, "photos")
        output_path = os.path.join(photo_dir, "output.mp4")

        # sort the photo
        images = sorted([
            img for img in os.listdir(photo_dir)
            if img.endswith((".png", ".jpg", ".jpeg"))
        ])

        if not images:
            print("No images found")
            return

        v_width, v_height = 1280, 720

        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            print(f"can't remove old video: {e}")
            output_path = os.path.join(photo_dir, f"output_{int(time.time())}.mp4")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_path, fourcc, 1, (v_width, v_height)) # 1 FPS

        for image in images:
            img_path = os.path.join(photo_dir, image)
            frame = cv2.imread(img_path)
            
            if frame is None:
                continue

            resized_frame = cv2.resize(frame, (v_width, v_height), interpolation=cv2.INTER_AREA)
            video.write(resized_frame)
            video.write(resized_frame)

        video.release()
        
        time.sleep(1)
        print(f" Video successfully created: {output_path}")
        return output_path





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
