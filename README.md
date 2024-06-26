#  Pi-Speed-Cam
Pi-Speed-Cam is a Raspberry Pi based Dash-Cam IoT device that uses Machine Learning to enforce speed limits on roads. It scans the front of the vehicle for speed signs, and creates a report if the vehicle is moving faster than the indicated speed limit.
## To Run Raspberry Pi Client
```bash
cd raspberry
pip install virtualenv
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```
If you install any new libraries while developing, dont forget to run the below before committing:
```bash
pip freeze > requirements.txt
```
To deactivate the virtual environment, run:
```bash
deactivate
```

##  To Run Server
- Train the Model
```bash
cd  server
pip install  kaggle
kaggle datasets  download  -d  andrewmvd/road-sign-detection
python ./src/preprocessing.py

git clone  https://github.com/ultralytics/yolov5
cd  yolov5
python -m venv venv
./venv/Scripts/activate

(venv) pip install  -r  requirements.txt
(venv) pip uninstall  torch  torchvision  -y
(venv) pip install  torch  torchvision  --index-url  https://download.pytorch.org/whl/cu121

(venv) python train.py --img 320  --batch 16  --epochs 50  --data VOC.yaml --weights yolov5s.pt --workers 2
```
- Run the receiver worker
```bash
cd server
python -m venv venv
./venv/Scripts/activate
(venv) pip install -r requirements.txt
(venv) python receive.py
```