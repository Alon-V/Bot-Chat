"""SettingUp the Chat Window UI and Functions"""

from datetime import datetime
from nicegui import ui
from fastapi import Request
from typing import Any, Optional

import socket
import threading
import random
import time
import uuid

from Common_Setups import SERVER_IP, SERVER_PORT
from State_Globals import (
    messages,
    active_users_list,
    avatar_urls,
    BG_COLORS,
    user_colors_cache,
    avatar_seeds,
)


# =====================================
# ===== Avatar & Color Management =====
# =====================================
# A function for assigning an avatar or a user -->
def get_avatar_url(username):
    if not username:    # If the username is empty we'll return a default avatar
        return "https://api.dicebear.com/7.x/bottts/svg?seed=unknown"
    if username not in avatar_seeds:    # Store the initial username as the seed for the avatar
        avatar_seeds[username] = username
    seed = avatar_seeds[username]   # Get the seed used for this user
    if seed not in user_colors_cache:   # Always returns the same avatar with a constant color for each user
        user_colors_cache[seed] = random.choice(BG_COLORS)
    bg_color = user_colors_cache[seed]
    if username == 'System':    # Special avatar for the System messages
        return "https://api.dicebear.com/7.x/bottts/svg?seed=system"
    return f"https://api.dicebear.com/7.x/adventurer/svg?seed={seed}&backgroundColor={bg_color}"    # Get the avatar from the "dicebear" website (avatar generator)

# A function to define the users name -->
def get_my_name_fallback(local_my_name: str) -> str:
    try: return ui.context.client.storage.get('my_name', local_my_name) # Read from client storage if available
    except Exception: return local_my_name  # Fallback value

name_edit_timer: dict[str, Optional[Any]] = {'t': None}  # Timer for username changing timeout

# ============================
# ===== Messages counter =====
# ============================
# Count how many messages should be visible for this user -->
def count_relevant_messages(own_name: str) -> int:
    c = 0
    for _mid, sender, _text, _stamp, target in messages:    # "Runs" on all the stored messages
        target_norm = 'ALL' if str(target or '').upper() == 'ALL' else str(target or '')
        if target_norm == 'ALL' or target_norm == own_name or sender == own_name:   # Checks how many messages relevant to me
            c += 1
    return c


