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
## To Run Server
```bash
cd server
npm i
npm run start
```