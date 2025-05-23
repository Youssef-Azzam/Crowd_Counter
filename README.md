# 🚦 **Automated Crowd Counter** 🚦

_A smart solution to count people in busy scenes in real time, using YOLO for detection and CSRT+IoU for robust tracking._

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)  
[![License](https://img.shields.io/badge/License-MIT-green?logo=github&logoColor=white)](LICENSE)  
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-orange?logo=streamlit&logoColor=white)](https://streamlit.io)  
[![Ultralytics](https://img.shields.io/badge/Ultralytics-8.3.140-red?logo=youtube&logoColor=white)](https://github.com/ultralytics/ultralytics)

---

## 📚 Table of Contents

- 📌 [Overview](#-overview)
- 🧠 [Features](#-features)
- 🛠️ [Installation & Setup](#-installation--setup)
- 🚀 [Getting Started](#-getting-started)
- 🎯 [Usage](#-usage)
- 🎥 [Demo](#-demo)
- 📁 [Project Structure](#-project-structure)
- 💡 [How It Works](#-how-it-works)
- 🧪 [Testing](#-testing)
- ❓ [FAQ](#-faq)
- 🧰 [Tech Stack](#-tech-stack)
- 🙋‍♂️ [Contributing](#-contributing)
- 📝 [License](#-license)

## 📌 Overview

Welcome to the 🧍‍♂️🧍‍♀️ People Detection & Tracking System!  
This project is a robust, real-time object detection and tracking solution built using the Ultralytics YOLOv11 model and OpenCV’s powerful CSRT tracker. The system counts people across video frames, tracks their movement, and visualizes their trajectories.

This was created as a research-grade tool with performance, clarity, and flexibility in mind. It can be extended for smart surveillance systems, retail footfall analysis, or any application involving human activity tracking.

> 🛠️ A huge part of the development effort went into managing conflicting dependencies (OpenCV contrib, Ultralytics, Torch, etc.) — don't worry, we’ve got a clean and simple setup process covered below. 🎯

---

## 🧠 Features

✨ Real-Time Object Detection with YOLOv11-Large      
📦 Lightweight & Fast Tracking via CSRT (Disambiguates overlapping people)  
📊 People Counter with Dynamic Updates  
🎨 Visual Bounding Boxes & ID Tracking  
🧩 Modular Codebase for Easy Customization  
📽️ Works with webcam feeds, video files, or RTSP streams  
📂 Well-structured project with clean logging & streamlit UI support  
📌 Compatible with OpenCV Contrib and modern Torch versions  

## 🧭 Architecture & Design

The system is built around modular, clean Python files designed for readability and scalability. Here’s a bird’s-eye view:

![Architecture Diagram](docs/architecture.png)


### 🧰 Modules

- **app.py**  
  🎬 Main entry point. Loads video stream, runs detection, tracking, and counting loop.  
- **detector.py**  
  🔍 Wrapper around Ultralytics YOLOv8 to detect people in frames.  
- **tracker.py**  
  🎯 Handles object tracking using OpenCV’s CSRT tracker, assigning unique IDs.  
- **people_counter/**  
  📦 Sub-package that organizes business logic:  
  - **counter.py** → counts people across frames  
  - **utils.py** → helper functions (drawing boxes, logging, etc.)  
  - **tracker_config.yaml** → tuning parameters  
- **requirements.txt**  
  📄 All pinned dependencies required for successful setup.
  