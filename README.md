# 🎙️ Suzzy AI - Voice Assistant

![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

An intelligent, interactive AI Voice Assistant designed to understand voice commands and execute real-time actions such as opening **WhatsApp**, **YouTube**, telling the **current time**, providing live **weather reports**, performing **web searches**, solving math calculations, and more.

Supports both **Browser Web Deployment via Streamlit** (with Web Speech API & native audio recording) and **Local Desktop CLI Mode**.

---

## 🌟 Key Features

- 💬 **Open WhatsApp**: Say *"Open WhatsApp"* to automatically launch WhatsApp Web (`web.whatsapp.com`) with voice confirmation.
- ▶️ **Open YouTube & Search**: Say *"Open YouTube"* or *"Play Believer on YouTube"* to instantly search and play music/videos.
- ⏰ **Real-Time Clock & Date**: Say *"What is the time"* or *"What is today's date"* to get accurate verbal time and date announcements.
- 🌤️ **Live Weather**: Say *"Weather in Mumbai"* or *"Temperature in London"* for real-time weather reports.
- 🌐 **Web & App Shortcuts**: Instant voice launch for Google, GitHub, Gmail, Spotify, Instagram, Netflix, and Wikipedia.
- 🧮 **Voice Calculator**: Solves spoken arithmetic expressions (e.g., *"What is 25 times 40"*).
- 🎙️ **Dual-Mode Voice in Streamlit**:
  - **Live Web Speech API**: Client-side, real-time voice interaction with zero server latency.
  - **Streamlit Audio Recorder**: Server-side Google Speech Recognition + Google Text-to-Speech (`gTTS`) audio playback.
  - **Text Command Console**: Type commands when in a quiet environment.

---

## 📁 Project Structure

```text
suzzy-voice-assistant/
├── app.py                  # Main Streamlit web application
├── assistant_core.py       # Core intent parsing & command engine
├── voice.py                # Standalone desktop CLI voice assistant
├── requirements.txt        # Python dependencies for Streamlit deployment
├── .streamlit/
│   └── config.toml         # Custom dark theme configuration
├── settings.json           # VS Code / Python environment settings
└── README.md               # Documentation & deployment guide
```

---

## 🚀 Quick Start (Run Locally)

### 1. Clone the repository
```bash
git clone https://github.com/Saieshwar-web/suzzy-voice-assistant.git
cd suzzy-voice-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Streamlit Web Assistant
```bash
streamlit run app.py
```
Your browser will open automatically at `http://localhost:8501`.

---

## ☁️ Deploy on Streamlit Community Cloud (Free)

Deploying this voice assistant to the cloud allows you to access it from any phone or computer browser!

1. **Push your repository to GitHub**:
   ```bash
   git add .
   git commit -m "Add Streamlit voice assistant with WhatsApp and YouTube support"
   git push origin main
   ```

2. **Open Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io).
   - Sign in using your GitHub account.

3. **Deploy New App**:
   - Click **New app**.
   - Select your repository: `Saieshwar-web/suzzy-voice-assistant`.
   - Set Branch: `main`.
   - Set Main file path: `app.py`.
   - Click **Deploy!**

4. **Microphone Permission**:
   - When the web page loads, allow browser microphone access when prompted.

---

## 🖥️ Running Desktop CLI Mode

If you want to run the assistant locally using your PC's desktop microphone and SAPI5 speakers (including opening native desktop apps like Notepad or Calculator):

```bash
# Ensure PyAudio is installed (if not already installed)
pip install PyAudio pyttsx3

# Run desktop assistant
python voice.py
```
- Say *"Hey Suzy"* or *"Hey Suzzy"* to wake up the assistant.
- Give commands like *"Open WhatsApp"*, *"Open YouTube"*, *"What is the time"*, or *"Exit"*.

---

## 🗣️ Supported Voice Commands Cheat-Sheet

| Voice Command | Action Executed | Spoken Response |
| :--- | :--- | :--- |
| *"Open WhatsApp"* | Opens WhatsApp Web (`web.whatsapp.com`) | *"Opening WhatsApp Web for you."* |
| *"Open YouTube"* | Opens YouTube homepage | *"Opening YouTube."* |
| *"Play Shape of You on YouTube"* | Searches YouTube for the track | *"Playing Shape of You on YouTube."* |
| *"What is the time?"* | Reads the current local time | *"The time is 02:30 PM."* |
| *"What is today's date?"* | Reads current day and date | *"Today is Friday, 16 October."* |
| *"Weather in Mumbai"* | Queries OpenWeatherMap | *"The temperature in Mumbai is 28°C with clear sky."* |
| *"Search Artificial Intelligence"* | Searches Google | *"Here are the Google search results for Artificial Intelligence."* |
| *"What is 45 times 12?"* | Calculates math equation | *"The answer to 45 * 12 is 540"* |
| *"Tell me a joke"* | Tells a funny tech joke | Spoken joke |
| *"Open GitHub"* / *"Open Gmail"* | Launches respective website | *"Opening GitHub / Gmail."* |

---

## 📜 License
This project is open-source under the [MIT License](LICENSE).
