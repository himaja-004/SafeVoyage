
## SafeVoyage: Intelligent Routing and Real-Time Risk Alerts for Safe Travel

SafeVoyage is a smart web-based navigation assistant that prioritizes user safety by analyzing routes using real-time and historical data, visualizing safety levels, and enabling community feedback. It helps users select the safest path to their destination and can send SOS alerts to emergency contacts.

## 📌 Features
✅ Login & Registration: Secure user authentication system.

🗺️ Safe Route Visualization: All places on the map are marked with safety indicators using pointer markers:

    🟢 Safe
    
    🟠 Moderate
    
    🔴 Risky

Multiple route options between your source and destination are displayed. Use the safety markers across all locations to assess and choose the safest route.

📊 Safety Percentage Display: Users can view safety scores of available routes.

📝 User Feedback System:

Submit safety feedback for any area.

View processed feedback summaries, including safety ratings, comments, and visuals.

🚨 SOS Alerts:

Sends an emergency message with live location to registered contacts using Fast2SMS API.

🧠 Machine Learning: Gaussian Mixture Model (GMM) used for safety classification based on accident and incident data.

📍 Geolocation Support: Automatically fetch user location for SOS.


## ⚙️ Technologies Used

Backend: Python Flask

Frontend: HTML, CSS (custom styling)

Database: SQLite

Routing API: OpenRouteService

Map Rendering: Folium

Model: Gaussian Mixture Model (scikit-learn)


## 🗂️ Folder Structure

SafeVoyage/

├── app.py                  # Main Flask app

├── generate_map.py         # Route calculation and map rendering

├── templates/              # HTML templates

│   ├── login.html

│   ├── register.html

│   ├── home.html

│   ├── feedback.html

│   └── view_feedback.html

├── static/                 # Static files (images, styles)

│   └── Styles.css

├── safety_data.db          # SQLite database

├── .env                    # Environment variables (API keys)

├── README.md               # Project documentation


## 🚀 How Tt Works

User logs in / registers.

On the homepage, user enters source and destination.

App fetches multiple route options from OpenRouteService.

Each route is analyzed for proximity to high-risk points using GMM.

Routes are displayed with safety scores and color codes.

User can:

Submit detailed safety feedback.

View feedback summaries.

Send SOS alerts with live location to emergency contacts.

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/SafeVoyage.git
   cd SafeVoyage
   ```

2. **Create virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API Key**:
   Create a `.env` file with:
   ```
   ORS_API_KEY=your_openrouteservice_api_key
   FAST2SMS_API_KEY=your_fast2sms_api_key
   ```

5. **Run the application**:
   ```bash
   python generate_map.py
   python app.py
   ```

6. Open browser at `http://localhost:5000`.
