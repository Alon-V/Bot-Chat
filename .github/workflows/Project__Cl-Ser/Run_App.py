from nicegui import ui
import threading
import subprocess
import platform
import webbrowser

from Common_Setups import CHAT_UI_PORT, CHROME_PATH


def open_popup_app(url: str):
    try:
        system = platform.system()

        if system == 'Darwin':  # macOS
            subprocess.Popen([
                'open', '-n', '-a', 'Google Chrome',
                '--args',
                f'--app={url}',
                '--window-size=450,600',
                '--window-position=80,50',
            ])

        elif system == 'Windows':  # Windows
            subprocess.Popen(
                f'start chrome --app={url} --window-size=450,600 --window-position=80,50',
                shell=True
            )

        else:  # Linux / Unknown
            subprocess.Popen(['google-chrome', f'--app={url}'])

    except Exception as e:
        print("Failed to open Chrome app window:", e)
        # Fallback: open in default browser
        webbrowser.open(url)
'''
def open_popup_app(url: str) -> None:
    """Open Chrome in app-mode (popup-like window) to the given URL."""
    try:
        subprocess.Popen([
            CHROME_PATH,
            f"--app={url}",
            "--window-size=450,600",
            "--window-position=80,50",
        ])
    except Exception as e:
        print("Failed to open Chrome app window:", e)

'''
def run_chat_app() -> None:
    """
    Starts the NiceGUI server. The UI pages are defined in app.py
    (build_launcher_ui / build_chat_ui).
    """
    # Import here so UI_Router.py registers routes before ui.run starts
    import UI_Router  # noqa: F401

    url = f"http://localhost:{CHAT_UI_PORT}/"

    # Open the launcher window shortly after the server starts
    threading.Timer(0.5, open_popup_app, args=(url,)).start()

    # Run NiceGUI without auto-opening a regular browser tab
    ui.run(
        reload=False,
        port=CHAT_UI_PORT,
        show=False,
        title="Chat Launcher",
    )


if __name__ in {"__main__", "__mp_main__"}:
    run_chat_app()