# Trash-sort AI 🗑️😍🤯

Hey there! This is a small AI side project I put together to recognize and sort garbage in real-time. It runs on a Jetson Orin and uses a standard USB webcam. It's nothing crazy, but it does a pretty good job at telling you if an item goes in the recycling bin or not.

### 🌟 Key Features
* Real-time AI Vision: Processes the live webcam feed on the fly using the Jetson's GPU.
* Web-based UI: View the live camera stream and AI predictions straight from any web browser on your local network.
* Lightweight & Fast: Uses an optimized ONNX model so it runs super smoothly without lagging.
* Clean Setup: Everything runs contained inside a Docker environment, keeping your board's main system completely clean.
  

### 🔍 What can it recognize?
Currently, the AI is trained to classify the following categories:
* **Cardboard** (Boxes, shipping packaging)
* **Glass** (Bottles, jars)
* **Metal** (Soda cans, tin cans)
* **Paper** (Newspapers, office paper)
* **Plastic** (Water bottles, food containers)
* **General Trash** (Items that don't belong in the recycling bin)
  
<p align="center">
  <img width="45%" alt="image1" src="https://github.com/user-attachments/assets/8e520b32-bffa-48ab-9987-18ec8dc09d33" />
  <img width="45%" alt="image2" src="https://github.com/user-attachments/assets/58f8730f-d941-4ed7-a23e-5b01f8e03097" />
</p>



### What you need
* A NVIDIA Jetson (I'm using the Orin)
* A standard USB webcam
* The [jetson-inference](https://github.com/dusty-nv/jetson-inference) Docker container setup on your board

## How to run it

### video tutorial: https://drive.google.com/file/d/14HE-HPBqi9pHs0TZfO-yHrvXtmTn2sHK/view?usp=sharing

**1. Start the Docker container**

You need to mount this project folder into your docker container so it can access the model and code. Run this in your Jetson's terminal:
```bash
cd ~/jetson-inference
./docker/run.sh --volume ~/Trash-sort:/Trash-sort
```
(Note: If you cloned the repository somewhere else, change ~/Trash-sort to your actual folder path!)

2. Run the Web UI
Once you are inside the container (your terminal prompt will change), navigate to the folder and start the Python server:
```bash
cd /Trash-sort
python3 web_ui.py
```
3. See it in action
Open a web browser on your computer (make sure you are connected to the same local network as the Jetson) and go to:
```bash
http://<your-jetson-IP>:8080
```
Just hold an item in front of the camera, and the UI will update in real-time. Feel free to mess around with the code or swap out the model. Have fun!
