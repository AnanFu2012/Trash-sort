# Trash-sort AI 🗑️

Hey there! This is a small AI side project I put together to recognize and sort garbage in real-time. It runs on a Jetson Orin and uses a standard USB webcam. It's nothing crazy, but it does a pretty good job at telling you if an item goes in the recycling bin or not.

## What you need
* A NVIDIA Jetson (I'm using the Orin)
* A standard USB webcam
* The [jetson-inference](https://github.com/dusty-nv/jetson-inference) Docker container setup on your board

## How to run it

**1. Start the Docker container**
You need to mount this project folder into your docker container so it can access the model and code. Run this in your Jetson's terminal:

```bash
cd ~/jetson-inference
./docker/run.sh --volume /path/to/your/Trash-sort:/Trash-sort
(Note: Change /path/to/your/Trash-sort to wherever you cloned this repository!)

2. Run the Web UI
Once you are inside the container (your terminal prompt will change), navigate to the folder and start the Python server:

Bash
cd /Trash-sort
python3 web_ui.py
3. See it in action
Open a web browser on your computer (make sure you are connected to the same local network as the Jetson) and go to:

Plaintext
http://<your-jetson-IP>:8080
Just hold an item in front of the camera, and the UI will update in real-time. Feel free to mess around with the code or swap out the model. Have fun!
