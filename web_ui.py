import jetson.inference
import jetson.utils
import cv2
from flask import Flask, Response, jsonify

app = Flask(__name__)

# Load the model
net = jetson.inference.imageNet(argv=[
    '--model=models/pro_trashnet/resnet18.onnx', 
    '--labels=models/pro_trashnet/labels.txt', 
    '--input_blob=input_0', 
    '--output_blob=output_0'
])
# Start the camera
camera = jetson.utils.videoSource("/dev/video0")

current_result = {"name": "AWAITING SCAN...", "recyclable": "Place Item", "color": "gray"}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Vision Garbage Sorting</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #0f1115; color: #fff; display: flex; height: 100vh; margin: 0; overflow: hidden; }
        #left { flex: 7; display: flex; justify-content: center; align-items: center; padding: 20px; background: #000; }
        #right { flex: 3; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #1a1d24; padding: 30px; box-shadow: -10px 0 20px rgba(0,0,0,0.5); z-index: 10; }
        img { width: 100%; max-height: 100%; object-fit: contain; border-radius: 12px; }
        .title { color: #888; font-size: 1.2rem; margin-bottom: 10px; letter-spacing: 2px; text-transform: uppercase; }
        #item-name { font-size: 3rem; font-weight: bold; margin: 0 0 40px 0; text-transform: uppercase; text-align: center; }
        .badge { padding: 20px 40px; font-size: 2.2rem; font-weight: bold; border-radius: 20px; transition: all 0.2s ease; }
        .green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: #fff; }
        .red { background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%); color: #fff; }
        .gray { background: #2a2e37; color: #666; }
    </style>
</head>
<body>
    <div id="left"><img src="/video_feed" alt="Camera Feed"></div>
    <div id="right">
        <div class="title">Current Target</div>
        <h1 id="item-name">AWAITING SCAN...</h1>
        <div id="recycle-badge" class="badge gray">Place Item</div>
    </div>
    <script>
        setInterval(() => {
            fetch('/api/result').then(res => res.json()).then(data => {
                document.getElementById('item-name').innerText = data.name;
                let badge = document.getElementById('recycle-badge');
                badge.innerText = data.recyclable;
                badge.className = 'badge ' + data.color;
            });
        }, 500); 
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_PAGE

@app.route('/api/result')
def get_result():
    return jsonify(current_result)

def generate_video():
    global current_result
    while True:
        img = camera.Capture()
        class_idx, confidence = net.Classify(img)
        
        if class_idx >= 0 and confidence > 0.6:
            name = net.GetClassDesc(class_idx)
            if name in ['cardboard', 'glass', 'metal', 'paper', 'plastic']:
                current_result = {"name": name.upper(), "recyclable": "♻️ RECYCLABLE", "color": "green"}
            else:
                current_result = {"name": name.upper(), "recyclable": "❌ NON-RECYCLABLE", "color": "red"}
        else:
            current_result = {"name": "SCANNING...", "recyclable": "STANDBY", "color": "gray"}
        
        array = jetson.utils.cudaToNumpy(img)
        array_bgr = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        ret, jpeg = cv2.imencode('.jpg', array_bgr)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
