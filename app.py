import streamlit as st
import cv2
import tempfile
import pandas as pd
from people_counter.detector import Detector
from people_counter.tracker import PeopleTracker

st.set_page_config(page_title="Video People Counter", layout="wide")
st.title("🕵️‍♀️ Video People Counter")

# Sidebar controls
model_path  = st.sidebar.text_input("YOLO model path", "yolo11l.pt")
conf_thresh = st.sidebar.slider("Detection confidence", 0.1, 1.0, 0.5, 0.05)
iou_thresh  = st.sidebar.slider("IOU threshold",       0.1, 1.0, 0.3, 0.05)
max_misses  = st.sidebar.number_input("Max tracker misses", 1, 30, 5)

# Upload or webcam
video_file = st.file_uploader("Upload a video file", type=["mp4","avi","mov"])
use_cam    = st.checkbox("Use Webcam (camera 0)")

# Only start processing when we have a source
if video_file or use_cam:
    # Prepare source path or device index
    if use_cam:
        source = 0
    else:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.write(video_file.read())
        source = tmp.name

    # Initialize detector & tracker
    detector = Detector(model_path, conf_thresh)
    tracker  = PeopleTracker(iou_thresh, max_misses)

    cap = cv2.VideoCapture(source)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    # Streamlit placeholders    
    video_pl  = st.empty()
    metric_pl = st.empty()

    # Collect time/count records
    records = []
    frame_idx = 0

    # Main loop
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1

        # Detection & counting
        dets  = detector.detect_people(frame)
        total = tracker.update(frame, dets)

        # Timestamp
        t_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        records.append({"time_sec": t_ms / 1000.0, "count": total})

        # Overlay
        cv2.putText(frame, f"Frame {frame_idx}/{total_frames}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame, f"Total Unique People: {total}", (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        # Show in Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_pl.image(frame_rgb, channels="RGB", use_container_width=True)
        metric_pl.metric("Live Unique Count", total)

        # Exit on keypress (works in local Python, Streamlit won’t catch it—
        # to stop, simply refresh or close the app).
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Final table
    df = pd.DataFrame(records)
    st.markdown("### 📊 People Count Over Time")
    st.dataframe(df)

else:
    st.info("Upload a video or check 'Use Webcam' to start counting.")
