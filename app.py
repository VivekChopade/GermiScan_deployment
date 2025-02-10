from flask import Flask, request, render_template, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # This is your frontend page

@app.route('/about')
def about():
    return render_template('about.html')  # Render the about page

# Contact route
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/run_yolo', methods=['POST'])
def run_yolo():
    data = request.json
    command_type = data.get("command")  # Get which command to run

    if command_type == "realtime":
        command = "python yolo_detect.py --model my_model.pt --source usb0"
    elif command_type == "video":
        video_name = data.get("video_name", "seed.mp4")  # Default video file name
        command = f"python yolo_detect.py --model my_model.pt --source {video_name}"
    elif command_type == "image":
        image_name = data.get("image_name", "seed_test1.jpg")  # Default image file name
        command = f"python yolo_detect.py --model my_model.pt --source {image_name}"
    else:
        return jsonify({"status": "error", "message": "Invalid command"}), 400

    try:
        subprocess.Popen(command, shell=True)  # Runs the command without blocking
        return jsonify({"status": "success", "message": "Command executed!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)