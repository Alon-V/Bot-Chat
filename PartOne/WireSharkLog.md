# Computer Networks Project Report- Part 1 🌐
## TCP/IP Packet Encapsulation and Capture

## Overview 🧭
This project demonstrates a practical implementation of TCP/IP communication by manually constructing, sending, capturing, and analyzing network packets.  
The goal is to gain an in-depth understanding of the encapsulation process across the TCP/IP layers and to observe real network traffic using Wireshark.

The project focuses on the HTTP protocol running over TCP and simulates real traffic on the local loopback interface. Packets are generated programmatically, sent through the network stack, captured in real time, and analyzed to verify correctness and protocol compliance.

---

## Table of Contents 📌

- [Project Goals](#project-goals-)
- [Technologies and Tools](#technologies-and-tools-%EF%B8%8F)
- [Stage 1: CSV File Preparation and Data Source](#stage-1-csv-file-preparation-and-data-source-%EF%B8%8F)
  - [Dataset (CSV Input)](#dataset-csv-input-)
  - [Data Preparation](#data-preparation-)
  - [Main Fields](#main-fields-)
- [Stage 2: Packet Encapsulation Process](#stage-2-packet-encapsulation-process-)
  - [Key Components](#key-components-)
  - [Final Packet Assembly Using the RawTcpTransport Class](#final-packet-assembly-using-the-rawtcptransport-class-%EF%B8%8F)
    - [Initialization](#initialization-__init__)
    - [Packet Encapsulation](#packet-encapsulation-encapsulate)
    - [Packet Transmission](#packet-transmission-send)
  - [Encapsulation Flow](#encapsulation-flow----)
  - [Interface Detection and Preview Demonstration](#interface-detection-and-preview-demonstration-)
- [Operating System Limitations and Solution](#operating-system-limitations-and-solution-%EF%B8%8F)
- [Stage 3: Packet Transmission and Capture](#stage-3-packet-transmission-and-capture-)
  - [Sending Logic](#sending-logic-)
  - [Capturing Logic](#capturing-logic-)
- [Stage 4: Analysis of Captured Traffic](#stage-4-analysis-of-captured-traffic-)
  - [Packet Overview](#packet-overview-)
  - [CSV-Based Packet Re-Transmission](#csv-based-packet-re-transmission-)
- [Scapy Warning During Packet Transmission](#scapy-warning-during-packet-transmission-%EF%B8%8F)
- [Results](#results-)
- [Conclusion](#conclusion-)

---

## Project Goals 🎯
- Demonstrate the TCP/IP encapsulation process in practice  
- Manually construct a CSV file containing application-layer messages.
- Description and analysis of the packet encapsulation process.
- Capture and analyze traffic using Wireshark.  
- Validate analysis and explanation of the network traffic captured using Wireshark, including supporting screenshots. 

---

## Technologies and Tools ⚙️
- **Operating System:** macOS  
- **Programming Language:** Python  
- **Development Environment:** Jupyter Notebook  
- **Network Analysis Tool:** Wireshark  
- **Network Interface:** Loopback (`lo`)  
- **Packet Handling:** Scapy  
- **Data Management:** Pandas (CSV files)

---
## Stage 1: CSV File Preparation and Data Source 🗃️

## Dataset (CSV Input) 📊
The CSV input data is based on real HTTP traffic on our computers for a certain period of time captured on the loopback interface on wireshark.

### Data Preparation 📑
1. Network traffic was captured using Wireshark on the loopback interface.
2. An HTTP filter was applied to isolate relevant packets.
3. Selected fields were exported to a CSV file.
4. Column names were adjusted to match the project’s code requirements.
5. The CSV file was loaded and validated in Jupyter Notebook.

<p align="center">
  <img src="images/csv_table_overview.png" width="800">
</p>

*Figure 1: Overview of the CSV file structure after export from Wireshark.*

### Main Fields: 🧾
- **msg_id** – Unique identifier for each packet
- **No.** Packet sequence number during capture  
- **timestamp** – Capture time relative to session start  
- **Source / Destination** – Source and destination IP addresses
- **app_protocol** - The application protocol used. Represents the layer in the communication model.
- **src_port / dst_port** – Source and destination ports  
- **Length** – Total packet length  
- **TCP payload** – Payload size at the TCP layer
- **iRTT:** Estimated round-trip time  
- **Flags** – TCP flags (SYN, ACK, FIN, PSH)  
- **Request Method** – HTTP method (if applicable)
- **Protocols in frame:** Protocol stack involved in the packet 
- **message** – Payload content  

---

## Stage 2: Packet Encapsulation Process 📦
This stage focuses on mapping captured application-layer messages to the TCP/IP layers through manual packet construction.
(known in the code as "Step 3 – Map to TCP/IP Layers (Encapsulation)")

### Key Components 🔑
- **Checksum calculation**  
  A custom checksum function is implemented to validate IP and TCP headers.

- **Hexdump utility**  
  Displays packet data in hexadecimal and ASCII format for inspection (packet visualization).

- **IP Header Construction**
  Explicit construction of IPv4 headers. 
  Fields include version, tos, total length, identification, flags_fragment, TTL, protocol, checksum, source IP, and destination IP.

- **TCP Header Construction**
  Explicit construction of TCP headers.  
  Fields include source port, destination port, sequence number, acknowledgment number,doff_reserved, flags, window, checksum and urg_ptr.
   
### Final Packet Assembly Using the RawTcpTransport Class 🏗️
At this stage, the final encapsulation of the constructed message is performed.  
The `RawTcpTransport` class is responsible for binding together all previously defined data and functions into a complete network packet.

The class is composed of several core methods, each responsible for a specific stage in the packet construction and transmission process.

#### Initialization (`__init__`)
The constructor initializes and stores the source and destination IP addresses and ports (`src_ip`, `dst_ip`, `src_port`, `dst_port`).  
In addition, an optional network interface parameter (`iface`) is defined, primarily for use in Windows environments.

During initialization, the operating system is detected and a decision is made whether to use Scapy for packet transmission or attempt manual raw socket usage.

#### Packet Encapsulation (`encapsulate`)
The `encapsulate` function is responsible for constructing the complete packet by combining the TCP header, IP header, and application-layer payload.

- The TCP header is built using the source and destination IP addresses, source and destination ports, payload data, and TCP flags.
- The IP header is constructed using the source and destination IP addresses and the total length of the TCP segment plus payload.
- The function returns a binary sequence representing the full packet structure:  
  **IP Header + TCP Header + Payload**

#### Packet Transmission (`send`)
The `send` function handles the actual transmission of the constructed packet.

- On macOS and Linux systems, the packet may be transmitted as a raw binary structure using the `sendto()` function with raw sockets.
- On Windows systems, the packet is constructed and transmitted using Scapy and sent through the dedicated Npcap loopback interface.

As discussed previously, the implementation was modified to enforce Scapy-based transmission across all operating systems to ensure consistent behavior and reliable packet capture.

---
### Encapsulation Flow --> 🌊
1. Application data is prepared as payload.
2. TCP header is constructed using source/destination ports and flags.
3. IP header is constructed using source/destination IP addresses.
4. Final packet is assembled as:  
   **IP Header + TCP Header + Payload**
   into a single binary sequence representing a valid TCP/IP packet.
---

### Interface Detection and Preview Demonstration 🔍
An additional code segment checks whether the execution environment is Windows and whether Scapy is available. If these conditions are met, a list of available network interfaces is printed.

In the final demonstration step, a preview packet is constructed to validate the encapsulation logic.  
The local loopback network (`127.0.0.1`) is used, a random source port is selected, the destination port is set manually to `12345`, and a generic payload message (“Hello Packet (preview)”) is defined.

All parameters are passed into a single packet instance, which is then printed to display the expected structure and verify correct packet assembly.

This process results in the successful encapsulation of the first complete packet:

<p align="center">
  <img src="images/packet_hexdump_preview.png" width="700">
</p>

*Figure 2: Hexdump representation of the preview packet, showing the manually constructed IP header, TCP header, and application-layer payload ("Hello Packet (preview)").*

The hexdump confirms that the packet is correctly structured according to the TCP/IP standard, with properly aligned headers and payload data encoded in ASCII format.

---

## Operating System Limitations and Solution ⚠️ 
On macOS (and in many cases Windows), sending raw TCP/IP packets using raw sockets is restricted by the operating system.  
As a result, packets may be silently dropped and not appear in Wireshark captures.

### Solution
To ensure consistent behavior across operating systems:
- All packet sending is forced through **Scapy** instead of relying on raw sockets.
- Scapy uses system-supported mechanisms to inject packets
- This allows Wireshark to reliably capture traffic on macOS

A known Scapy warning regarding the `iface` parameter is expected and does not indicate an error.

<p align="center">
  <img src="images/FallBack_Change.png" width="600">
</p>

*Figure 3: Forcing Scapy-based packet transmission to ensure cross-platform compatibility and reliable packet capture.*

---

## Stage 3: Packet Transmission and Capture 📡
Following the packet encapsulation process, the next stage involves transmitting the constructed packets and capturing them in real time.

Wireshark is launched and configured to capture traffic on the loopback interface (`lo`).  
While packet transmission is executed, the captured packets can be observed running in the background, simulating controlled network traffic.

### Sending Logic 📤
A communication object is created by defining the local loopback network (`127.0.0.1`), selecting a random source port, manually setting the destination port to `12345`, and configuring the network interface according to the operating system requirements (including the Npcap virtual adapter on Windows).  
All parameters are passed to a `RawTcpTransport` instance, which encapsulates the complete connection configuration.

### Capturing Logic 📥
To demonstrate packet transmission, the `demo_send()` function is used to send three packets in a controlled manner.  
For each transmission, a textual payload (“Hello Packet”) is generated, the `send()` function constructs the IP, TCP, and payload layers, and the packet is transmitted with fixed time intervals between transmissions.

In a subsequent step, the function is invoked with TCP flags set to `0x18` (PSH + ACK) using `demo_send(flags=0x18)`.

The transmitted packets are then captured and inspected in Wireshark.  
Packet identification is performed using the following capture filter:
```py
"tcp.port==12345".
```

---

## Stage 4: Analysis of Captured Traffic 🔎
    
<p align="left">
  <img src="images/wireshark_capture_overview1.png" width="600">
</p>
<p align="left">
  <img src="images/wireshark_capture_overview2.png" width="600">
</p>
<p align="left">
  <img src="images/wireshark_capture_overview3.png" width="600">
</p>
<p align="left">
  <img src="images/wireshark_capture_overview4.png" width="600">
</p>

*Figure 4: Wireshark capture overview showing TCP packets exchanged over the loopback interface using destination port 12345.*

<br>

### Packet Overview 💾
The captured traffic consists of multiple TCP packets matching the predefined criteria:
- Source and destination IP: `127.0.0.1`
- Random source ports (29200)
- Destination port: `12345`
- TCP flags: PSH + ACK (0x18)
- One sec timeout between sends
- Payload: “Hello Packet”

<br>

### CSV-Based Packet Re-Transmission 🔁
All messages from the original CSV file were re-encapsulated and transmitted again using the same TCP/IP structure.  
Wireshark successfully captured all transmitted packets, confirming the correctness of the encapsulation and transmission process.

<p align="center">
  <img src="images/wireshark_csv_retransmission.png" width="900">
</p>

*Figure 5: Wireshark capture showing the re-transmission of all CSV-based messages as individually encapsulated TCP packets.*

---

## Scapy Warning During Packet Transmission ⚠️

During the execution of the `demo_send()` function and the subsequent re-transmission of messages from the CSV file, a warning message generated by Scapy is displayed.

<p align="center">
  <img src="images/scapy_iface_warning.png" width="900">
</p>

*Figure 6: Scapy SyntaxWarning indicating that the `iface` parameter has no effect when using L3 packet transmission.*

This message represents a `SyntaxWarning` and does **not** indicate a runtime error or a failure in packet transmission.  
The warning originates from Scapy’s `send()` function, which operates at Layer 3 (IP level). At this layer, the `iface` parameter typically has no effect, as Scapy automatically selects the appropriate network interface.

In the context of this project, Scapy autonomously chooses the loopback interface for packet transmission.  
The warning is therefore expected behavior and does not impact the correctness of the packet encapsulation, transmission, or capture process.

---

## Results ✅
- All generated packets were successfully captured in Wireshark
- Packet structure matched the TCP/IP standard
- Encapsulation, transmission, and capture processes worked as expected
- The project validates the correctness of manual packet construction

---

## Conclusion 🏁
This project provides hands-on experience with TCP/IP communication beyond the theoretical level.  
By manually building and analyzing packets, we gained a deeper understanding of encapsulation, protocol headers, checksums, and real network traffic behavior.

The combination of Python, Scapy, and Wireshark proved effective for learning and demonstrating how data flows through the TCP/IP stack in practice.
