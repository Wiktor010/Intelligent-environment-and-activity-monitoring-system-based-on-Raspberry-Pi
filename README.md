# Intelligent-environment-and-activity-monitoring-system-based-on-Raspberry-Pi
A project created for the needs of the subject of advanced use of microprocessors. The project uses the `pimoroni-bme280` and `adafruit-circuitpython-bh1750` libraries to communicate with the sensors.
## Prerequisites

- **Hardware**: A Raspberry Pi with connected sensors.
- **Software**: Python 3.7 or higher is recommended.

## Setup and Installation

### 1. Clone the Repository

First, clone this repository to your local machine.

```bash
git clone git@github.com:Wiktor010/Intelligent-environment-and-activity-monitoring-system-based-on-Raspberry-Pi.git
```
### 2. Navigate to the Project Directory
Change to the directory where the project was cloned:
```bash
cd Intelligent-environment-and-activity-monitoring-system-based-on-Raspberry-Pi
```

### 3. Create a Virtual Environment

Create a virtual environment to isolate the project dependencies:
```bash
python3 -m venv env
```
### 4. Activate the Virtual Environment

Activate the virtual environment with the following command:
- On Linux or macOS:
```bash
source env/bin/activate
```
- On Windows:
```bash
.\env\Scripts\activate
```

### 5. Install the Required Libraries
Install the necessary dependencies using requirements.txt:
```bash
env/bin/pip3 install -r requirements.txt
```

## Additional Notes
If you add new dependencies, remember to update requirements.txt by running:
```bash
pip freeze > requirements.txt
```
