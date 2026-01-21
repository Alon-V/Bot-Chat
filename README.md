# About Botchat 🤖

A real time chat application built with Python, Raw TCP Sockets, and NiceGUI
Botchat is a full Client Server architecture using pure Python socket libraries for networking wrapped in a responsive web-based interface.

## Key Features ✨
- Pure TCP Networking: Built entirely on Python's standard socket library (no high level wrappers like Socket.IO). (Saddly this was asked for in the project reqirments)
- Real-Time Communication: Instant messaging with support for Global Chat and Private Messaging.
- Multi-User Support: Handles multiple concurrent connections.
- Dynamic UI: Modern interface (NiceGUI was very time saving and helpfull) with auto-scrolling, message bubbles, and notifications.
- Launcher: Fuctions as a control center and an observer.

## Project Structure 🧌
|--Main_Server.py      # The TCP Server logic (Connection handling, Broadcasting)
|--Chat_UI.py          # The Chat Window interface (NiceGUI + Client Socket)
|--Launcher_UI.py      # The Dashboard/Login screen (Server toggle, User list)
|--Common_Setups.py    # Configuration file (IP, PORT, Constants)
|--Run_App.py          # Main entry point to start the application
|--UI_Router.py        # Routes traffic between Launcher and Chat modes
|--State_Globals.py    # Shared state variables (Message history, Active users)
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
###Running the chat and server

To be contiued 

