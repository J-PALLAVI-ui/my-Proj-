# FujiNova (富士ノヴァ) — Easy Windows Runner Guide

Welcome to FujiNova! This guide explains how to start and use the application on Windows without needing any programming knowledge.

---

## ⚡ Quick Start: 3 Simple Steps

### Step 1: Install Prerequisites (One-time only)
Ensure you have the following installed on your computer:
1. **Python** (version 3.11, 3.12, 3.13, or 3.14):
   - Download from: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - *Important:* During installation, make sure to check **"Add python.exe to PATH"**.
2. **Node.js** (LTS version):
   - Download from: [https://nodejs.org/](https://nodejs.org/)

---

### Step 2: Start FujiNova
1. Open the project folder (`FujiNova`).
2. **Double-click `START_FUJINOVA.bat`**.
3. A command prompt window will open and perform all setup automatically:
   - Sets up the Python environment and installs dependencies.
   - Installs frontend packages.
   - Prepares the database with Mount Fuji attractions.
   - Starts both the backend API and frontend web app.
4. When ready, FujiNova will **automatically open in your default web browser** at:
   - **Web App:** [http://localhost:5173](http://localhost:5173)

---

### Step 3: Stop FujiNova
When you are done using the application:
- **Double-click `STOP_FUJINOVA.bat`**.
- This safely stops all background server processes and frees up system ports.

---

## 🔑 How to Add an AI API Key (Optional)

FujiNova functions out of the box with built-in verified answers. If you want Hana to have full conversational capabilities using live AI models:

1. Look for the file named `.env` in the main folder.
2. Open `.env` with Notepad.
3. Replace the placeholder with your actual API key:
   - **For OpenAI:**
     ```ini
     OPENAI_API_KEY=sk-your_actual_key_here
     ```
   - **Or for Google Gemini:**
     ```ini
     FUJINOVA_PRIMARY_PROVIDER=google
     GEMINI_API_KEY=your_actual_gemini_key_here
     ```
4. Save and close Notepad.
5. Restart the app using `STOP_FUJINOVA.bat` and then `START_FUJINOVA.bat`.

---

## 🧭 Main Pages & Features in the App

When you open [http://localhost:5173](http://localhost:5173), you can switch between 5 workspaces using the top navigation bar:

1. **Hana Assistant:** Chat with your AI travel companion, ask travel questions, and build personalized trip plans.
2. **Discover:** Browse verified Mount Fuji attractions, onsens, viewpoints, and cultural heritage sites.
3. **CrowdSense:** See real-time and predicted crowd levels across attractions, with smart alternative suggestions to avoid long queues.
4. **Your Journey:** View detailed public transit schedules (Fujikyu train and bus routes) with exact times and ticket fares.
5. **My Travel:** Save and customize your multi-day itinerary.

---

## ❓ Troubleshooting Common Issues

### Issue 1: "Python was not found" or "Node is not recognized"
- **Solution:** Reinstall Python or Node.js from the official links above, making sure to enable the **"Add to PATH"** checkbox. Restart your computer if needed.

### Issue 2: "Port 8000 or 5173 is already in use"
- **Solution:** Run `STOP_FUJINOVA.bat` to terminate any hanging instances, then run `START_FUJINOVA.bat` again.

### Issue 3: Browser didn't open automatically
- **Solution:** Manually open your web browser (Chrome, Edge, Firefox, Brave) and navigate to:
  `http://localhost:5173`

### Issue 4: Backend API Status
- You can check if the backend is running properly by visiting:
  - Health check: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
  - Interactive API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
