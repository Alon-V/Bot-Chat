import socket
import threading
import time
import uuid

from Common_Setups import SERVER_PORT

def make_msg_id() -> str:
    return f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"

# Send one protocol line (server -> clients) -->
def send_line(sock: socket.socket, line: str) -> None:
    try:
        sock.sendall((line + "\n").encode("utf-8"))
    except Exception:
        pass

# ====================
# ===== Server CFG ===
# ====================
# Server Def. -->
HOST = '0.0.0.0'
PORT = SERVER_PORT

online_users = {}  # nickname -> socket
online_users_lock = threading.Lock()


# Sending a list of users separated by (,) -->
def tell_everyone_who_is_online() -> None:
    # Send USERS|System|ALL|name1,name2,... to all connected sockets:
    with online_users_lock:
        # Hide pseudo-users like __LAUNCHER__...
        current_users = [n for n in online_users.keys() if not str(n).startswith("__")]
        sockets = list(online_users.values())

    all_names = ",".join(current_users)
    system_message = f"USERS|System|ALL|{all_names}"    # Format: TYPE|SENDER|TARGET|CONTENT

    for user_socket in sockets:
        send_line(user_socket, system_message)


# Send one protocol line to everyone -->
def broadcast(line: str) -> None:
    with online_users_lock:
        sockets = list(online_users.values())
    for s in sockets:
        send_line(s, line)


# Server-side reserved names protection -->
def is_reserved_name(name: str) -> bool:
    n = (name or "").strip()
    if not n:
        return True
    if n.casefold() == "system":
        return True
    if n.startswith("__LAUNCHER__"):
        return True
    return False


def handle_single_client(client_socket: socket.socket, address):
    nickname = None
    try:
        # ------------------------------------------------------------
        # ----- Stage 1: receiving the first name and connecting -----
        # ------------------------------------------------------------
        nickname = client_socket.recv(1024).decode('utf-8', errors='replace')
        nickname = nickname.strip()
        if not nickname: return

        # block reserved names:
        if is_reserved_name(nickname):
            send_line(client_socket, f"ERR|System|{nickname}|NAME_TAKEN")
            try:
                client_socket.close()
            except Exception:
                pass
            return

        with online_users_lock:
            if nickname in online_users:
                send_line(client_socket, f"ERR|System|{nickname}|NAME_TAKEN")
                try: client_socket.close()
                except Exception: pass
                return
            online_users[nickname] = client_socket

        print(f"--> NEW FRIEND: {nickname} joined from {address}")

        # Updating list of users -->
        tell_everyone_who_is_online()

        # "Join Message": happens only once in the beginning -->
        broadcast(f"MSG|System|ALL|{make_msg_id()}|{nickname} -> has joined the chat")

        # -------------------------------------------------------------------
        # ----- Stage 2: the main loop that listens to all the messages -----
        # -------------------------------------------------------------------
        buffer = ""
        while True:
            chunk = client_socket.recv(4096).decode('utf-8', errors='replace')
            if not chunk:
                break
            buffer += chunk

            while "\n" in buffer:
                incoming_data, buffer = buffer.split("\n", 1)
                incoming_data = incoming_data.strip()
                if not incoming_data:
                    continue

                # ----- Client requested clean exit -----
                if incoming_data.startswith("CMD:QUIT"):
                    print(f"{nickname} requested quit")
                    buffer = ""  # optional: drop remaining buffered commands
                    raise ConnectionResetError  # or: return / break out nicely

                # ----- Name Change Command -----
                if incoming_data.startswith("CMD:NAME_CHANGE:"):
                    _, _, new_name_req = incoming_data.split(":", 2)

                    # Updating the dictionary: the old for the new
                    old_name = nickname
                    new_name = new_name_req.strip()  # Updating the local variable in the server

                    # validate new name on server side too:
                    if is_reserved_name(new_name):
                        send_line(client_socket, f"ERR|System|{old_name}|NAME_TAKEN")
                        continue

                    with online_users_lock:
                        if (not new_name) or (new_name in online_users):
                            send_line(client_socket, f"ERR|System|{old_name}|NAME_TAKEN")
                            continue

                        # Move socket from old_name to new_name:
                        if old_name in online_users:
                            del online_users[old_name]
                        nickname = new_name
                        online_users[nickname] = client_socket   # Re-enlisting

                    # ack to the client who requested it -->
                    send_line(client_socket, f"ACK|System|{old_name}|NAME_CHANGED|{nickname}")

                    print(f"--> {old_name} has changed the user_name to-> {nickname}")

                    # Update list + Inform everyone -->
                    tell_everyone_who_is_online()
                    broadcast(f"RENAME|{old_name}|{nickname}")
                    broadcast(f"MSG|System|ALL|{make_msg_id()}|{old_name} has changed the user_name to-> {nickname}")   # Message to everybody about the change
                    continue    # Skipping the rest of the loop because it's a command and not a normal text

                # ----- Avatar Change Command -----
                if incoming_data.startswith("CMD:AVATAR:"):
                    _, _, avatar_url = incoming_data.split(":", 2)
                    avatar_url = avatar_url.strip()
                    print("SERVER GOT AVATAR:", nickname, avatar_url)
                    if avatar_url:
                        # broadcast to everyone: AVATAR|username|url
                        broadcast(f"AVATAR|{nickname}|{avatar_url}")
                    continue

                # ----- Handling normal messages (TARGET:MSG_ID:TEXT) -----
                if ":" in incoming_data:
                    target_raw, rest = incoming_data.split(":", 1)
                    target_raw = target_raw.strip()
                    if ":" not in rest:
                        continue
                    msg_id, message_text = rest.split(":", 1)

                    target_is_all = (target_raw.upper() == "ALL")
                    target = "ALL" if target_is_all else target_raw

                    if target_is_all:
                        formatted_msg = f"MSG|{nickname}|ALL|{msg_id}|{message_text}"
                        with online_users_lock:
                            sockets = list(online_users.values())
                        for user_socket in sockets:
                            send_line(user_socket, formatted_msg)
                    else:
                        # Lookup exact username (no .upper())
                        with online_users_lock:
                            target_socket = online_users.get(target)
                        if target_socket:   # Sending to target
                            formatted_msg = f"MSG|{nickname}|{target}|{msg_id}|{message_text}"
                            send_line(target_socket, formatted_msg)
                            if target != nickname:  # Preventing duplication in client
                                send_line(client_socket, formatted_msg)

    except (ConnectionResetError, BrokenPipeError):
        pass
    except Exception as e:
        print(f"Error handling client {nickname}: {e}")
    finally:    # Handling exit
        should_announce = False

        with online_users_lock:
            if nickname and nickname in online_users:
                del online_users[nickname]
                should_announce = True

        # Exiting message -->
        if should_announce:
            broadcast(f"MSG|System|ALL|{make_msg_id()}|{nickname} -> has disconnected")

        try: client_socket.close()
        except Exception: pass
        print(f"Connection closed for {nickname}")
        tell_everyone_who_is_online()

def wake_up_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"Server is listening on port {PORT}...")

        while True:
            client, addr = server.accept()
            threading.Thread(target=handle_single_client, args=(client, addr)).start()
    except Exception as e:
        print(f"CRITICAL SERVER ERROR: {e}")


if __name__ == "__main__":
    wake_up_server()
