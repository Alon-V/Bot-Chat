"""SettingUp the Launcher Window UI and Functions"""

from nicegui import ui
from fastapi import Request
import os, sys, socket, subprocess, signal, threading, time, uuid
from typing import Optional, Dict

from Common_Setups import SERVER_IP, SERVER_PORT
from State_Globals import active_users_list, messages


# ===========================================
# ===== Main builder called from app.py =====
# ===========================================
async def build_launcher_ui(request: Request) -> None:
    ui.query('body').style('background-color: #4a0404')  # Set a background color

    # ---------------------------------
    # ----- Server toggle support -----
    # ---------------------------------
    SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), 'Main_Server.py')  # The path to the server
    server_proc: Dict[str, Optional[subprocess.Popen]] = {'p': None}  # Holds the server process reference so we use it later

    # Check server availability by trying to connect to the TCP port -->
    def is_server_running() -> bool:
        try:  # Try to connect quickly. If it works, server is running.
            with socket.create_connection((SERVER_IP, SERVER_PORT), timeout=0.25):
                return True
        except OSError:
            return False

    # Start server as a subprocess -->
    def start_server() -> bool:
        if is_server_running():  # Checks if it is already running: if it is we don't need it
            return True
        try:
            server_proc['p'] = subprocess.Popen(
                [sys.executable, SERVER_SCRIPT],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,  # Needed on Mac for clean terminate/kill
            )  # Opens the server subprocess
            ui.notify('Server started', type='positive')
            return True
        except Exception as e:
            ui.notify(f'Failed to start server: {e}', type='negative')
            server_proc['p'] = None  # Reset stored process handle
            return False

    # Fallback: kill the process that is listening on SERVER_PORT -->
    def kill_server_by_port():
        try:
            # list open files/sockets and find who listens on TCP:SERVER_PORT:
            out = subprocess.check_output(["lsof", "-nP", f"-iTCP:{SERVER_PORT}", "-sTCP:LISTEN"], text=True)
            # Remove header line and empty lines:
            lines = [ln for ln in out.splitlines() if ln and "PID" not in ln]
            for ln in lines:  # Each line contains PID in column index 1
                parts = ln.split()
                pid = int(parts[1])
                os.kill(pid, signal.SIGTERM)  # Send SIGTERM to terminate process politely
        except subprocess.CalledProcessError:
            pass
        except Exception as e:  # Couldn't kill the server
            print("kill_server_by_port error:", e)

    # Stop the server subprocess, or fallback to kill by port -->
    def stop_server():
        p = server_proc['p']
        if p is None:  # If we don't have the Popen handle, try kill by port
            ui.notify("No local server proc; trying to stop by port...", type='warning')
            kill_server_by_port()
            return
        try:  # Try to terminate gracefully
            p.terminate()
            try:
                p.wait(timeout=1.5)
            except Exception:  # Didn't worked: kill it
                p.kill()
        finally:  # Always reset handle
            server_proc['p'] = None
            ui.notify('Server stopped', type='warning')

    # ------------------------------------------
    # ----- Launcher observer (USERS sync) -----
    # ------------------------------------------
    # A hidden TCP connection from the launcher window to the server:
    launcher_socket: Optional[socket.socket] = None

    # Connect to server as a special launcher client -->
    # (name starts with __LAUNCHER__)
    def start_launcher_observer():
        nonlocal launcher_socket
        if launcher_socket is not None:
            return

        try:
            # Create TCP socket and connect to server:
            launcher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            launcher_socket.connect((SERVER_IP, SERVER_PORT))

            # Send a unique launcher name so server doesn't reject it as duplicate:
            launcher_name = f"__LAUNCHER__{uuid.uuid4().hex[:6]}"  # Random Hex at the end of the name (unique)
            launcher_socket.sendall(launcher_name.encode('utf-8'))
        except Exception as e:
            print("Launcher observer connect failed:", e)
            return

        # Background loop: reads server lines and updates active_users_list -->
        def listen_launcher():
            buffer = ""
            while True:
                try:
                    chunk = launcher_socket.recv(4096).decode("utf-8", errors="replace")  # Receive bytes from server, decode to string
                    if not chunk: break  # Socket closed -> exit thread
                    buffer += chunk  # Add to buffer
                    # Process full lines (server protocol ends lines with '\n'):
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if not line: continue

                        parts = line.split("|")  # Server message format uses "|"
                        if len(parts) >= 4 and parts[0].strip() == "USERS":  # Expected USERS format: USERS|System|All|user
                            users_str = parts[3]
                            active_users_list.clear()  # Replace the whole users list
                            if users_str:  # If server sent non-empty list, split it by commas
                                active_users_list.extend([
                                    u.strip() for u in users_str.split(",")
                                    # ignore empty names and ignore launcher pseudo-users:
                                    if u.strip() and not u.strip().startswith("__LAUNCHER__")
                                    ])
                except Exception as e:
                    print("Launcher observer recv error:", e)
                    break

        # Start thread that listens to the server in background:
        threading.Thread(target=listen_launcher, daemon=True).start()

    start_launcher_observer()  # Start immediately

    # Close the launcher observer socket when the UI client disconnects -->
    def stop_launcher_observer():
        nonlocal launcher_socket
        try:
            if launcher_socket is not None:
                launcher_socket.close()
        except Exception:
            pass
        launcher_socket = None

    # When this browser tab disconnects, close launcher observer socket -->
    ui.context.client.on_disconnect(stop_launcher_observer)


    # ----------------------------------
    # ----- Close all chat windows -----
    # ----------------------------------
    # The function to close all the active chats -->
    def close_all_chats():
        # A JavaScript command that is closing all the windows that were opened
        ui.run_javascript(r'''
            // 1) Broadcast: ask ALL chat windows to close
            try {
                const bc = new BroadcastChannel('chat_control_v1');
                bc.postMessage('CLOSE_ALL_CHATS');
                bc.close();
            } catch(e) {}

            // 2) If we stored references to windows, try to close them too
            if (window.openedWindows && Array.isArray(window.openedWindows)) {
                window.openedWindows.forEach(w => { try { w.close(); } catch(e) {} });
            }

            // Reset counters and references
            window.chatWindowCount = 0;
            window.openedWindows = [];
        ''')
        active_users_list.clear()  # Clear active users list on the launcher side
        ui.notify('Active users list cleared', type='info', color='green')

    # ---------------------------------
    # ----- Shutdown whole system -----
    # ---------------------------------
    # A function to shut down the whole system (from start to end) -->
    def shutdown_system():
        # stop_server()  # Closing the server
        ui.notify('Shutting down system...', type='negative')
        # 1) ask all chat windows to close FIRST
        close_all_chats()

        # 2) stop server shortly after (give windows time to react)
        ui.timer(1.0, stop_server, once=True)

        # 3) close launcher window last
        ui.timer(1.3, lambda: ui.run_javascript('window.close();'), once=True)

        # 4) finally stop the launcher process (optional)
        ui.timer(1.8, lambda: os.kill(os.getpid(), signal.SIGTERM), once=True)

    # ---------------------------------
    # ----- Server UI indicator -----
    # ---------------------------------
    server_icon = None
    server_toggle = None

    # Update the server icon + toggle switch to reflect actual server state -->
    def update_server_ui():
        nonlocal server_icon, server_toggle
        if server_icon is None or server_toggle is None:
            return

        running = is_server_running()

        # icon + color:
        if running:  # If server is running -> green cloud_done icon
            server_icon.name = 'cloud_done'
            server_icon.classes(remove='text-red-500', add='text-green-500')
            server_icon.tooltip('Server Online')
        else:  # If server is off -> red cloud_off icon
            server_icon.name = 'cloud_off'
            server_icon.classes(remove='text-green-500', add='text-red-500')
            server_icon.tooltip('Server Offline')
        server_icon.update()  # Force icon redraw

        # Keep toggle switch in sync with real state:
        if server_toggle.value != running:
            server_toggle.value = running
            server_toggle.update()

    # Callback fired when user toggles the server switch in UI -->
    def on_server_toggle(e):
        val = None
        # Set value as appeared:
        if isinstance(e.args, dict):
            val = e.args.get('value')
        elif isinstance(e.args, (list, tuple)) and e.args:
            val = e.args[0]
        want_on = bool(val)  # What the server want
        running = is_server_running()  # Actual current state
        if want_on == running: return
        if want_on:  # Starting server
            if not start_server(): ui.notify('Failed to start server (check console)', type='negative')
        else:  # Stopping server: close all chat windows and clear state
            close_all_chats()
            try:
                messages.clear()
            except Exception:
                pass
            active_users_list.clear()
            stop_server()
        update_server_ui()  # Refresh UI indicator

    # ---------------------------------------------
    # ----- Dialog UI to display active users -----
    # ---------------------------------------------
    # Setting the dialogue window for showing the activity users -->
    with ui.dialog() as users_dialog, ui.card().classes('w-80 bg-red-950 border border-white/20 shadow-2xl p-4'):
        ui.label('Active Users:').classes('text-white text-xl font-bold mb-4 border-b border-white/10 w-full pb-2')
        users_list_container = ui.column().classes(
            'w-full gap-3')  # A container that will update every time we open the window
        with ui.row().classes('w-full justify-end mt-4'):
            ui.button('CLOSE', on_click=users_dialog.close).props('flat').classes(
                'text-white border border-white/40 squared-full px-4')  # Closing button and properties

    # A function for updating and showing the dialogue content-->
    def show_active_users():
        users_list_container.clear()  # Clearing the old list
        users_list_container.classes('overflow-visible')  # Ensure the container can grow
        with users_list_container:
            if not active_users_list:  # If we have no users yet
                ui.label('No data available yet...').classes('text-gray-400 italic text-sm')
                ui.label('(Open a chat window to sync)').classes('text-gray-600 text-xs')
            else:  # Create one row per user
                for name in active_users_list:
                    with ui.row().classes(
                            'items-center w-full justify-between bg-white/5 p-2 rounded-lg overflow-visible min-w-0'):
                        with ui.row().classes('items-center gap-3 min-w-0'):
                            ui.icon(name='account_circle', color='red-200').classes('text-3xl shrink-0')
                            ui.label(name).classes('text-white font-large truncate')
                        ui.icon(name='link', color='green-400').classes(
                            'text-xl shrink-0 opacity-80 hover:opacity-100 transition-all').tooltip('Connected')
        users_dialog.open()  # Finally open the dialog

    # If dialog is open, refresh it periodically -->
    def refresh_users_dialog():
        if users_dialog.value:
            show_active_users()

    ui.timer(0.5, refresh_users_dialog)  # Every 0.5 sec check if dialog is open and refresh its content

    # -------------------------------------------------------------
    # ----- Launcher presence + focus bridge (anti-duplicate) -----
    # -------------------------------------------------------------
    await ui.run_javascript(r'''
            (() => {
              const HEART = 'launcher_heartbeat_v2';
              const CH = 'launcher_ctrl_v1';

              // heartbeat every 0.8 sec
              const beat = () => localStorage.setItem(HEART, String(Date.now()));
              beat();
              window.__launcherBeatTimer = setInterval(beat, 800);

              const bc = new BroadcastChannel(CH);
              bc.onmessage = (ev) => {
                const msg = ev.data || {};
                if (msg.type === 'PING') {
                  try { window.focus(); } catch(e) {}
                  bc.postMessage({ type: 'PONG', id: msg.id });
                  return;
                }
                if (msg.type === 'FOCUS') {
                  try { window.focus(); } catch(e) {}
                }
              };

              window.addEventListener('beforeunload', () => {
                try { clearInterval(window.__launcherBeatTimer); } catch(e) {}
                // We dont delete the HEART to avoid "uncleaned" closing that will break identification
              });
            })();
            ''')

    # ----------------------------------------------------------
    # ----- Start launcher observer (only if server is up) -----
    # ----------------------------------------------------------
    if is_server_running():
        start_launcher_observer()

    # ------------------------------
    # ----- Launcher UI Layout -----
    # ------------------------------
    with ui.column().classes('w-full items-center justify-center h-screen'):
        with ui.card().classes(
                'relative w-96 p-8 rounded-3xl items-center bg-white/10 backdrop-blur-md border border-white/20 shadow-2xl'):
            # A menu button in the top right corner -->
            with ui.column().classes('absolute top-1 right-1 z-50 items-center gap-1 self-end'):
                # The main operating button
                def toggle_admin():
                    admin_actions.set_visibility( not admin_actions.visible)  # The menu buttons are not visible until we toggle the settings button
                    btn_main.props(f'icon={"close" if admin_actions.visible else "settings"}')  # Changing the button icons accordingly

                btn_main = ui.button(icon='settings', on_click=toggle_admin) \
                    .props('round color=red-900 shadow-lg')  # The settings button properties

                # The buttons are opening down:
                with ui.column().classes('items-center gap-1') as admin_actions:
                    admin_actions.set_visibility(False)
                    # Using scale and dense for them to be small
                    ui.button(icon='group', on_click=show_active_users) \
                        .props('round dense color=red-800').classes('scale-75') \
                        .tooltip('Show Active Users')  # Active users button
                    ui.button(icon='close_fullscreen', on_click=close_all_chats) \
                        .props('round dense color=red-700').classes('scale-75') \
                        .tooltip('Close all chat windows')  # Closing all operating chats button
                    ui.button(icon='power_settings_new', on_click=shutdown_system) \
                        .props('round dense color=black').classes('scale-75') \
                        .tooltip('Shutdown System')  # System shutdown button

            # Server icon + toggle (standalone, top-left) -->
            ui.add_head_html(""" <style> .cloud-outline { filter: drop-shadow(0 0 4px #ffffff); } </style> """)
            with ui.row().classes('absolute top-0 left-3 z-50 items-center gap-1'):
                server_icon = ui.icon('cloud_off').classes('text-red-500 text-2xl cloud-outline')
                server_toggle = ui.switch().props('color=blue')
                server_toggle.on('update:model-value', on_server_toggle)

            update_server_ui()
            ui.timer(3.0, update_server_ui)  # polling עדין, לא “דוחף” סתם

            # Headlines, Icons and Info -->
            ui.icon('rocket_launch', color='white').classes('text-6xl mb-4')
            ui.label('Welcome to the Chat 👋').classes('text-white text-2xl font-bold')
            ui.label('COMMAND CENTER').classes('text-white text-lg font-bold tracking-tighter mb-2')

            with ui.row().classes('items-center gap-2 mb-6'):
                ui.icon('account_circle', color='red-200').classes('text-3xl')
                ui.label('Create a New User').classes('text-red-200 text-2xl font-bold tracking-tighter')

            # The function to initiate a new chat from the menu -->
            def launch_chat():
                name = (new_user_name.value or '').strip()
                if not name or len(name) > 9:  # Validation: Username cannot be empty and max 9 characters
                    ui.notify('Please enter a name (1-9 chars)', type='warning')
                    return

                # Prevent using an online / system / launcher name (client-side) -->
                name_norm = name.casefold()
                online_norm = {u.strip().casefold() for u in active_users_list if u and u.strip()}
                if name_norm in online_norm:
                    ui.notify(f'"{name}" is already online. Choose another name.', type='negative')
                    return
                if name_norm in {'system'} or name_norm.startswith('__launcher__'):
                    ui.notify('This name is reserved.', type='warning')
                    return
                js_code = f"""
                            if (window.chatWindowCount === undefined) window.chatWindowCount = 0;       // Resetting the variables
                            if (window.openedWindows === undefined) window.openedWindows = [];          // Resetting the variables
                            window.openedWindows = window.openedWindows.filter(w => w && !w.closed);    // remove already-closed windows from the list
                            let offset = window.chatWindowCount * 50;                                   // Calculate the location
                            let url = '/?mode=chat&nickname={name}';                                    // Building the url
                            let newWin = window.open(url, '_blank', `popup=yes,width=650,height=400,left=${{100 + offset}},top=${{100 + offset}}`);
                            if (newWin) window.openedWindows.push(newWin);                              // Saving the window on the list
                            window.chatWindowCount++; """   # JavaScript to open a new popup window with a cascading offset and saves the info
                ui.run_javascript(js_code)  # Opens a popup chat window
                ui.notify(f'Opening chat for {name}...', type='positive')
                new_user_name.value = ''  # Reset the box input for the next name

            new_user_name = ui.input(label='Enter Nickname', placeholder='Up to 9 chars...') \
                .classes('w-full mb-8') \
                .props('dark standout="bg-red-900/30" color=white label-color=red-200') \
                .style('color: white !important;') \
                .props('input-style="color: white"') \
                .props('counter maxlength=9') \
                .on('keydown.enter', launch_chat)  # The new name box input definition

            ui.button('LAUNCH CHAT', on_click=launch_chat) \
                .classes('''
                    w-full py-4 rounded-xl font-bold text-white shadow-lg
                    bg-red-900 hover:bg-red-700 
                    transform transition-all duration-300 hover:scale-105
                    hover:shadow-[0_0_20px_rgba(255,0,0,0.4)]
                    tracking-widest
                ''').style('background-color: #7f1d1d !important;')  # 'LAUNCH CHAT' button definition

            ui.label('The control panel stays open to add more users.').classes(
                'text-xs text-gray-400 mt-4')  # 'Notice' label