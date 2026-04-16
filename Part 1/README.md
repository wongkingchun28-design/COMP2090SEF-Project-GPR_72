
# COMP2090SEF-Project-GPR_72
## Task 1: Healthcare Tracking System

A comprehensive desktop application designed to monitor, analyze, and visualize personal health data. Built with Python and PySide6, this system provides a centralized hub for tracking everything from vital signs and physical activity to mental well-being and hydration.

## Features

### 1. **Interactive Dashboard**
- **Dynamic Visualizations:** Includes "beating" heart rate animations, progress rings for calories and hydration, and categorized bar charts.
- **Categorized Tracking:**
    - **Vitals:** Heart Rate (BPM) and Blood Pressure (mmHg).
    - **Physical:** BMI, Physical Activity (METs/Kcal), and Hydration.
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

## Installation

### Prerequisites
- Python 3.9 or higher
- `pip` (Python package manager)

### Dependencies
Install the required libraries using the following command:

```bash
pip install PySide6 matplotlib fpdf2 opencv-python
```

---

## File Structure

- **`GUI.py`**: The main entry point. Handles the UI logic, page switching, and user interactions.
- **`Base.py`**: Manages user profiles (Name, Age, Gender, Goals) and JSON persistence.
- **`ReportGenerator.py`**: Logic for converting CSV data into a structured PDF report.
- **`PlotGraph.py`**: Handles the parsing of CSV data and generating Matplotlib charts.
- **`question.py`**:  Question list for PHQ9&GAD7
- **`user_health_data.csv`**: A structured repository for persisting user-reported metrics and historical logs. 
- **`user_profile.json`**:  Data for user profiles
- **`determine/` (Module)**: Logic for vitals interpretation
    - `BaseAnalyzer.py`
    - `HeartRate.py`
    - `BloodPressure.py`
    - `PHQ9andGAD7.py`
    - `weight.py`
    - `StoolAndUrine.py`
- **`exercise_dataset.csv`**: Reference data for calculating calories burned per activity.
- **`HeartRateStatus.json`**: Reference chart for heart rate fitness based on age/gender.

---

## Usage

### 1. **Run the Application:**
   ```bash
   python GUI.py
   ```
   or click run GUI.py on your idle
   
### 2. After run the GUI.py you should see this page

<img width="1081" height="1662" alt="螢幕擷取畫面 2026-04-16 012812" src="https://github.com/user-attachments/assets/35df15cc-5742-4489-b6cf-26955426dc9a" />

### 3. You can click on any **Input** button, it will pop up a small window to ask you to input

<img width="1077" height="1662" alt="螢幕擷取畫面 2026-04-16 012828" src="https://github.com/user-attachments/assets/a52b26ab-9c9f-4e1d-bbb7-9678753556b3" />

### 4. For the Mental Wellbeing, there will be two type of question, choose one to answer

<img width="539" height="163" alt="螢幕擷取畫面 2026-04-16 013046" src="https://github.com/user-attachments/assets/d5108407-a84e-4c41-a680-58f642821286" />

### 5. The question will bee like this

<img width="756" height="698" alt="螢幕擷取畫面 2026-04-16 013052" src="https://github.com/user-attachments/assets/088044fb-294e-4c73-9a97-fd87d676e478" />

### 6. After answer all the question, it will show you the reesult

<img width="744" height="308" alt="螢幕擷取畫面 2026-04-16 013103" src="https://github.com/user-attachments/assets/48d34311-c53d-4d98-9d40-c7c9caec5682" />

### 7. For the **Daily Photo log**, it will show you the photo you input on the same day

<img width="482" height="191" alt="螢幕擷取畫面 2026-04-16 015713" src="https://github.com/user-attachments/assets/dfc5e606-4942-46da-95b7-7ba3cdf590dd" />

### 8. Click on **Trend**, you will see **Generate Play Photo Recap Video** button click on it you will see the video make of all of your photos
### 9. Also on the **Trend Page**, there will be graph that show the trend of your data 

<img width="1039" height="1560" alt="螢幕擷取畫面 2026-04-16 015729" src="https://github.com/user-attachments/assets/217228f9-de55-4b8c-b21a-cb84ab46be52" />

### 10. You can scroll down on **Trend Page**, at the bottom you will see **Export Full Health Report (PDF)** click it and you can get your data in pdf format

<img width="1063" height="1645" alt="螢幕擷取畫面 2026-04-16 015742" src="https://github.com/user-attachments/assets/a682d1c2-628f-4747-917b-6231bd41ae35" />

### 11. On **User Page**, it will list your personal data

<img width="1064" height="1638" alt="螢幕擷取畫面 2026-04-16 015802" src="https://github.com/user-attachments/assets/24766d48-5e4e-4725-8173-7e5529e0304d" />

### 12. You can edit all the data and it will refresh the data immediately

<img width="1054" height="1636" alt="螢幕擷取畫面 2026-04-16 015813" src="https://github.com/user-attachments/assets/dc54f4fe-a9b9-4e00-b3cd-a572256cdf41" />







---

## Data Storage
- **`user_profile.json`**: Stores basic user metrics.
- **`user_health_data.csv`**: A pipe-delimited log of every entry made in the system, categorized by date and time.
- **`/photos`**: Directory where uploaded progress images are stored.

---
### Data & Knowledge Sources

* **Resting Heart Rate Guidance**: Reference provided by [CR Fitness](https://crfitnessdotnet.wordpress.com/how-to-take-a-resting-heart-rate/).
* **Exercise Dataset**: [Calories Burned During Exercise and Activities](https://www.kaggle.com/datasets/aadhavvignesh/calories-burned-during-exercise-and-activities) 
    * **Author**: Vignesh, A. (2023)
    * **License**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
---

### Clinical Assessment Tools

* **Depression Severity (PHQ-9)**: Referenced from the [Patient Health Questionnaire-9](https://www.mdcalc.com/calc/1725/phq9-patient-health-questionnaire9).
* **Anxiety Screening (GAD-7)**: Referenced from the [General Anxiety Disorder-7](https://www.mdcalc.com/calc/1727/gad7-general-anxiety-disorder7).

---
## Disclaimer
*This system is intended for personal tracking and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a physician or other qualified health provider with any questions regarding a medical condition.*

---
**Developed for:** COMP2090SEF Project
