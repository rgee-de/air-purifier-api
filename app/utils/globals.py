from app.services.websocket_manager import WebSocketManager
from models.status import StatusModel

latest_status = StatusModel().dict()
websocket_manager = WebSocketManager()
