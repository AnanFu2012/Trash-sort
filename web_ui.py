import jetson.inference
import jetson.utils
import cv2
from flask import Flask, Response, jsonify

app = Flask(__name__)

# 1. 挂载你跑完 40 轮的完全体大模型
net = jetson.inference.imageNet(argv=[
    '--model=models/pro_trashnet/resnet18.onnx', 
    '--labels=models/pro_trashnet/labels.txt', 
    '--input_blob=input_0', 
    '--output_blob=output_0'
])
# 2. 启动你的罗技 C270 摄像头
camera = jetson.utils.videoSource("/dev/video0")

# 存储当前识别结果的全局变量
current_result = {"name": "等待识别...", "recyclable": "请放入物品", "color": "gray"}

# 3. 内嵌的 HTML、CSS 和 JavaScript
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>AI 视觉垃圾分拣系统</title>
    <style>
        body { font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; background-color: #0f1115; color: #fff; display: flex; height: 100vh; margin: 0; overflow: hidden; }
        #left { flex: 7; display: flex; justify-content: center; align-items: center; padding: 20px; background: #000; }
        #right { flex: 3; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #1a1d24; padding: 30px; box-shadow: -10px 0 20px rgba(0,0,0,0.5); z-index: 10; }
        img { width: 100%; max-height: 100%; object-fit: contain; border-radius: 12px; }
        .title { color: #888; font-size: 1.2rem; margin-bottom: 10px; letter-spacing: 2px; }
        #item-name { font-size: 3rem; font-weight: bold; margin: 0 0 40px 0; text-transform: uppercase; text-align: center; }
        .badge { padding: 20px 40px; font-size: 2.2rem; font-weight: bold; border-radius: 20px; transition: all 0.2s ease; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: #fff; }
        .red { background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%); color: #fff; }
        .gray { background: #2a2e37; color: #666; box-shadow: none; }
    </style>
</head>
<body>
    <div id="left">
        <img src="/video_feed" alt="Camera Feed">
    </div>
    <div id="right">
        <div class="title">当前锁定目标</div>
        <h1 id="item-name">等待识别...</h1>
        <div id="recycle-badge" class="badge gray">请放入物品</div>
    </div>

    <script>
        // JS 轮询：每秒向后端拉取 2 次识别结果，动态更新 DOM
        setInterval(() => {
            fetch('/api/result')
                .then(res => res.json())
                .then(data => {
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
        
        # 自信度 > 60% 才更新 UI，防止背景噪点导致画面乱闪
        if class_idx >= 0 and confidence > 0.6:
            name = net.GetClassDesc(class_idx)
            # 逻辑：除 trash 以外均判定为可回收
            if name in ['cardboard', 'glass', 'metal', 'paper', 'plastic']:
                current_result = {"name": name.upper(), "recyclable": "♻️ 可回收", "color": "green"}
            else:
                current_result = {"name": name.upper(), "recyclable": "❌ 不可回收", "color": "red"}
        else:
            current_result = {"name": "正在扫描...", "recyclable": "等待中", "color": "gray"}
        
        # 将画面转为 JPEG 供网页调用
        array = jetson.utils.cudaToNumpy(img)
        array_bgr = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        ret, jpeg = cv2.imencode('.jpg', array_bgr)
        frame = jpeg.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # 挂载在 8080 端口
    app.run(host='0.0.0.0', port=8080)