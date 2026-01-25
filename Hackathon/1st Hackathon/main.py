import time
import cv2
import numpy as np
import socket
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
from collections import deque, Counter
import math

latest_gesture = "UNKNOWN"
latest_ts = 0.0
recv_buffer = ""
glove_status = "DISCONNECTED"
camera_status = "FRONTEND"
# MediaPipe landmarker
landmarker = None
# Latest flex values
latest_flex = None
latest_flex_ts = 0.0
WINDOW = 15
gesture_hist = deque(maxlen=WINDOW)
wrist_hist = deque(maxlen=WINDOW)
score_hist = deque(maxlen=WINDOW)
latest_confidence = 0.0
latest_stability = 0.0
latest_vision = 0.0
latest_consistency = 0.0

# ESP32 FLEX DATA
def get_flex_data(sock):
    global recv_buffer
    try:
        chunk = sock.recv(1024).decode(errors="ignore")
        if not chunk:
            return None
        recv_buffer += chunk
        if "\n" not in recv_buffer:
            return None
        line, recv_buffer = recv_buffer.split("\n", 1)
        parts = line.strip().split(",")
        if len(parts) != 5:
            return None
        values = [int(v) for v in parts]
        return {"Thumb": values[0], "Index": values[1], "Middle": values[2], "Ring": values[3], "Pinky": values[4]}
    except socket.timeout:
        return None
    except Exception as e:
        print("[ERROR] ESP32 recv error:", e)
        return None

# HAND PROCESSING
def get_hand_landmarks_from_bgr(frame_bgr):
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect(mp_image)

    if not result.hand_landmarks:
        return None, 0.0

    # choose Right hand if present, else first hand
    chosen_i = 0
    for i, handed in enumerate(result.handedness):
        label = handed[0].category_name
        if label == "Right":
            chosen_i = i
            break

    landmarks = result.hand_landmarks[chosen_i]
    vision_score = float(result.handedness[chosen_i][0].score) if result.handedness else 0.0
    return landmarks, vision_score

def get_finger_states(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    joints = [3, 6, 10, 14, 18]
    states = []
    for i in range(5):
        tip = hand_landmarks[tips[i]]
        joint = hand_landmarks[joints[i]]
        if i == 0:  # thumb (right-hand logic)
            states.append(1 if tip.x > joint.x else 0)
        else:
            states.append(1 if tip.y < joint.y else 0)
    return tuple(states)

def fuse_features(flex_data, finger_states, thresholds):
    flex_states = None
    vision_states = finger_states
    if flex_data is not None:
        flex_states = tuple(
            1 if flex_data[f] > thresholds[f] else 0
            for f in ["Thumb", "Index", "Middle", "Ring", "Pinky"]
        )
    if flex_states and vision_states:
        return tuple(flex_states[i] & vision_states[i] for i in range(5))
    elif vision_states:
        return vision_states
    elif flex_states:
        return flex_states
    else:
        return None

# CONFIDENCE ANALYSIS
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def compute_metrics():
    if len(gesture_hist) < 5:
        return None
    c = Counter(gesture_hist)
    most_common_g, most_common_n = c.most_common(1)[0]
    gesture_consistency = most_common_n / len(gesture_hist)
    if len(wrist_hist) >= 2:
        dist_sum = 0.0
        for i in range(1, len(wrist_hist)):
            x1,y1 = wrist_hist[i-1]
            x2,y2 = wrist_hist[i]
            dist_sum += math.sqrt((x2-x1)**2 + (y2-y1)**2)
        avg_jitter = dist_sum / (len(wrist_hist)-1)
    else:
        avg_jitter = 0.0
    jitter_scaled = clamp(avg_jitter / 0.02)  # tweak 0.02 based on your camera
    stability = clamp(1.0 - jitter_scaled)
    if len(score_hist) > 0:
        vision_score = sum(score_hist)/len(score_hist)
    else:
        vision_score = 0.0
    gesture_confidence = clamp(0.5*vision_score + 0.5*gesture_consistency)
    return {
        "gesture_consistency": gesture_consistency,
        "vision_score": vision_score,
        "avg_jitter": avg_jitter,
        "stability": stability,
        "gesture_confidence": gesture_confidence,
        "dominant_gesture": most_common_g
    }

# WORKER
def worker():
    global glove_status, landmarker, latest_flex, latest_flex_ts
    ESP32_IP = "192.168.1.10"
    ESP32_PORT = 5000
    MODEL_PATH = "hand_landmarker.task"

    # Load MediaPipe
    try:
        base_options = BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
        )
        landmarker = vision.HandLandmarker.create_from_options(options)
        print("[MediaPipe] HandLandmarker loaded:", MODEL_PATH)
    except Exception as e:
        print("[ERROR] Could not load hand_landmarker.task:", e)
        return
    esp_socket = None
    next_esp_retry = 0.0

    while True:
        now = time.time()

        # connection retry
        if esp_socket is None and now >= next_esp_retry:
            next_esp_retry = now + 2.0
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5)
                s.connect((ESP32_IP, ESP32_PORT))
                s.settimeout(0.2)
                esp_socket = s
                glove_status = "CONNECTED"
                print("[ESP32] Connected")
            except Exception:
                esp_socket = None
                glove_status = "DISCONNECTED"

        # read flex
        if esp_socket is not None:
            try:
                flex = get_flex_data(esp_socket)
                if flex is not None:
                    latest_flex = flex
                    latest_flex_ts = now
            except Exception:
                try:
                    esp_socket.close()
                except:
                    pass
                esp_socket = None

        # freshness status
        glove_status = "CONNECTED" if (now - latest_flex_ts) <= 2.0 else "DISCONNECTED"
        time.sleep(0.01)

# FASTAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    print("Worker started (NO camera in backend)")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend running. Camera is on FRONTEND. Use /status and /process_frame"}

@app.get("/status")
def status():
    return {
        "glove": glove_status,
        "camera": camera_status,
        "gesture": latest_gesture,
        "ts": latest_ts,
        "gesture_confidence": latest_confidence,
        "stability": latest_stability,
        "vision_score": latest_vision,
        "consistency": latest_consistency,
    }

# Frame API
class FrameIn(BaseModel):
    # JPEG frame base64 WITHOUT prefix: "data:image/jpeg;base64,"
    jpg_base64: str
    mirrored: bool = False  # if frontend is mirroring video (CSS transform), tell backend

@app.post("/process_frame")
def process_frame(payload: FrameIn):
    global latest_gesture, latest_ts
    if landmarker is None:
        return {"ok": False, "error": "MediaPipe model not loaded"}

    # decode base64 jpeg
    try:
        import base64
        jpg_bytes = base64.b64decode(payload.jpg_base64)
        np_arr = np.frombuffer(jpg_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            return {"ok": False, "error": "Bad image"}
    except Exception as e:
        return {"ok": False, "error": f"Decode failed: {e}"}

    # If frontend mirrors the video, handedness may invert. Option: flip back for correct handedness.
    if payload.mirrored:
        frame = cv2.flip(frame, 1)

    # Vision landmarks (Right hand)
    landmarks, vision_score = get_hand_landmarks_from_bgr(frame)

    finger_states = None
    if landmarks is not None:
        finger_states = get_finger_states(landmarks)

    # Fuse with latest flex
    flex_threshold = {"Thumb": 400, "Index": 420, "Middle": 430, "Ring": 415, "Pinky": 405}
    gesture_map = {
        (0,0,0,0,0): "FIST / CLOSED HAND",
        (1,1,1,1,1): "OPEN PALM",
        (0,1,0,0,0): "ONE",
        (0,1,1,0,0): "TWO",
        (0,1,1,1,0): "THREE",
        (0,1,1,1,1): "FOUR",
        (1,0,0,0,0): "THUMBS UP",
        (0,0,0,0,1): "PINKY",
        (0,0,0,1,0): "RING",
        (0,0,1,0,0): "MIDDLE",
        (0,1,0,0,1): "HANG LOOSE",
        (1,1,0,0,0): "GUN",
        (0,1,1,0,1): "LOVE SIGN",
    }

    fused = fuse_features(latest_flex, finger_states, flex_threshold)
    gesture = gesture_map.get(fused, "UNKNOWN") if fused is not None else "UNKNOWN"
    # History tracking
    gesture_hist.append(gesture)
    score_hist.append(float(vision_score))
    if landmarks is not None:
        wrist = landmarks[0]  # wrist landmark
        wrist_hist.append((float(wrist.x), float(wrist.y)))
    else:
        wrist_hist.append((0.0, 0.0))
    metrics = compute_metrics()
    # store latest gesture using metrics
    global latest_confidence, latest_stability, latest_vision, latest_consistency
    metrics = compute_metrics()
    if metrics:
        latest_gesture = metrics["dominant_gesture"]
        latest_confidence = metrics["gesture_confidence"]
        latest_stability = metrics["stability"]
        latest_vision = metrics["vision_score"]
        latest_consistency = metrics["gesture_consistency"]
        latest_ts = time.time()
    else:
        # fallback values when not enough data yet
        latest_confidence = 0.0
        latest_stability = 0.0
        latest_vision = 0.0
        latest_consistency = 0.0
    return {
        "ok": True,
        "gesture": latest_gesture,
        "ts": latest_ts,
        "glove": glove_status,
        "camera": camera_status,
        "gesture_confidence": latest_confidence,
        "stability": latest_stability,
        "vision_score": latest_vision,
        "consistency": latest_consistency,
    }
