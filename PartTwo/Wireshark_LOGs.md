# Computer Networks Project Report- Part 2 🌐
## TCP/IP Client-Server Chat Packet Capture

## Welcome to our network traffic (Wireshark) tour 🦈
In this section, we examine the Client-Server Chat network traffic captured using Wireshark and explain how different types of TCP connections are used throughout the system.

---

## Table of Contents 📌
- [TCP Handshake Scenarios](#tcp-handshake-scenarios-)
  - [Launcher-Observer Connection](#1-launcher-observer-connection------)
  - [Launcher Server Availability Check](#2-launcher-server-availability-check-----)
  - [A "New User" Connection](#3-a-new-user-connection----)
- [Sending a Message](#sending-a-massage-)
- [Receiving a Message](#reciving-a-massage-)

---

## TCP Handshake Scenarios 🤝
Below are the three main types of TCP handshakes observed in the application.

---

## 1. Launcher-Observer Connection  [ 🚀 → 👀 ]
The *"Observer"* is a hidden TCP connection to the server initiated by the Launcher and kept open continuously.
The Observer connection serves as a persistent monitoring channel, allowing the Launcher to remain synchronized with the server state independently of active chat users.

Its purpose is:
- **Live User Monitoring:** Receives real-time updates about connected users (joins and disconnects).
- **Global Control Operations:** Enables system-wide actions such as: "Show Active Users", "Close All Chats" and "Shutdown System".
- **Architectural Separation:** Maintains a clear distinction: `Data Plane → Chat Messages` -|- `Control Plane → Observer + Launcher`.

### This handshake consists of:

**`[SYN]` :** A connection request.

  ⤵️
  
**`[ACK]` :** A server acknowledgment (a yes/no answer to the request).

Once established, the connection remains open (otherwise nothing happens).

An easy way to identify this connection in Wireshark is by inspecting the packet length:  
it does not exceed **25 bytes**, since the message sent during the handshake is the identifier: __LAUNCHER__.

---

## 2. Launcher Server Availability Check [ 🚀 → 📡 ]
The Launcher periodically establishes a short-lived TCP connection to verify whether the server is online.  
Once the status is confirmed, the connection is immediately closed.

Its purpose is:
- **Health Check:** Performs a real TCP-level availability check, independent of UI state or local process assumptions.
- **External Verification:** Detects servers started manually or running on other machines within the LAN.
- **UI Synchronization:** Aligns UI state (online/offline indicators, controls) with the actual server status.
- **Fault Awareness:** Identifies crashes or unexpected server termination.
- **Lightweight Design:** Short-lived connection; not part of the messaging protocol and minimal resource usage.


### This handshake consists of:

**`[SYN]` :** A connection request.

  ⤵️
  
**`[ACK]` :** A server acknowledgment (a yes/no answer to the request). 

Indicating whether the connection request was accepted (otherwise nothing happens).

  ⤵️
  
**`[FIN]` :** Connection termination.

<br>

<div align="center">
<img width="1215" height="496" alt="image" src="https://github.com/user-attachments/assets/d0db2a95-8838-496c-b7ba-3f81365dc77a" />
  </div>

---

## 3. A "New User" Connection [ 🆕 👤 ]
When a new user joins the chat, a dedicated TCP connection is established between the client and the server using a standard **three-way handshake**, as introduced and discussed in the course.

### This handshake consists of:

**`[SYN]` :**  
A connection request sent by the client to initiate the session.

  ⤵️

**`[SYN, ACK]` :**  
The server acknowledges the request and agrees to establish the connection (otherwise nothing happens).

  ⤵️

**`[ACK]` :**  
The client confirms the acknowledgment, completing the connection setup.

  ⏩

❗️ *Immediately after the handshake is completed, the client sends its **username** as the first application-level payload.* --> **`[PSH, ACK]`** 

<br>

Below is the handshake sequence used to create a new user, followed by the packet containing the username ("Vin"):

<div align="center">
<img width="1347" height="968" alt="image" src="https://github.com/user-attachments/assets/d18695de-c055-4293-864e-80e3e99c80cd" />
  </div>

<br>

<div align="center">
<img width="1107" height="668" alt="image" src="https://github.com/user-attachments/assets/8def7304-51b1-4f84-817e-87307202e186" />
  </div>

<br>

The difference between the source and destination IP addresses indicates that the user was created on a different machine than the one hosting the server.

Additionally, the capture shows the randomized port assigned to the client when sending a request to the server(**59772**), which listens on port **8081**.

---

## Sending a massage 📟
First- let's send a message:

<div align="center">
<img width="648" height="396" alt="Screenshot 2026-01-24 at 12 41 11" src="https://github.com/user-attachments/assets/666b1a17-a868-419f-9fd7-6dfbe780c3e5" />
</div>

<br>

When a user sends a message, the traffic appears as follows:

<div align="center">
<img width="1049" height="17" alt="image" src="https://github.com/user-attachments/assets/e0005833-ace6-4880-9397-f55beced01ae" />
  </div>

<br>

In this example:
- Source IP: `10.0.0.15` (client)
- Destination IP: `10.0.0.16` (server) {*It is always the server's location}
- The packet includes both the client’s ephemeral port (**59772**) and the server’s listening port (**8081**)

<br>

The message payload itself can be observed here ("I am a mistborn"):

<div align="center">
<img width="552" height="116" alt="image" src="https://github.com/user-attachments/assets/ce3a154c-d6c6-4ab1-94ad-2bc8d4ecc186" />
</div>

---

## Reciving a massage 📬
Now let's see what happens when we recive the massage:

<div align="center">
<img width="648" height="397" alt="Screenshot 2026-01-24 at 12 41 28" src="https://github.com/user-attachments/assets/1e9bfebc-4208-4e8c-b54d-d9603ffceb1e" />
</div>

<br>

Since this message is a **broadcast**, the server forwards it to all connected users.  
This is visible in Wireshark by observing multiple outgoing packets from the server, each with a different destination port.

<br>

<div align="center">
<img width="1072" height="49" alt="image" src="https://github.com/user-attachments/assets/c7e77c29-5ee5-4e25-8e6b-2d70261104ae" />
</div>

<br>

As we can see the message that was sent for one client ('Client 1') went through the server and sent to all of the other clients that were connected.

- ***Server -> Client 2 :*** `8081 → 61157` , `10.0.0.16 → 10.0.0.15`
- ***Server -> Client 3 :*** `8081 → 61204` , `10.0.0.16 → 10.0.0.15`
- ***Server -> Client 4 :*** `8081 → 59772` , `10.0.0.16 → 10.0.0.15`
- **All the clients were on the same machine, that does'nt have to be the case.*

<br>

<div align="center">
<img width="552" height="116" alt="Screenshot 2026-01-24 at 12 32 38" src="https://github.com/user-attachments/assets/b9056119-5d76-4639-b851-346569696a8c" />
</div>

<br>

We can see that the payload is the message we sent ("I am a mistborn") from Client 1 ("Vin") as a broadcast to everyone ("ALL"). 

**In case its a private massage then he sends this only to one user.*



