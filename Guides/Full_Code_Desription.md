# BotChat 🤖💬  
**Multi-window TCP Chat with a Launcher Control Center (NiceGUI + Python Sockets)**

BotChat is a learning-oriented chat system that demonstrates a full client–server workflow using:
- **NiceGUI** for UI (Launcher + Chat windows)
- A custom **TCP server** implemented with Python sockets
- A simple, explicit **line-based protocol** (USERS / MSG / ACK / ERR / RENAME / AVATAR)

The project includes a **Launcher (Control Center)** window that can:
- Start/stop the server
- Spawn multiple chat users (each opens in its own popup window)
- Display active users
- Close all chat windows
- Shutdown the entire system cleanly

---

## Table of Contents 📌
- [Features](#features-)
  - [Launcher (Control Center)](#launcher-control-center-)
  - [Chat Window](#chat-window-)
- [Project Structure](#project-structure-)
- [Architecture Overview](#architecture-overview-)
- [Requirements](#requirements-)
- [Configuration (IP / Ports)](#configuration-ip--ports-)
- [Installation](#installation-)
- [How to Run](#how-to-run-)
  - [Run via Launcher (Recommended)](#1-run-via-launcher-recommended-)
  - [Run Server Manually + UI](#2-run-server-manually--ui-)
  - [Open Pages Manually (No Popup)](#3-open-pages-manually-no-popup-)
- [How to Use the Launcher](#how-to-use-the-launcher-)
- [How to Use the Chat Window](#how-to-use-the-chat-window-)
- [Protocol Reference](#protocol-reference-)
- [Important Notes & Warnings](#important-notes--warnings-)
- [Troubleshooting](#troubleshooting-)
- [Known Limitations](#known-limitations-)

---

## Features ✨
### Launcher (Control Center) 🚀
- ✅ Server ON/OFF toggle with real-time status icon (cloud on/off)
    - Start server as a subprocess (local execution)
    - Stop server gracefully; fallback kill by port (macOS `lsof`)
- ✅ Spawn multiple users (each in a dedicated popup chat window)
- ✅ Display active users (live refreshed dialog)
- ✅ Close all chat windows via BroadcastChannel
- ✅ Full system shutdown: close chats → stop server → close launcher

### Chat Window 💬
- ✅ Global messages (“Everyone”)
- ✅ Direct messages (private to a selected user)
- ✅ Username change with:
  - client-side validation
  - server-side validation
  - server ACK synchronization
  - rollback timer (revert typed name if not confirmed)
- ✅ Avatar selection:
  - DiceBear-based avatars (seed-based)
  - optional background color selection (seed → bg cache)
  - server broadcast so all clients sync the avatar
- ✅ Scroll-aware unread counter:
  - “scroll to bottom” floating button
  - badge indicating unseen messages when user is scrolled up
- ✅ Clean disconnect handshake:
  - sends `CMD:QUIT`
  - waits briefly for server-side close
  - reduces “ghost users”

---

## Project Structure 📁
Core files (based on your code):
- [`Run_App.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/Run_App.py) – starts NiceGUI server and opens the Launcher in Chrome app-mode
- [`UI_Router.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/UI_Router.py) – routes `/` to Launcher and `mode=chat` to Chat
- [`Launcher_UI.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/Launcher_UI.py) – server toggle, create users, active users dialog, shutdown logic
- [`Chat_UI.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/Chat_UI.py) – chat messages, sending, DM, rename, avatar sync, scrolling behavior
- [`Main_Server.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/Main_Server.py) – TCP server (protocol handling, broadcast, private messages)
- [`Common_Setups.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/Common_Setups.py) – configuration (SERVER_IP, ports, Chrome path)
- [`State_Globals.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/State_Globals.py) – UI state (messages, active users, avatars)

---

## Architecture Overview 🧠
BotChat consists of three layers:

### 🌐 UI Layer (NiceGUI)
- **Launcher UI:** [`BotChat/Launcher_UI.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/Launcher_UI.py)
- **Chat UI:** [`BotChat/Chat_UI.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/Chat_UI.py)
- Routing controlled by:
  - **File:** [`BotChat/UI_Router.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/UI_Router.py)
  - `/` → launcher  
  - `/?mode=chat&nickname=<name>` → chat window

### 🖥️ TCP Server Layer (Sockets)
- **File:** [`BotChat/Main_Server.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/Main_Server.py)
- Listens on: `HOST=0.0.0.0`, `PORT=<SERVER_PORT>`
- Accepts multiple clients.
- Each client handled in a dedicated thread.
- Maintains:
  - `online_users: Dict[nickname -> socket]`
  - `online_users_lock` for concurrency
  - routing of global/direct messages
  - rename requests (ACK/ERR)
  - avatar broadcasts
 
### 🗂️ Shared State (In-Process)
The UI (launcher + chat windows in the same NiceGUI process) share Python globals:
- **File:** [`BotChat/State_Globals.py`](https://github.com/Alon-V/Bot-Chat/blob/main/BotChat/State_Globals.py)
- Stores:
  - `messages`: chat history entries
  - `active_users_list`: server-synced online names
  - `avatar_urls`: synced avatar URL map
  - `avatar_seeds`: stable avatar identity across renames
  - `user_colors_cache`: stable bg color per avatar seed

---

## Project Structure 📁
Core files (based on your code):
- `Run_App.py` – starts NiceGUI server and opens the Launcher in Chrome app-mode
- `UI_Router.py` – routes `/` to Launcher and `mode=chat` to Chat
- `Launcher_UI.py` – server toggle, create users, active users dialog, shutdown logic
- `Chat_UI.py` – chat messages, sending, DM, rename, avatar sync, scrolling behavior
- `Main_Server.py` – TCP server (protocol handling, broadcast, private messages)
- `Common_Setups.py` – configuration (SERVER_IP, ports, Chrome path)
- `State_Globals.py` – UI state (messages, active users, avatars)

---

## Requirements ✅
- Python 3.10+ recommended
- Packages:
  - `nicegui`
  - `fastapi` (used by NiceGUI routing)

> If you have a `requirements.txt`, install from it. Otherwise, use the commands below.

---

## Configuration (IP / Ports) 🌐
All configuration is located in:

`BotChat/Common_Setups.py`

```py
SERVER_IP = '10.0.0.16'
SERVER_PORT = 8081
CHAT_UI_PORT = 8080
