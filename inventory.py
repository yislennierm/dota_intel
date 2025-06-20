import mss
import cv2
import numpy as np
import threading
import time
import os

# --- Configuration ---
TEMPLATE_FOLDER = "templates"
TEMPLATE_PATTERN = "tophero_"
MATCH_THRESHOLD = 0.75

# Define ROIs as percentages of the selected monitor: (left%, top%, width%, height%)
# 0.40 → 40% from the left of the monitor (horizontal offset)
# 0.02 → 2% from the top of the monitor (vertical offset)
# 0.20 → Width = 20% of the monitor width
# 0.08 → Height = 8% of the monitor height
ROI_DEFINITIONS = {
    "heroes_hud": (0.40, 0.20, 0.4, 0.10),
}

# Shared frame storage
latest_frames = {key: None for key in ROI_DEFINITIONS}


# --- Utility Functions ---

def select_monitor(monitors):
    print("Available monitors:")
    for idx, mon in enumerate(monitors[1:], start=1):
        print(f"{idx}: {mon}")
    selected = int(input("Select monitor number (e.g., 1): "))
    return monitors[selected]

def get_absolute_roi(monitor, roi_percent):
    x = int(monitor['left'] + roi_percent[0] * monitor['width'])
    y = int(monitor['top']  + roi_percent[1] * monitor['height'])
    w = int(roi_percent[2] * monitor['width'])
    h = int(roi_percent[3] * monitor['height'])
    return (x, y, w, h)

def detect_heroes_in_roi(frame, template_folder, pattern, threshold=0.7, scales=[0.8, 0.9, 1.0, 1.1, 1.2]):
    detected_heroes = []
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    for filename in os.listdir(template_folder):
        if not filename.startswith(pattern):
            continue
        hero_name = filename.replace(pattern, "").replace(".png", "")
        template_path = os.path.join(template_folder, filename)
        base_template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if base_template is None:
            continue

        for scale in scales:
            template = cv2.resize(base_template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            if template.shape[0] > frame_gray.shape[0] or template.shape[1] > frame_gray.shape[1]:
                continue
            result = cv2.matchTemplate(frame_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val >= threshold:
                detected_heroes.append((hero_name, max_loc, max_val))
                break  # stop at first successful scale

    return detected_heroes

# --- ROI Worker Thread ---

def roi_worker(name, monitor, roi_percent):
    roi = get_absolute_roi(monitor, roi_percent)
    region = {"left": roi[0], "top": roi[1], "width": roi[2], "height": roi[3]}
    with mss.mss() as sct:
        while True:
            sct_img = sct.grab(region)
            frame = np.array(sct_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            latest_frames[name] = frame
            time.sleep(0.01)  # Target ~100 fps


# --- Main Loop ---

def start_capture():
    with mss.mss() as sct:
        monitor = select_monitor(sct.monitors)

    for name, roi_percent in ROI_DEFINITIONS.items():
        thread = threading.Thread(target=roi_worker, args=(name, monitor, roi_percent), daemon=True)
        thread.start()

    session_heroes = set()
    radiant_team = []
    dire_team = []

    while True:
        for name, frame in latest_frames.items():
            if frame is not None:
                if name == "heroes_hud":
                    detected = detect_heroes_in_roi(frame, TEMPLATE_FOLDER, TEMPLATE_PATTERN, MATCH_THRESHOLD)
                    new_detected = [hero for hero, _, _ in detected if hero not in session_heroes]

                    if new_detected:
                        for hero in new_detected:
                            session_heroes.add(hero)
                            print(f"[+] New hero detected: {hero}")

                        if len(session_heroes) == 10 and not radiant_team and not dire_team:
                            all_heroes_sorted = sorted(session_heroes)
                            radiant_team = all_heroes_sorted[:5]
                            dire_team = all_heroes_sorted[5:]
                            print("\n--- Final Team Composition ---")
                            print(f"Radiant: {', '.join(radiant_team)}")
                            print(f"Dire:    {', '.join(dire_team)}")

                    # Draw rectangles on detected heroes
                    for hero, loc, _ in detected:
                        template_path = os.path.join(TEMPLATE_FOLDER, f"{TEMPLATE_PATTERN}{hero}.png")
                        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                        if template is not None:
                            h, w = template.shape
                            top_left = loc
                            bottom_right = (top_left[0] + w, top_left[1] + h)
                            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                            cv2.putText(frame, hero, (top_left[0], top_left[1] - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                cv2.imshow(f"{name.capitalize()} View", frame)

        if cv2.waitKey(1) == 27:  # ESC to exit
            break

    cv2.destroyAllWindows()


# --- Entry Point ---
if __name__ == "__main__":
    start_capture()
