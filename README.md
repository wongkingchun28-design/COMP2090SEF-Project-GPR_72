# COMP2090SEF-Project-GPR_72
## 🏥 Healthcare Tracking System

A comprehensive desktop application designed to monitor, analyze, and visualize personal health data. Built with Python and PySide6, this system provides a centralized hub for tracking everything from vital signs and physical activity to mental well-being and hydration.

## 🚀 Features

### 1. **Interactive Dashboard**
- **Dynamic Visualizations:** Includes "beating" heart rate animations, progress rings for calories and hydration, and categorized bar charts.
- **Categorized Tracking:**
    - **Vitals:** Heart Rate (BPM) and Blood Pressure (mmHg).
    - **Physical:** Body Composition (BMI), Physical Activity (METs/Kcal), and Hydration.
    - **Lifestyle:** Sleep Quality (Time Range), Dietary Intake, and Medication logs.
    - **Diagnostics:** Digestive Health (Urine color & Stool type based on the Bristol Scale).

### 2. **Advanced Health Analysis**
- **Clinical Interpretations:** Uses backend analyzers to categorize data (e.g., Stage 1 Hypertension, BMI status, Heart Rate fitness levels).
- **Mental Health Assessments:** Integrated **PHQ-9 (Depression)** and **GAD-7 (Anxiety)** surveys with automated scoring and recommendations.
- **MET-based Exercise Tracking:** Calculate calorie burn using a built-in dataset of over 200 activities.

### 3. **Visual & Multimedia Logging**
- **Daily Photo Log:** Users can upload daily progress photos.
- **Video Recap:** Automatically generates a time-lapse video recap of saved photos using OpenCV to visualize physical transformations.

### 4. **Data Management & Reporting**
- **CSV Storage:** All data is logged with timestamps in a structured CSV format for portability.
- **Trend Analysis:** High-quality Matplotlib graphs showing health trends over time (Weight, BP, Heart Rate, etc.).
- **PDF Report Generation:** Generate a professional, multi-page PDF summary including user profile info, trend graphs, and detailed record logs.

---

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- `pip` (Python package manager)

### Dependencies
Install the required libraries using the following command:

```bash
pip install PySide6 matplotlib fpdf2 opencv-python
```

---

## 📂 File Structure

- **`GUI.py`**: The main entry point. Handles the UI logic, page switching, and user interactions.
- **`Base.py`**: Manages user profiles (Name, Age, Gender, Goals) and JSON persistence.
- **`ReportGenerator.py`**: Logic for converting CSV data into a structured PDF report.
- **`PlotGraph.py`**: Handles the parsing of CSV data and generating Matplotlib charts.
- **`determine/` (Module)**:
    - `BaseAnalyzer.py`: Abstract base class for all health logic.
    - `HeartRate.py` & `BloodPressure.py`: Logic for vitals interpretation.
    - `PHQ9andGAD7.py`: Scoring logic for mental health surveys.
    - `weight.py`: BMI calculations.
    - `StoolAndUrine.py`: Logic for digestive health summaries.
- **`exercise_dataset.csv`**: Reference data for calculating calories burned per activity.
- **`HeartRateStatus.json`**: Reference chart for heart rate fitness based on age/gender.

---

## 🖥️ Usage

1. **Run the Application:**
   ```bash
   python GUI.py
   ```
2. **Setup Profile:** Navigate to the **User** tab to set your age, height, and daily calorie goals.
3. **Log Data:** Click **INPUT** on any dashboard tile (e.g., Heart Rate) to enter new data.
4. **View Trends:** Go to the **Trend** tab to see visual graphs of your progress over time.
5. **Generate Report:** In the **Trend** tab, click "Export Full Health Report" to save a PDF of your history.
6. **Photo Recap:** Upload photos in the "Daily Photo Log" and click "Generate & Play Video" to see your journey.

---

## 📊 Data Storage
- **`user_profile.json`**: Stores basic user metrics.
- **`user_health_data.csv`**: A pipe-delimited log of every entry made in the system, categorized by date and time.
- **`/photos`**: Directory where uploaded progress images are stored.

---

## ⚖️ Disclaimer
*This system is intended for personal tracking and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a physician or other qualified health provider with any questions regarding a medical condition.*

---
**Developed for:** COMP2090SEF Project
