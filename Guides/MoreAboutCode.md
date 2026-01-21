1. Main_Server:
This script is the central hub of your system. It opens a "listening" port on your computer and waits for people to connect.
When a user joins, it creates a dedicated "Thread" just for them so it can handle multiple people talking at the same time without getting stuck.
Its main job is to receive a message from one person, figure out who it is meant for (everyone or a specific person), and deliver it.

2. Chat_UI:
This is the actual chat window that users see and interact with. It uses NiceGUI to draw the message bubbles, input box, and avatars on the screen.
it runs a background listener that constantly waits for incoming messages from the server so the screen updates instantly when someone texts you.
It also handles the "Handshake" logic, ensuring that when you close the window, it tells the server "I'm leaving" and waits for confirmation before shutting down.

3. Launcher_UI:
This is the first screen you see, acting as a dashboard for the whole system.
It has buttons to start or stop the Server process and allows you to launch new Chat windows.
It includes a special "Observer" feature—a hidden connection that stays online in the background to watch who joins or leaves the server.
This ensures the "Active Users" list in the red box is always correct, even if you don't have any chat windows open.

Common_Setups:
This hold some Importent stats like the IP address and Port number all other filles uses this and if you want to switch from Localhost to LAN this makes it easier

UI_Router:
This script decides which screen to show based on the URL.

Run_App:
This is the main script that starts your application. It launches the NiceGUI web server and automatically opens a Chrome window in "App Mode" (without the address bar) so the chat looks like a real desktop program.
It also imports the router to ensure all your pages are registered before the app begins.
