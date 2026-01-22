# About Botchat 🤖

A real time chat application built with Python, Raw TCP Sockets, and NiceGUI.
Botchat is a full Client Server architecture using pure Python socket libraries for networking wrapped in a responsive web-based interface.

--> [In case you want to first look at part 1- "TCP/IP Packet Encapsulation and Capture" click here](/PartOne/WireSharkLog.md)


--> [In case you want to skip to LAN setup](https://github.com/Alon-V/Bot-Chat?tab=readme-ov-file#how-to-run-chatbot-on-local-lan-multiple-computers-)

---

## Key Features ✨
- **Pure TCP Networking:** Built entirely on Python's standard socket library (no high level wrappers like Socket.IO). (Saddly this was asked for in the project reqirments)
- **Real-Time Communication:** Instant messaging with support for Global Chat and Private Messaging.
- **Multi-User Support:** Handles multiple concurrent connections.
- **Dynamic UI:** Modern interface (NiceGUI was very time saving and helpfull) with auto-scrolling, message bubbles, and notifications.
- **Launcher:** Fuctions as a control center and an observer.

---

## Project Structure 🧌
| File | Short summery |
| --- | --- |
| [Main_Server](/BotChat/Main_Server.py) | The TCP Server logic (Connection handling, Broadcasting) |
| [Chat_UI](/BotChat/Chat_UI.py) | The Chat Window interface (NiceGUI + Client Socket) |
| [Launcher_UI](/BotChat/Launcher_UI.py) | The Dashboard/Login screen (Server toggle, User list) |
| [Common_Setups](/BotChat/Common_Setups.py) | Configuration file (IP, PORT, Constants) |
| [Run_App](/BotChat/Run_App.py) | Main entry point to start the application |
| [UI_Router](/BotChat/UI_Router.py) | Routes traffic between Launcher and Chat modes |
| [State_Globals](/BotChat/State_Globals.py) | Shared state variables (Message history, Active users) |

*If you want to know a bit more about the code itself -> [Short_Code_Description](/Guides/Short_Code_Description.md) , [Full_Code_Description](/Guides/Full_Code_Description.md)

---

## How to Run 🏃

First of all, you need:
- Python 3.10+
- NiceGUI

### Easy (and "special") way to run it:

Copy all the code in the project one by one to a open project you have make sure each code is in a diffrent file in that project

### The normal way:
1. Clone the repository: 

```py
git clone https://github.com/yourusername/python-lan-chat.git
cd python-lan-chat
```

2. Install dependencies:

```py
pip install nicegui
```

3. Run the Application:

```py
python Run_App.py
```

---

## How to Use the app 👨‍💻

### Running the chat and server
There are 2 ways to open the server:
1) Run the `Main_Server` file and then start the app from the `Run_App` file.
2) In the app luncher (that opens after running the run_app file), there is a toggle with an indicator in the upper left corner, switch it on, and thats it.
    - *This button might not work if you try to use the chat in a lan network. In that case use method noumber (1).

### Adding a user

This luncher is what you should see after running `Run_App`:
<div align="center">
  <img width="300" height="400" alt="image" src="https://github.com/user-attachments/assets/838ae443-56ed-4c18-802f-b3d895017376" />
</div>

1) **Create a User:**

   Enter a nickname in the Launcher to open a new chat window. Press 'Enter' or "LAUNCH CHAT".

   That’s it — a new chat user is created and opened in its own window.
   
<div align="center">
<img width="227" height="163" alt="Screenshot 2026-01-22 at 20 31 09" src="https://github.com/user-attachments/assets/9434e868-11da-4ddf-8e2d-463508edfbf7" />
</div>

2) **Edit User Details:**

   You can change your username by clicking the name field at the bottom-left of the chat window.
 
   You can also change your avatar by clicking the avatar image on the top-left.

<div align="center">
<img width="572" height="368" alt="Screenshot 2026-01-22 at 20 25 44" src="https://github.com/user-attachments/assets/46907f27-5769-4e05-ba24-66f2e1aa7277" />
</div>

3) **Launcher Management:**

   The Launcher allows you to view connected users, close all chat windows simultaneously and even shutdown the whole system.

<div align="center">
<img width="300" height="400" alt="image" src="https://github.com/user-attachments/assets/0568f2e2-f45f-4ef2-b044-76658ed0cf65" />
</div>

*For further explanations you can see ->

- [How to Use the Launcher](https://github.com/Alon-V/Bot-Chat/blob/main/Guides/Full_Code_Description.md#how-to-use-the-launcher-)
- [How to Use the Chat Window](https://github.com/Alon-V/Bot-Chat/blob/main/Guides/Full_Code_Description.md#how-to-use-the-chat-window-)

---

## How to run chatbot on local LAN (Multiple Computers) 🌐

1. Find your IPv4 Address (see guide for further explanation- [How to Find your IP](/Guides/How_to_find_your_IPv4_Address.md))
2. Open [Common_Setups](/BotChat/Common_Setups.py).
3. Update the SERVER_IP variable:
`SERVER_IP = '*.*.*.*'  # Replace with YOUR local IP`
4. Ensure your Windows Firewall allows inbound traffic on the port defined in SERVER_PORT if it does not work just disable the firewall
