# Architecture

```text
Input Source
  -> Frame Manager
  -> YOLO Person Detector
  -> Multi-Object Tracker
       -> CSRT baseline
       -> ByteTrack
       -> BoT-SORT
  -> Track Manager
       -> stable track IDs
       -> bounding boxes
       -> centroids
  -> Analytics Engine
       -> directional line crossing
       -> current occupancy
       -> zone occupancy
       -> trajectories
       -> dwell summaries
       -> FPS and latency
  -> Interfaces
       -> Streamlit
       -> CLI
  -> Outputs
       -> CSV
       -> JSON
       -> annotated MP4
```

## Why Line Crossing?

Counting newly created tracker IDs is fragile. A person can receive a new ID
after occlusion, detector dropout, low FPS, or camera movement. Directional line
crossing turns tracks into explicit events, which is a better match for use
cases such as entrances, exits, and occupancy monitoring.

## Tracker Strategy

CSRT remains available because it is easy to explain and useful as a baseline.
ByteTrack and BoT-SORT are included because they are stronger multi-object
tracking choices for detection-driven people tracking. ByteTrack is usually a
good fast default. BoT-SORT is useful when camera motion or identity stability
matters more.

## Limits

This system is still detection-based. It can fail in extremely dense crowds,
heavy occlusion, low light, or poor camera angles. For scenes where people are
not individually detectable, a true crowd-density estimation model is a more
appropriate approach.
