# NexCare AI — Intelligent Healthcare Ecosystem

NexCare AI is a high-performance, multi-page Hospital Management System (HMS) built with Streamlit. It provides a real-time command centre for hospital administrators, a secure portal for patients, and a clinical management tool for doctors.

##  Key Features

- **Admin Panel**: Real-time monitoring of resources (beds, staff, ambulances), automated patient risk assessment, and an AI-driven Crisis Mode for emergency surges.
- **Patient Portal**: Secure access to health records, clinical vitals tracking, treatment timelines, and lab results.
- **Doctor Panel**: Roster management, detailed clinical patient cards, and automated rounding schedules.
- **AI Risk Engine**: Rule-based clinical logic for high-risk patient alerts (Hypoxia, Tachycardia, Hypertension).
- **Sustainability Dashboard**: Real-time resource optimization metrics for hospital efficiency.

## 🛠️ Technology Stack

- **Frontend/Backend**: Streamlit (Python)
- **Data Engine**: Pandas & Custom Synthetic Data Simulator
- **Visualizations**: Plotly
- **Styling**: Custom Vanilla CSS (Apollo Hospital Brand Inspired)

## 💻 Installation & Running

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/NexCareAI.git
   cd NexCareAI
   ```

2. **Run the application**:
   - **Windows**: Simply double-click `run.bat`
   - **Manual**:
     ```bash
     pip install -r requirements.txt
     streamlit run Home.py
     ```

## 📂 Project Structure

- `Home.py`: Landing page and navigation portal.
- `pages/`: Individual dashboards (Admin, Patient, Doctor).
- `components/`: Modular UI elements (charts, alerts, crisis mode).
- `ai/`: Risk assessment engine logic.
- `data/`: Synthetic data simulator and providers.
- `assets/`: Custom CSS stylesheets for the premium UI.

---
*Developed for Hackathon 2025 · NexCare AI Team*
