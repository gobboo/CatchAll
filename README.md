# CatchAll


#### Description
CatchAll is a system designed for Raspberry-Pis along with an external Server ( Preferrably with a GPU ) too be a handsfree doorbell. This system is designed to detect faces using a Camera & OpenCV to alert the owner of someone being at there door.

If somebody is coming closer to your door, the system detects them at a certain distance, now if they stand there for x amount of seconds then the user will be alerted on their phone about who is at the door, if applicable.

This system also has a built in dashboard which you can setup by connecting to the Hotspot the system creates in which you will specify certain parameters then finally allow it to connect to your home network which you will then connect to by typing in the device name along with http:// before hand to open the dashboard, login, view stats, see a life feed, update the system and more.

#### Installation

To begin with first clone this repository:
` git clone https://github.com/mobles/catchall.git`

Next go into the client and first create a virtual environment to work from:
`virtualenv .env && source .env/bin/activate && pip install -r requirements.txt`

This will also install the requirements for you automatically.

Then you'll want to do the same for the server folder.

Once done, first launch the server using
`python main.py`
This server will do all the facial recognition and will store known faces when a user uploads them, it will also cache them so that on startup it doesn't have to analyze all the faces everytime in launches.

Next head into the client folder again and launch the client:
`python main.py runserver --host 0.0.0.0 --port 80`

This will launch the client on the raspberry pi with the specified IP ( 0.0.0.0 being IPV4 ) and with port 80.


AUTO INSTALLER WILL BE COMING SOON

This project is no where close to finished and is still being worked on for a project in college.
