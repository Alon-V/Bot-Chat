> **Academic Project Notice**  
> This project was developed as part of an academic assignment focusing on TCP/IP protocols, encapsulation, real network traffic, Client–server architecture, and protocol design.

# About Botchat 🤖

## Part 1: 📦
A practical implementation of TCP/IP communication by manually constructing, sending, capturing, and analyzing network packets.
In the goal of an in-depth understanding of the encapsulation process across the TCP/IP layers, while observing and analyzing real network traffic using Wireshark.

## Part 2: 💬
A real-time chat application built with Python, Raw TCP Sockets, and NiceGUI.
Botchat is a full Client-Server architecture using pure Python socket libraries for networking wrapped in a responsive web-based interface.

## Shortcats: 🛣️
--> **In case you want to first look at part 1:** 

- For the Whole `"Part One"` folder [click here](/PartOne)
- For the "TCP/IP Packet Encapsulation and Capture" [click here](/PartOne/WireSharkLog.md) 

--> **In case you want to first look at part 2:** 

- For the Whole `"Part Two"` folder [click here](/PartTwo)
- For the "TCP/IP Client-Server Chat Packet Capture" [click here](/PartTwo/Wireshark_LOGs.md) 

--> **In case you want to skip to the LAN setup** [click here](https://github.com/Alon-V/Bot-Chat?tab=readme-ov-file#how-to-run-chatbot-on-local-lan-multiple-computers-)

---
## * This next section is a short guide for Part Two of the project ->  
---

## Table of Contents 📌

- [Key Features](#key-features-)
- [Project Structure](#project-structure-)
- [How to Run](#how-to-run-)
- [How to Use the App](#how-to-use-the-app-%E2%80%8D)
  - [Running the Chat and Server](#running-the-chat-and-server)
  - [Adding a User](#adding-a-user)
- [How to Run Chatbot on Local LAN (Multiple Computers)](#how-to-run-chatbot-on-local-lan-multiple-computers-)
- [Use of AI Tools (Disclosure)](#use-of-ai-tools-disclosure-)
  - [Purpose of Use](#purpose-of-use)
  - [Example Prompts](#example-prompts)

---

## Key Features ✨
- **Pure TCP Networking:** Built entirely on Python's standard socket library (no high-level wrappers like Socket.IO). (Sadly this was asked for in the project requirements 😉)
- **Real-Time Communication:** Instant messaging with support for Global Chat and Private Messaging.
- **Multi-User Support:** Handles multiple concurrent connections.
- **Dynamic UI:** Modern interface (NiceGUI was very time-saving and helpful) with auto-scrolling, message bubbles, and notifications.
- **Launcher:** Functions as a control center and an observer.

---

## Project Structure 🧌
| File | Short summary |
| --- | --- |
| [Main_Server](/PartTwo/BotChat/Main_Server.py) | The TCP Server logic (Connection handling, Broadcasting) |
| [Chat_UI](/PartTwo/BotChat/Chat_UI.py) | The Chat Window interface (NiceGUI + Client Socket) |
| [Launcher_UI](/PartTwo/BotChat/Launcher_UI.py) | The Dashboard/Login screen (Server toggle, User list) |
| [Common_Setups](/PartTwo/BotChat/Common_Setups.py) | Configuration file (IP, PORT, Constants) |
| [Run_App](/PartTwo/BotChat/Run_App.py) | Main entry point to start the application |
| [UI_Router](/PartTwo/BotChat/UI_Router.py) | Routes traffic between Launcher and Chat modes |
| [State_Globals](/PartTwo/BotChat/State_Globals.py) | Shared state variables (Message history, Active users) |

*If you want to know a bit more about the code itself -> [Short_Code_Description](/Guides/Short_Code_Description.md) , [Full_Code_Description](/Guides/Full_Code_Description.md)

---

## How to Run 🏃

First of all, you need:
- Python 3.10+
- NiceGUI

### Easy (and "special") way to run it:

Copy all the code in the project one by one into an open project you have. Make sure each file from this repo is copied into a separate file in that project.

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

## How to Use the App 👨‍💻

### Running the chat and server
There are 2 ways to start the server:
1) Run the `Main_Server` file and then start the app from the `Run_App` file.
2) In the app launcher (that opens after running the `Run_App` file), there is a toggle with an indicator in the upper left corner, switch it on, and that’s it.
    - *This button might not work if you try to use the chat on a LAN network.
      In that case use method number (1).

### Adding a user

This launcher is what you should see after running `Run_App`:
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
- Under [Full_Code_Description](/Guides/Full_Code_Description.md) look for: `How to Use the Launcher` or `How to Use the Chat Window`

---

## How to run chatbot on local LAN (Multiple Computers) 🌐

1. Find your IPv4 Address (see guide for further explanation- [How to Find your IP](/Guides/How_to_find_your_IPv4_Address.md))
2. Open [Common_Setups](/BotChat/Common_Setups.py).
3. Update the SERVER_IP variable:
`SERVER_IP = '*.*.*.*'  # Replace with YOUR local IP`
4. Ensure that inbound traffic on `SERVER_PORT` is allowed by the Windows system Firewall.
   (Temporarily disabling the firewall may help during testing, but is not recommended for production environments.)

---

## Use of AI Tools (Disclosure) 📠

This project made limited use of AI-based tools as a productivity aid during development and documentation.

### Purpose of Use
AI tools were used for:
- Improving code readability and structure (exp. notes, structure)
- Refining documentation wording and technical explanations (exp. readme's)
- Verifying design decisions and edge cases during development (exp. "where can we fall?")

No code was generated from start to finish by AI, and all architectural decisions, implementation, and debugging were performed by us.

### Example Prompts
Examples of prompts used during development include:
- *"Review this TCP client–server design and suggest potential edge cases."*
- *"Help refine this README section to be clearer for an academic evaluator."*
- *"Explain possible failure scenarios in a socket-based rename handshake."*
