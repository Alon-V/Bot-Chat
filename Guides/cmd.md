# How to find your IPv4 Address 🖥️

## Network Address Verification (Windows) 🪟

On Windows systems, the local IP address can be verified using the Command Prompt.

### Command Prompt Access
The Command Prompt can be opened by pressing **Windows + R**, which opens the *Run* dialog.

<div align="center">
  <img width="409" height="207" alt="Run dialog" src="https://github.com/user-attachments/assets/bb47b557-8d7f-44de-8031-f7edce224484" />
</div>

In the Run dialog, type `cmd` and press **Enter** to open the Command Prompt.

<div align="center">
  <img width="750" height="400" alt="Command Prompt" src="https://github.com/user-attachments/assets/28f65585-e3cb-4d3f-8bd1-38a84da8f7a0" />
</div>

### IP Address Identification
Once the Command Prompt is open, execute the following command: 'ipconfig'

---

## Network Address Verification (macOS) 🍎

On macOS, the active IP address can be identified using one of the following methods:

### System Settings
The local IP address can be viewed through the operating system settings by navigating to:
**System Settings → Network → Active Network Interface (Wi-Fi or Ethernet)**.  
The assigned IP address is displayed under the connection details.

step (1)->
<div align="center">
<img width="500" height="500" alt="Network Settings" src="https://github.com/user-attachments/assets/65f6a8af-7576-4f56-a280-fd76f0cbca12" />
</div>

step (2)->
<div align="center">
<img width="500" height="500" alt="IPv4 Location in Settings" src="https://github.com/user-attachments/assets/823d0328-3709-40ca-8bc4-f901dd1f0100" />
</div>

### Terminal Commands
Alternatively, the IP address can be obtained using the command line.

First, open the terminal on your conputer, then type the following commands:

- For Wi-Fi connections:
"ipconfig getifaddr en0"

- For Ethernet connections:
"ipconfig getifaddr en1"

- To display all network interfaces:
"ifconfig"

for example->
<div align="center">
<img width="582" height="158" alt="Terminal IPv4" src="https://github.com/user-attachments/assets/3c94c855-10da-49d4-a33c-1b8b7a8f067b" />
</div>