# ===========================================
# ===== Main builder called from app.py =====
# ===========================================
async def build_chat_ui(request: Request) -> None:
    initial_name = request.query_params.get('nickname', '').strip()  # Default or named username

    # -----------------------------------
    # 1) Setting up name and variables
    # -----------------------------------
    if initial_name: my_name = initial_name
    else: my_name = f'User{random.randint(1000, 9999)}'  # Set the name to the given nickname or to a default one

    ui.context.client.storage['my_name'] = my_name  # Adding my name to the storage
    saved_avatar = ui.context.client.storage.get('my_avatar', '')
    my_avatar = saved_avatar if saved_avatar else get_avatar_url(my_name)  # Getting the new users or changed avatar
    ui.context.client.storage['my_avatar'] = my_avatar  # Adding my avatar to the storage

    # UI refs for later updates -->
    logged_as_label = None
    avatar_img_top = None
    avatar_img_footer = None
    name_input = None
    text = None
    target = None
    scroll_btn = None
    badge = None

    # --------------------------------
    # 2) Scroll + Rename sync state
    # --------------------------------
    # Variables to track after scrolling positions -->
    new_msg_counter = {'count': 0}  # A variable to track after messages that weren't read yet
    last_count = [count_relevant_messages(my_name)]  # Saves the last amount of new messages
    is_up = [False]  # Saves the information if the user is currently up
    #ui.on('scroll_state', lambda e: is_up.__setitem__(0, bool((e.args or {}).get('up', False))))  # Catches the event from the JavaScript on chat_messages

    def on_scroll_state(e):
        up = bool((e.args or {}).get('up', False))
        is_up[0] = up

        # אם חזרתי לתחתית -> להעלים כפתור + לאפס מונה
        if not up:
            new_msg_counter['count'] = 0
            if badge is not None:
                badge.text = ''
                badge.set_visibility(False)
            if scroll_btn is not None:
                scroll_btn.classes(remove='scale-100', add='scale-0')

    ui.on('scroll_state', on_scroll_state)
    latest_confirmed_name = [my_name]  # Rename pending state (thread -> UI)
    avatar_dirty = {'flag': False} # New Avatar flag
    name_edit_timer = {'t': None}  # timer handle
    name_dirty = {'flag': False}  # user typed but didn't confirm yet

    # -------------------------------
    # 3) Server-Client connections
    # -------------------------------
    # Creating a soket connection to the Server -->
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        client_socket.sendall((my_name + "\n").encode('utf-8'))  # Sending an "introduction" message to the server with our name
        ui.notify(f"Connected as {my_name}", type='positive')
    except Exception as e:
        ui.query('body').style('background-color: #1a0202; color: white;')
        ui.label(f"CONNECTION ERROR: {e}").classes('text-red-500 text-2xl font-bold m-4')
        ui.label("Please ensure 'Main_Server.py' is running!").classes('text-xl m-4')
        return

    # -----------------------------------------
    # 3.1) Scroll listener (real-time state)
    # -----------------------------------------
    # Tracking where you at all the time -->
    await ui.run_javascript(r'''
    (() => {
      const threshold = 200;   // px from bottom that still counts as "at bottom"
      let lastUp = null;
      let t = null;

      const calc = () => {
        const scrollPos = window.innerHeight + window.scrollY;
        const totalHeight = document.body.offsetHeight;
        const nearBottom = scrollPos >= (totalHeight - threshold);
        const up = !nearBottom;

        if (up !== lastUp) {
          lastUp = up;
          emitEvent('scroll_state', { up });
        }
      };

      window.addEventListener('scroll', () => {
        if (t) return;
        t = setTimeout(() => { t = null; calc(); }, 120);
      }, { passive: true });

      window.addEventListener('resize', calc);
      setTimeout(calc, 200); // initial
    })();
    ''')

    # ----------------------------------
    # 4) Open the Launcher (fixed JS)
    # ----------------------------------
    async def open_launcher():
        # Check if Launcher exists, if not (no heartbeat): open a new Launcher popup
        opened = await ui.run_javascript(r'''
            (async () => {
              const HEART = 'launcher_heartbeat_v2';    // localStorage key used as heartbeat timestamp
              const CH = 'launcher_ctrl_v1';            // BroadcastChannel name

              const bc = new BroadcastChannel(CH);
              const id = Math.random().toString(36).slice(2);

              let gotPong = false;
              const onMsg = (ev) => {
                const msg = ev.data || {};
                if (msg.type === 'PONG' && msg.id === id) gotPong = true;
              };
              bc.addEventListener('message', onMsg);

              // If a fresh heartbeat exists, we assume a Launcher is already open ->
              const last = Number(localStorage.getItem(HEART) || 0);
              if (Date.now() - last < 2500) {
                bc.postMessage({ type: 'PING', id });
                await new Promise(r => setTimeout(r, 250));
                if (gotPong) {  // If you fot a "PONG" (there is one): dont open a new one
                  bc.postMessage({ type: 'FOCUS' });
                  bc.removeEventListener('message', onMsg);
                  bc.close();
                  return false; // means: do not open new launcher
                }
              }

              bc.removeEventListener('message', onMsg);
              bc.close();

              // No launcher detected -> open a new window
              const w = window.open('/', '_blank', 'popup=yes,width=450,height=600,left=80,top=20');
              return !!w; // True if opened, False if blocked
            })();
            ''')
        if opened is False:
            ui.notify('Launcher is already open-> cant open a new one', type='warning', position='top')

    # --------------------------
    # 5) Avatar picker dialog
    # --------------------------
    avatar_choices = {'urls': []}
    selected_bg = {'value': None}  # None = random background

    def make_random_avatar_url(seed: str, bg=None) -> str:
        bg_color = bg or random.choice(BG_COLORS)
        return f"https://api.dicebear.com/7.x/adventurer/svg?seed={seed}&backgroundColor={bg_color}"

    # Grid
    @ui.refreshable
    def avatar_grid():
        with ui.grid(columns=4).classes('gap-7'):
            for url in avatar_choices['urls']:
                img = ui.image(url).classes('w-24 h-24 rounded-2xl border border-white/15 cursor-pointer hover:scale-105 transition')
                img.on('click', lambda e, u=url: choose_avatar(u))

    def regen_avatar_grid():
        bg = selected_bg['value']  # None אם לא נבחר
        avatar_choices['urls'] = [make_random_avatar_url(uuid.uuid4().hex[:8], bg=bg) for _ in range(8)]
        avatar_grid.refresh()

    def set_bg_none():
        selected_bg['value'] = None
        regen_avatar_grid()

    def pick_color(col: str):
        selected_bg['value'] = col
        regen_avatar_grid()

    def choose_avatar(url: str):
        ui.context.client.storage['my_avatar'] = url    # Local

        # tell server so it can broadcast to everyone
        try:
            client_socket.sendall(f"CMD:AVATAR:{url}\n".encode("utf-8"))
        except Exception as e:
            print("Failed to send avatar to server:", e)

        # שמירה גם במפה המקומית כדי שמייד יופיע
        me = str(ui.context.client.storage.get('my_name', my_name)).strip()
        avatar_urls[me] = url

        # עדכון התמונות ב-UI (טופ + פוטר)
        if avatar_img_top is not None:
            avatar_img_top.source = url
            avatar_img_top.update()
        if avatar_img_footer is not None:
            avatar_img_footer.source = url
            avatar_img_footer.update()

        # Tell server to broadcast my avatar to everyone:
        try:
            client_socket.sendall(f"CMD:AVATAR:{url}\n".encode("utf-8"))
        except Exception as e:
            print("Failed to send avatar update:", e)

        chat_messages.refresh()
        ui.notify('Avatar updated', type='positive', position='top')
        avatar_dialog.close()

    with ui.dialog() as avatar_dialog:
        with ui.card().classes(
                'w-[520px] max-w-[92vw] bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl shadow-2xl p-5'):
            # Header
            with ui.row().classes('w-full items-start justify-between'):
                with ui.column().classes('gap-0'):
                    ui.label('Choose Your Avatar').classes('text-white text-3xl font-bold')
                    ui.label('Pick one, or refresh for new options').classes('text-gray-300 text-md')
                ui.button(icon='close', on_click=avatar_dialog.close) \
                    .props('flat round dense') \
                    .classes('text-white hover:bg-white/10')

            ui.separator().classes('my-1 opacity-10')
            # Background picker
            ui.label('Background Colors ->').classes('text-gray-200 text-sm font-semibold tracking-wide mb-2')

            with ui.row().classes('w-full items-center justify-between gap-5 mb-3'):
                with ui.row().classes('gap-6 items-center'):
                    ui.button('Random', icon='casino', on_click=set_bg_none) \
                        .props('unelevated dense color=purple-10') \
                        .classes('bg-white/10 text-white hover:bg-white/15 rounded-xl')

                    ui.add_head_html(''' <style> .color-swatch:hover { outline: 2px solid rgba(255,255,255,0.75); outline-offset: 2px; } </style> ''')
                    with ui.row().classes('gap-2 items-center'):
                        for c in BG_COLORS:
                            ui.button('', on_click=lambda _=None, col=c: pick_color(col)) \
                                .props('flat dense') \
                                .style(
                                f'background-color: #{c}; width: 22px; height: 22px; min-width: 22px; '
                                'border-radius: 8px; border: 1px solid rgba(255,255,255,0.25);') \
                                .classes('color-swatch transition-transform duration-150 hover:scale-125 hover:shadow-lg')

                with ui.row().classes('w-full items-center justify-between'):
                    ui.label('Avatar options ->').classes( 'text-gray-200 text-md font-semibold tracking-wide leading-none')
                    ui.button('Refresh', icon='refresh', on_click=regen_avatar_grid) \
                        .props('unelevated dense color=teal-9') \
                        .classes('bg-emerald-600 text-white hover:bg-emerald-500 rounded-lg shadow text-xs px-2 py-1')
            avatar_grid()

    regen_avatar_grid()

    # ------------------------------------------------
    # 6) The chat message display logic and styling
    # ------------------------------------------------
    @ui.refreshable
    def chat_messages() -> None:
        own_name = ui.context.client.storage.get('my_name', '')  # Gets "my name" from the storage
        own_avatar = ui.context.client.storage.get('my_avatar', '')  # Gets "my avatar" from the storage
        # Filter messages to show only those relevant to the current user (Private or Global)
        relevant_messages = []
        for msg_id, sender, text, stamp, target in messages:
            raw_target = (target or '')
            target_norm = 'ALL' if raw_target.upper() == 'ALL' else raw_target  # Don't miss an "ALL" no matter how it written
            # Only if the message is for everyone / send to me / sent by me
            if target_norm == 'ALL' or target_norm == own_name or sender == own_name:
                relevant_messages.append(
                    (msg_id, sender, text, stamp, target_norm))  # Keep if it's to ALL / to me / by me

        # Shows the messages that were meant to me or sent from me -->
        if relevant_messages:
            for msg_id, sender, text, stamp, target_id in relevant_messages:  # To who I sent/received a message to/from
                sent_by_me = (sender == own_name)
                # Build a short label for the stamp- "Everyone / Direct"
                label = ""
                if target_id == 'ALL':
                    label = "To All"
                elif sent_by_me:
                    label = f"To {target_id}" if target_id != 'ALL' else ""
                elif target_id != 'ALL':
                    label = "Direct"

                # If it's a system message we'll add to her a unique Class
                is_system = (sender == 'System')

                # Avatar selection:
                if sent_by_me and own_avatar:
                    avatar = own_avatar  # If it's me, prefer my saved avatar from storage
                else:
                    avatar = avatar_urls.get(sender) or get_avatar_url(sender)  # otherwise, use synced avatar_urls OR generate based on name   @@@@@

                # Build the message bubble component & properties -->
                msg = ui.chat_message(name=sender, text=text, stamp=f"{stamp} {label}".strip(), avatar=avatar,sent=sent_by_me).props(f'key="{msg_id}"')
                if is_system:
                    msg.classes('system-msg')  # Different style for system messages
                else:
                    msg.classes('received-msg' if not sent_by_me else '')

        else:  # Display a placeholder when the chat is empty
            with ui.column().classes('flex items-center justify-center text-gray-400').style('min-height: 10vh'):
                ui.icon('chat_bubble_outline').classes('text-5xl mb-2')
                ui.label('No messages yet')

    # ------------------------------
    # 7) Listener thread (server)
    # ------------------------------
    # A function for listening to messages from the server (will run on background) -->
    def listen_to_server():
        buffer = ""  # Accumulates partial TCP chunks
        while True:
            try:  # receiving a message from the server (up to 1024 bits)
                chunk = client_socket.recv(4096).decode('utf-8', errors='replace')
                if not chunk: break
                buffer += chunk

                # ---- stage 1: Identifying the type of message by the protocol ---
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line: continue

                    parts = line.split("|")
                    if len(parts) < 2: continue  # protect protection from "broken" messages

                    msg_type = parts[0].strip()  # Could be MSG / USERS / ERR / ACK

                    # ---- option A: the server sent list of updated users ----
                    if msg_type == "USERS" and len(parts) >= 4:
                        # The format: USERS|System|All|user1,user2,user3
                        users_str = parts[3]
                        active_users_list.clear()
                        if users_str:  # if the list is not empty, we will update
                            active_users_list.extend([u.strip() for u in users_str.split(",") if u.strip()])

                    # ---- option A.1: server error (e.g., name taken) ----
                    elif msg_type == "ERR" and len(parts) >= 4:
                        # ERR|System|<who>|<code>
                        err_code = parts[3].strip()
                        ui.notify(f"Server error: {err_code}", type='negative', position='top')

                    # ---- option A.2: server ack (e.g., name changed approved) ----
                    elif msg_type == "ACK" and len(parts) >= 5:
                        # ACK|System|<old>|NAME_CHANGED|<new>
                        action = parts[3].strip()
                        if action == "NAME_CHANGED":
                            latest_confirmed_name[0] = parts[4].strip()

                    # ---- option A.3: server rename event (avatar seed sync) ----
                    elif msg_type == "RENAME" and len(parts) >= 3:
                        # RENAME|old|new
                        old_n = parts[1].strip()
                        new_n = parts[2].strip()
                        if old_n and new_n:
                            avatar_seeds[new_n] = avatar_seeds.get(old_n, old_n)
                        continue  # לא מוסיפים הודעה לצ'אט

                    # ---- option A.4: server change to avatar ---- @@@@@
                    elif msg_type == "AVATAR" and len(parts) >= 3:
                        # AVATAR|username|url
                        who = parts[1].strip()
                        url = "|".join(parts[2:]).strip()  # safe if '|' somehow appears
                        if who and url:
                            avatar_urls[who] = url
                            avatar_dirty['flag'] = True
                            # אם זה אני - נשמור גם ב-storage כדי שהטופ/פוטר והבועות שלי יתעדכנו
                            '''me = str(ui.context.client.storage.get('my_name', my_name)).strip()
                            if who == me:
                                ui.context.client.storage['my_avatar'] = url

                            '''
                            chat_messages.refresh()
                        continue

                    # ---- option B: the server sent a normal chat message ----
                    elif msg_type == "MSG" and len(parts) >= 5:
                        # MSG|sender|target|msg_id|content(with possible |)
                        sender = parts[1].strip()
                        raw_target = parts[2].strip()
                        target_id = 'ALL' if raw_target.upper() == 'ALL' else raw_target
                        msg_id = parts[3].strip()
                        content = "|".join(parts[4:])  # חשוב: אם יש '|' בתוך הודעה, שלא יחתוך לך

                        # Hide launcher system messages from chat users -->
                        if sender == 'System' and '__LAUNCHER__' in content: continue

                        # לשמור avatar קבוע אחרי rename לפי הודעת system
                        '''
                        if sender == 'System' and ' has changed the user_name to-> ' in content:
                            try:
                                old_n, new_n = [x.strip() for x in content.split(' changed name to ', 1)]
                                avatar_seeds[new_n] = avatar_seeds.get(old_n, old_n)
                            except Exception as e:
                                print(f"Error parsing system msg: {e}")
                        '''
                        if any(m[0] == msg_id for m in messages): continue  # If there is already a message with the same msg_id, we don't add it
                        # creating variables for the presentation -->
                        stamp = datetime.now().strftime('%H:%M')
                        # adding to the global list (saving the real target_id so we would know if it's private or for all) -->
                        messages.append((msg_id, sender, content, stamp, target_id))

            except Exception as e:
                print(f"Error receiving: {e}")
                break

    threading.Thread(target=listen_to_server,daemon=True).start()  # Activating the thread that is listening to the server

    # ----------------
    # 8) UI Updater
    # ----------------
    # Updating globally for all the users that are connected -->
    def update_ui():
        nonlocal logged_as_label
        current_me = ui.context.client.storage.get('my_name', my_name)
        confirmed_name = latest_confirmed_name[0]

        if avatar_dirty['flag']:
            avatar_dirty['flag'] = False
            chat_messages.refresh()

        # Name sync from server ACK:
        # === מנגנון סנכרון: אם יש חוסר תאמה, מבצעים עדכון כפוי ===
        if current_me != confirmed_name:
            print(f"Syncing name: {current_me} -> {confirmed_name}")

            # 1. עדכון הזיכרון
            ui.context.client.storage['my_name'] = confirmed_name

            # 2. עדכון ויזואלי
            if logged_as_label: logged_as_label.text = f'Logged as: {confirmed_name}'
            try:
                if name_input is not None: name_input.value = confirmed_name
            except:
                pass

            # 4. תיקון הודעות אחורה (כדי שהבועות יסתדרו)
            old_name = current_me
            new_name = confirmed_name
            for i, (mid, sender, msg_text, stamp, tgt) in enumerate(messages):
                new_sender = new_name if sender == old_name else sender
                new_tgt = new_name if tgt == old_name else tgt
                if new_sender != sender or new_tgt != tgt:  # If it's my old name or a different target
                    messages[i] = (mid, new_sender, msg_text, stamp, new_tgt)
            chat_messages.refresh()

            # הודעה למשתמש
            ui.notify(f"Name updated to: {confirmed_name}", type='positive', position='top')
            # we got a confirmed name -> stop revert timer
            name_dirty['flag'] = False
            t = name_edit_timer.get('t')
            if t is not None:
                try:
                    t.cancel()
                except Exception:
                    pass
            name_edit_timer['t'] = None
            # מעדכנים את המשתנה המקומי להמשך הפונקציה
            current_me = confirmed_name

        # refresh target select options:
        current_options = {'ALL': 'Everyone'}
        for user in active_users_list:
            u = str(user).strip()
            if u and u != current_me: current_options[u] = u
        if target.value not in current_options and target.value != 'ALL':
            target.value = 'ALL'
        target.options = current_options  # Refreshing all the users (except myself)
        target.update()

        current_relevant = count_relevant_messages(current_me)  # Updating the current count
        if current_relevant > last_count[0]:  # Checking if you have messages if you haven't read yet
            chat_messages.refresh()  # Refreshing the chat bubbles on the screen
            if is_up[0]:  # If there is a new message and the user is scrolled up
                new_msg_counter['count'] += (current_relevant - last_count[0])  # Deducting the messages you are reading from the msg_counter list
                badge.text = str(new_msg_counter['count'])
                badge.set_visibility(True)
                scroll_btn.classes(remove='scale-0', add='scale-100')  # Adapting the scrolling position
            else:  # If the user is down, we'll just automatically glide
                ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
            last_count[0] = current_relevant  # Updating the new current count of unread messages

    # ---------------------------
    # 9) Send + Rename actions
    # ---------------------------
    # A simple helper to scroll the page to the bottom -->
    def scroll_to_bottom_and_reset():
        new_msg_counter['count'] = 0    # Resetting counter
        if badge is not None and scroll_btn is not None:
            badge.text = ''     # Resetting the text
            badge.set_visibility(False)     # Making the button invisible again
            scroll_btn.classes(remove='scale-100', add='scale-0')
        ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)') # Forcefully scroll down

    # The function for sending the message to the chat -->
    def send() -> None:
        current_name = str(ui.context.client.storage.get('my_name', my_name)).strip()
        msg = (text.value or '').strip() if text is not None else ''
        if not msg:     # Validation: prevent sending empty strings or whitespace
            ui.notify('Cannot send empty message', type='warning', position='top')
            return
        try:
            if client_socket.fileno() == -1:
                ui.notify('You are disconnected. Please refresh.', type='negative')
                return

            raw_target = (target.value or 'ALL') if target is not None else 'ALL'
            recipient = ('ALL' if str(raw_target).upper() == 'ALL' else str(raw_target)).strip()

            if recipient != 'ALL' and recipient == current_name:
                ui.notify("You can't send a message to yourself", type='warning', position='top')
                if target is not None:target.value = 'ALL'
                return

            msg_id = f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"
            payload = f"{recipient}:{msg_id}:{msg}"
            client_socket.sendall((payload + "\n").encode("utf-8"))

            stamp = datetime.now().strftime('%H:%M')
            messages.append((msg_id, current_name, msg, stamp, recipient))
            chat_messages.refresh()

            if text is not None: text.value = ''

            ui.timer(0.1, scroll_to_bottom_and_reset, once=True)

        except OSError as e:    # Catch Errno 9
            ui.notify(f"Connection Lost! Please refresh. ({e})", type='negative', close_button=True)
        except Exception as e:
            ui.notify(f"Error sending: {e}", type='negative')

    # The function for updating your username from the name_input slot in the footer -->
    def update_name():
        new_name = (name_input.value or '').strip() if name_input is not None else ''
        if not new_name or len(new_name) > 9:   # Validation: Username cannot be empty and max 9 characters
            msg = 'The Name can not be empty!' if not new_name else 'The Name must be up to 9 characters!'
            ui.notify(msg, type='warning', position='top')      # "Warning" notification
            if name_input is not None:
                name_input.value = ui.context.client.storage.get('my_name', my_name)    # Show the former name in the name_input slot
            return

        # Prevent renaming to an already-online name (client-side):
        name_norm = new_name.casefold()
        current_me = str(ui.context.client.storage.get('my_name', my_name)).strip()

        online_norm = {u.strip().casefold() for u in active_users_list if u and u.strip()}
        online_norm.discard(current_me.casefold())

        if name_norm in online_norm:
            ui.notify(f'"{new_name}" is already online. Choose another name.', type='negative', position='top')
            if name_input is not None:
                name_input.value = current_me
            return

        if name_norm in {'system', 'admin'} or name_norm.startswith('__launcher__'):
            ui.notify('This name is reserved.', type='warning')
            return

        # If everything is clear we'll update the name and show a "Success" notification
        try:
            cmd = f"CMD:NAME_CHANGE:{new_name}"
            client_socket.sendall((cmd + "\n").encode("utf-8"))
            name_dirty['flag'] = False
        except Exception as e:
            ui.notify(f"Failed to update name: {e}", type='negative')
            name_input.value = my_name

    # If user typed something in name_input but didn't press Enter - revert after 8 sec -->
    def revert_name_if_not_confirmed():
        if not name_dirty['flag']:
            return

        # Revert typed text back to the actual confirmed name
        confirmed = str(ui.context.client.storage.get('my_name', my_name)).strip()
        if name_input is not None:
            name_input.value = confirmed
            name_input.update()
        name_dirty['flag'] = False

    # Start/reset a 8s timer every time user edits the name field -->
    def on_name_edit():
        name_dirty['flag'] = True

        # cancel previous timer
        t = name_edit_timer.get('t')
        if t is not None:
            try:
                t.cancel()
            except Exception:
                pass

        # start new 8s timer
        name_edit_timer['t'] = ui.timer(8.0, revert_name_if_not_confirmed, once=True)

    # --------------------------
    # 10) Disconnect handling
    # --------------------------
    closing = {'done': False}   # Closed or Open flag

    # Send QUIT only if socket is still open -->
    def safe_send_quit():
        try:
            if client_socket is not None and client_socket.fileno() != -1:
                client_socket.sendall(b"CMD:QUIT\n")
                print(">>> CMD:QUIT SENT")
        except Exception as ex:
            print(">>> CMD:QUIT send failed:", ex)

    # The function to handle the event of a client leaving the chat -->
    def handle_disconnect():
        # prevent double-close
        if closing['done']: return
        closing['done'] = True

        safe_send_quit()
        try: client_socket.shutdown(socket.SHUT_RDWR)
        except Exception: pass

        try: client_socket.close()
        except Exception: pass

    # immediate disconnections -->
    def close_me_now():
        print(">>> close_me_now TRIGGERED")
        handle_disconnect()

    ui.on('close_me_now', lambda _e: close_me_now())

    # When the tab is closed: client has disconnected -->
    ui.context.client.on_disconnect(handle_disconnect)
    ui.on('page_closing', lambda _e: handle_disconnect())   # Closing the socket as soon as thw window closed

    await ui.context.client.connected()
    await ui.run_javascript('window.addEventListener("beforeunload", () => { emitEvent("page_closing", {}); });')

    # close-all-chats channel listener
    await ui.run_javascript(r'''
       (() => {
         const bc = new BroadcastChannel('chat_control_v1');
         bc.onmessage = (ev) => {
           if (ev && (ev.data === 'CLOSE_ALL_CHATS' || ev.data === 'CLOSE_ME')) {
             try {
                // tell Python to close socket
                emitEvent("close_me_now", {});
                window.close();
             } catch(e) {}
           }
         };
       })();
       ''')

    # --------------
    # 11) Styling
    # --------------
    # Chat Background color and properties -->
    ui.query('body').style('''
                    background-color: #1a0202; 
                    background-image: radial-gradient(#3d0505 1px, transparent 0px);
                    background-size: 20px 20px;
                    margin: 0; padding: 0;
                ''')

    # AddOn page style -->
    ui.query('.q-page').style('background-color: transparent;')

    # An HTML definitions for the messages bubbles on the chat panel -->
    ui.add_head_html('''
                <style>
                    /* The name of the sender above the message bubble - white */
                    .q-message-name { color: white !important; font-weight: bold; opacity: 0.9; margin-bottom: 4px; }

                    /* The message bubble that you receive- gray */
                    .q-message-text { background: #9ba4b3 !important; color: black !important; border-radius: 12px !important; }

                    /* The message bubble that you send- white */
                    .q-message-sent .q-message-text { background: #ffffff !important; color: black !important; border-radius: 12px !important; }

                    /* Changing the Stamp color to light black (gray) */    
                    .q-message-stamp { color: rgba(0, 0, 0, 0.85) !important; }

                    /* The color of the text that you are typing (to prevent merge colors) */
                    input { color: white !important; } 

                    .system-msg .q-message-text { background: #121212 !important; color: #ffffff !important; border: 1px solid #333 !important; font-style: italic !important; font-size: 0.85rem; min-height: unset !important; }

                    .system-msg .q-message-text, .system-msg .q-message-text * { color: #ffffff !important; }

                    .system-msg .q-message-stamp { color: #ffffff !important; opacity: 0.9; }

                    .system-msg .q-message-name { color: #ffffff !important; font-size: 0.75rem !important; opacity: 0.7; }
                </style>
                ''')

    # CSS definition -->
    ui.add_css(r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}')

    # -----------------------------------------------
    # 12) The top bar (UI): pinned to the top left
    # -----------------------------------------------
    ui.add_head_html(''' <style> .avatar-hover:hover { box-shadow: 0 0 0 2px rgba(255,255,255,0.75); transform: scale(1.20);}
                            .avatar-hover { transition: transform 150ms ease, box-shadow 150ms ease; border-radius: 9999px; display: inline-flex; } </style>''')
    with (ui.row().classes('''fixed top-2 left-2 z-50 items-center bg-white/10 backdrop-blur-md py-2 px-4
                                rounded-2xl border border-white/20 shadow-2xl''')):
        # An Img button to open avatar change (top-left) -->
        with ui.avatar(size='md') \
                .classes('avatar-hover shadow-md border border-white/30') \
                .on('click', lambda: avatar_dialog.open()) \
                .tooltip('Change Avatar'):
            avatar_img_top = ui.image(ui.context.client.storage.get('my_avatar',my_avatar))     # Shows the avatar image @@@@@

        with ui.column().classes('gap-0'):  # Headlines and info
            ui.label('SECURITY STATUS: ENCRYPTED').classes('text-[10px] text-red-400 font-bold tracking-widest')
            logged_as_label = ui.label(f'Logged as: {my_name}').classes('text-sm font-bold text-white')

    # A button to open Launcher (top-right) -->
    with ui.row().classes(
            'fixed top-2 right-2 z-50 items-center bg-white/10 backdrop-blur-md py-2 px-2 '
            'rounded-2xl border border-white/20 shadow-2xl'):
        ui.button(icon='rocket_launch', on_click=open_launcher) \
            .props('dense flat') \
            .classes('text-white w-7 h-7 p-0 min-w-0 text-lg '
                     'transition-transform duration-150 hover:scale-110') \
            .tooltip('Open Launcher')

    # A button for auto-scrolling when you have new messages (hidden at first) -->
    with ui.button(on_click=scroll_to_bottom_and_reset) \
            .props('round unelevated') \
                  .classes('''fixed bottom-24 right-6 z-50 transition-all scale-0 
                                bg-black text-white 
                                border-[2px] border-white shadow-2xl''') \
                  .style('width: 38px; height: 38px; min-height: 38px;') as scroll_btn_ref:  # Button definition and his properties
        scroll_btn = scroll_btn_ref
        ui.icon('expand_more').classes('text-2xl font-bold')  # The icon of the button
        badge = ui.badge('', color='orange-600') \
            .props('floating') \
            .classes('text-[10px] px-1.5 py-0.5 font-bold border border-white shadow-sm')  # Number notification badge
        badge.set_visibility(False)

    # -----------------------------------------------
    # 13) The Footer: the main section of the chat
    # -----------------------------------------------
    footer = ui.footer().classes('bg-white/10 backdrop-blur-md py-4 px-6 border-t border-white/10 shadow-2xl')
    with footer:
        with ui.row().classes('w-full no-wrap items-center gap-3 max-w-4xl mx-auto'):  # They are all in the same row
            with ui.avatar():
                avatar_img_footer = ui.image(ui.context.client.storage.get('my_avatar', my_avatar)).classes('shadow-md border border-white/20') # ui.image(my_avatar).classes('shadow-md border border-white/20')  # Shows the avatar image

            # The name_input slot: where you can change and update your name -->
            name_input = ui.input(label='My Name', value=my_name) \
                .style('width: 80px') \
                .props('dense flat color=white label-color=red-600 input-style="color: white"') \
                .on('update:model-value', on_name_edit) \
                .on('keydown.enter', lambda _: update_name())


            # The text message input: where you can type your message to the chat -->
            text = ui.input(placeholder='message') \
                .on('keydown.enter', send) \
                .props('rounded standout="bg-white/20" color=white input-style="color: white"') \
                .classes('flex-grow bg-white/10 rounded-full text-white border border-white/10')

            # The target selection slot: to who to send from all the users (except myself) -->
            target = ui.select(options={'ALL': 'Everyone'}, value='ALL', label='Send to') \
                .props('dense outlined dark color=white popup-content-class="bg-red-750 text-white"') \
                .classes('w-32')

            # The send button -->
            ui.button(icon='send', on_click=send) \
                .props('flat') \
                .classes('''bg-red-900 text-white squared-full p-1.5 hover:bg-red-700 hover:scale-110
                            transition-all shadow-[0_0_15px_rgba(255,0,0,0.3)]''')

    # ---------------------------------------------------------------------------
    # 14) The Message Area: the section where connect and defines the messages
    # ---------------------------------------------------------------------------
    messages_area = (ui.column().classes('w-full max-w-2xl mx-auto items-stretch pt-11 p-4 mb-6 rounded-xl'))
    messages_area.props('id=messages_area')
    with messages_area:
        await ui.context.client.connected()  # Ensures the client is fully connected to the server before rendering chat messages (Awaits WebSocket establishment)
        ui.timer(0.1, lambda: ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)'),
                 once=True)  # Automatically scrolls to the bottom in a new user
        chat_messages()  # Calls to the message definition for this user

    # ---------------------------
    # 15) Start UI timer updates
    # ---------------------------
    ui.timer(0.1, update_ui)