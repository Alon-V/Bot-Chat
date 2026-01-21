"""Decides What to Open -> (Chat / Launcher) """

from nicegui import ui
from fastapi import Request

from Launcher_UI import build_launcher_ui
from Chat_UI import build_chat_ui


@ui.page('/')
async def main(request: Request) -> None:
    is_chat = (request.query_params.get('mode') == 'chat')

    if is_chat:
        await build_chat_ui(request)
    else:
        await build_launcher_ui(request)