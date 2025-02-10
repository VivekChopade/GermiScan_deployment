import os
import sys
import argparse
import glob
import time
import cv2
import numpy as np
from ultralytics import YOLO

# Define and parse user input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--model', help='Path to YOLO model file (example: "runs/detect/train/weights/best.pt")', required=True)
parser.add_argument('--source', help='Image source, can be image file ("test.jpg"), image folder ("test_dir"), video file ("testvid.mp4"), or index of USB camera ("usb0")', required=True)
parser.add_argument('--thresh', help='Minimum confidence threshold for displaying detected objects (example: "0.4")', default=0.5)
parser.add_argument('--resolution', help='Resolution in WxH to display inference results at (example: "640x480"), otherwise, match source resolution', default=None)
parser.add_argument('--record', help='Record results from video or webcam and save it as "demo1.avi". Must specify --resolution argument to record.', action='store_true')

args = parser.parse_args()

# Parse user inputs
model_path = args.model
img_source = args.source
min_thresh = args.thresh
user_res = args.resolution
record = args.record

# Check if model file exists and is valid
if not os.path.exists(model_path):
    print('ERROR: Model path is invalid or model was not found. Make sure the model filename was entered correctly.')
    sys.exit(0)

# Load the model into memory and get label map
model = YOLO(model_path, task='detect')
labels = model.names

# Define germination logic
def get_germination_rate(classname, conf):
    if classname in ['rice', 'wheat', 'chickpea']:
        if conf * 100 < 5:
            return '<5'
        else:
            return '>5'
    return '<5'

# Parse input to determine if image source is a file, folder, video, or USB camera
img_ext_list = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.bmp', '.BMP']
vid_ext_list = ['.avi', '.mov', '.mp4', '.mkv', '.wmv']

if os.path.isdir(img_source):
    source_type = 'folder'
elif os.path.isfile(img_source):
    _, ext = os.path.splitext(img_source)
    if ext in img_ext_list:
        source_type = 'image'
    elif ext in vid_ext_list:
        source_type = 'video'
    else:
        print(f'File extension {ext} is not supported.')
        sys.exit(0)
elif 'usb' in img_source:
    source_type = 'usb'
    usb_idx = int(img_source[3:])
else:
    print(f'Input {img_source} is invalid. Please try again.')
    sys.exit(0)

# Parse user-specified display resolution
resize = False
if user_res:
    resize = True
    resW, resH = int(user_res.split('x')[0]), int(user_res.split('x')[1])

# Check if recording is valid and set up recording
if record:
    if source_type not in ['video', 'usb']:
        print('Recording only works for video and camera sources. Please try again.')
        sys.exit(0)
    if not user_res:
        print('Please specify resolution to record video at.')
        sys.exit(0)
    
    # Set up recording
    record_name = 'demo1.avi'
    record_fps = 30
    recorder = cv2.VideoWriter(record_name, cv2.VideoWriter_fourcc(*'MJPG'), record_fps, (resW, resH))

# Load or initialize image source
if source_type == 'image':
    imgs_list = [img_source]
elif source_type == 'folder':
    imgs_list = []
    filelist = glob.glob(img_source + '/*')
    for file in filelist:
        _, file_ext = os.path.splitext(file)
        if file_ext in img_ext_list:
            imgs_list.append(file)
elif source_type == 'video' or source_type == 'usb':
    if source_type == 'video':
        cap_arg = img_source
    elif source_type == 'usb':
        cap_arg = usb_idx
    cap = cv2.VideoCapture(cap_arg)
    if user_res:
        ret = cap.set(3, resW)
        ret = cap.set(4, resH)

# Function to resize frame to fit the screen
def resize_to_fit_screen(frame):
    # Get screen resolution (you can adjust these values based on your screen)
    screen_width = 1920  # Default screen width
    screen_height = 1080  # Default screen height
    
    # Get frame dimensions
    frame_height, frame_width = frame.shape[:2]
    
    # Calculate scaling factor to fit the frame within the screen
    scale_width = screen_width / frame_width
    scale_height = screen_height / frame_height
    scale = min(scale_width, scale_height)
    
    # Resize the frame while maintaining aspect ratio
    new_width = int(frame_width * scale)
    new_height = int(frame_height * scale)
    resized_frame = cv2.resize(frame, (new_width, new_height))
    
    return resized_frame

# Function to process a single frame
def process_frame(frame):
    if resize:
        frame = cv2.resize(frame, (resW, resH))

    results = model(frame, verbose=False)
    detections = results[0].boxes
    object_count = 0

    for i in range(len(detections)):
        xyxy = detections[i].xyxy.cpu().numpy().squeeze().astype(int)
        xmin, ymin, xmax, ymax = xyxy
        classidx = int(detections[i].cls.item())
        classname = labels[classidx]
        conf = detections[i].conf.item()
        germination_rate = get_germination_rate(classname, conf)
        
        color = (0, 255, 0)
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
        label = f'{classname}: {int(conf*100)}% | {germination_rate}'
        cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        object_count += 1
    
    cv2.putText(frame, f'Objects: {object_count}', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 255, 255), 2)
    
    # Resize the frame to fit the screen
    resized_frame = resize_to_fit_screen(frame)
    cv2.imshow('YOLO detection results', resized_frame)
    
    if record and source_type in ['video', 'usb']:
        recorder.write(frame)

# Handle image or folder sources
if source_type in ['image', 'folder']:
    for img_path in imgs_list:
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"Error: Unable to load image {img_path}.")
            continue
        process_frame(frame)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

# Handle video or USB camera sources
elif source_type in ['video', 'usb']:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        process_frame(frame)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

    if record:
        recorder.release()
    cap.release()
    cv2.destroyAllWindows()