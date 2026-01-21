# About Botchat 🤖

A real time chat application built with Python, Raw TCP Sockets, and NiceGUI
Botchat is a full Client Server architecture using pure Python socket libraries for networking wrapped in a responsive web-based interface.
[In case you want to look at part 1 first click here](/PartOne/WireSharkLog.md)


## Key Features ✨
- Pure TCP Networking: Built entirely on Python's standard socket library (no high level wrappers like Socket.IO). (Saddly this was asked for in the project reqirments)
- Real-Time Communication: Instant messaging with support for Global Chat and Private Messaging.
- Multi-User Support: Handles multiple concurrent connections.
- Dynamic UI: Modern interface (NiceGUI was very time saving and helpfull) with auto-scrolling, message bubbles, and notifications.
- Launcher: Fuctions as a control center and an observer.


## Project Structure 🧌
| File | Short summery |
| --- | --- |
| Main_Server.py | The TCP Server logic (Connection handling, Broadcasting) |
| Chat_UI.py | The Chat Window interface (NiceGUI + Client Socket) |
| Launcher_UI.py | The Dashboard/Login screen (Server toggle, User list) |
| Common_Setups.py | Configuration file (IP, PORT, Constants) |
| Run_App.py | Main entry point to start the application |
| UI_Router.py | Routes traffic between Launcher and Chat modes |
| State_Globals.py | Shared state variables (Message history, Active users) |

If you want to know a bit more about the code itself

## How to Run 🏃
You need
- Python 3.8+
- NiceGUI

### easy (and "special") way to run it:

Copy all the code in the project one by one to a open project you have make sure each code is in a diffrent file in that project

### The normal way:
1. Clone the repository: 

`git clone https://github.com/yourusername/python-lan-chat.git
cd python-lan-chat`

2. Install dependencies:

`pip install nicegui`

3. Run the Application:

`python Run_App.py`

## How to Use the app
### Running the chat and server
There are 2 ways to open the server
- run the server file
- in the app luncher that opens after running the run_app file there is a button in the upper right corner
  *This button might not work if you try to use the chat in a lan network in that case run the server file before run_app.

### Adding a user
This luncher is what you should see after running run_app
<div align="right">
  <img width="200" height="200" alt="image" src="https://github.com/user-attachments/assets/838ae443-56ed-4c18-802f-b3d895017376" />
</div>
Step one Enter a nickname for your user
anddd thats it you have a user
you can change his name by clicking on the name on the butom left and you can do the same with the image

using the Luncher you can see who is coneccted and close the chat for everyone
<div align="right">
<img width="200" height="200" alt="image" src="https://github.com/user-attachments/assets/0568f2e2-f45f-4ef2-b044-76658ed0cf65" />
</div>

## How to run chatbot on local LAN (Multiple Computers) 🌐

1. Find your IPv4 Address (Run ipconfig in CMD).[How to Enter cmd](/Guides/cmd.md)
2. Open Common_Setups.py.
3. Update the SERVER_IP variable:
`SERVER_IP = '*.*.*.*'  # Replace with YOUR local IP`
4. Ensure your Windows Firewall allows inbound traffic on the port defined in SERVER_PORT if it does not work just disable the firewall
