# How to Publish This Project on GitHub

Use this guide if you are new to Git and GitHub.

## What You Have Now

Your upgraded local project folder is:

```text
D:\Courses of SEMESTER-8\Advanced AI (Computer Vision)\Crowd_Counter_upgraded
```

This folder is not automatically published. GitHub will only change after you
run Git commands yourself.

## Step 1: Install Git

If Git is not installed, download it from:

```text
https://git-scm.com/downloads
```

During installation, the default options are fine.

## Step 2: Open Terminal

On Windows:

1. Open the folder in File Explorer.
2. Click the address bar.
3. Type `cmd`.
4. Press Enter.

Or open PowerShell manually.

## Step 3: Go to the Project Folder

In the terminal, run:

```bat
cd /d "D:\Courses of SEMESTER-8\Advanced AI (Computer Vision)\Crowd_Counter_upgraded"
```

## Step 4: Test the Project Locally

Create a virtual environment:

```bat
python -m venv .venv
```

Activate it:

```bat
.venv\Scripts\activate
```

Install dependencies:

```bat
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Run tests:

```bat
pytest
```

Run the app:

```bat
streamlit run app.py
```

If Streamlit opens in your browser, the project is ready to publish.

## Step 5: Publish to Your Existing GitHub Repository

If you want to update this existing repository:

```text
https://github.com/Youssef-Azzam/Crowd_Counter
```

First clone it somewhere separate:

```bat
cd /d "D:\Courses of SEMESTER-8\Advanced AI (Computer Vision)"
git clone https://github.com/Youssef-Azzam/Crowd_Counter.git Crowd_Counter_github
cd Crowd_Counter_github
```

Create a new branch:

```bat
git checkout -b upgrade-analytics-tracking
```

Now copy all files from:

```text
D:\Courses of SEMESTER-8\Advanced AI (Computer Vision)\Crowd_Counter_upgraded
```

into:

```text
D:\Courses of SEMESTER-8\Advanced AI (Computer Vision)\Crowd_Counter_github
```

When Windows asks whether to replace files, choose replace.

Then remove files that should no longer be tracked:

```bat
git rm -r --cached venv people_counter/__pycache__ yolo11l.pt
```

If one of those paths says it does not exist, that is okay. Continue.

Stage your files:

```bat
git add .
```

Check what will be committed:

```bat
git status
```

Commit:

```bat
git commit -m "Upgrade crowd counter analytics and tracking pipeline"
```

Push to GitHub:

```bat
git push origin upgrade-analytics-tracking
```

Then go to GitHub in your browser. GitHub will show a button to create a Pull
Request. Click it, review the files, then merge when you are happy.

## Step 6: Alternative - Push Directly to Main

Only do this if you are comfortable replacing the current repo immediately:

```bat
git checkout main
git add .
git commit -m "Upgrade crowd counter analytics and tracking pipeline"
git push origin main
```

Using a branch is safer.
