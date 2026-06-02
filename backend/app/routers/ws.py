"""WebSocket endpoint for real-time Ocorrencia feed."""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth.utils import decode_access_token
from app.schemas.ws_message import EventType, WSMessage
from app.services.ws_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/ocorrencias")
async def ws_ocorrencias(websocket: WebSocket):
    """WebSocket endpoint for live Ocorrencia feed.

    Opcional: autenticação via token JWT na query string ?token=...
    """
    token = websocket.query_params.get("token")
    user_email: str | None = None

    if token is not None:
        payload = decode_access_token(token)
        if payload is not None:
            user_email = payload.get("sub")

    await manager.connect(websocket, user_email)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                msg_type = data.get("type")

                if msg_type == EventType.PONG.value:
                    # heartbeat response — record PONG for timeout detection
                    manager.record_pong(websocket)
                else:
                    # echo unknown message types back as pong
                    pong = WSMessage(
                        type=EventType.PONG,
                        data={"received": data},
                    )
                    await manager.send_personal(pong, websocket)

            except json.JSONDecodeError:
                pong = WSMessage(
                  type=EventType.PONG,
                  data={"received": raw},
                )
                await manager.send_personal(pong, websocket)

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
