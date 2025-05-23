@echo off
REM ───────────────────────────────────────────────────────────────────
REM 1) Create virtual environment
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create venv
    exit /b 1
)

REM 2) Activate it
call venv\Scripts\activate.bat
if "%VIRTUAL_ENV%"=="" (
    echo ERROR: Failed to activate venv
    exit /b 1
)

REM 3) Upgrade pip, setuptools, wheel
echo Upgrading pip, setuptools, wheel…
pip install --upgrade pip setuptools wheel

REM 4) Uninstall any OpenCV variants
echo Uninstalling any existing OpenCV packages…
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python opencv-contrib-python-headless

REM 5) Install the contrib build (with CSRT)
echo Installing opencv-contrib-python==4.8.1.78…
pip install --only-binary=:all: opencv-contrib-python==4.8.1.78

REM 6) Pin NumPy to 1.23.5
echo Installing numpy==1.23.5…
pip install --only-binary=:all: numpy==1.23.5

REM 7) Install Ultralytics without its own deps
echo Installing ultralytics (no dependencies)…
pip install ultralytics --no-deps

REM 8) Install remaining requirements
echo Installing streamlit, pandas, scipy, matplotlib, contourpy…
pip install --only-binary=:all: ^
    streamlit==1.45.1 ^
    pandas==2.0.1 ^
    scipy==1.9.3 ^
    matplotlib==3.7.1 ^
    contourpy==1.3.2

