"""Threaded JSON-line LAN networking for the Star Wars game.

The module contains only standard-library networking code.  The Pygame main
thread never performs blocking socket I/O: both the server and the client use
background threads plus queues for incoming/outgoing messages.
"""
from __future__ import annotations

import json
import queue
import socket
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

LAN_PORT = 48732  # Fester LAN-TCP-Port; bei Bedarf hier ändern.
NETWORK_DEBUG = True  # Für einen stillen Release-Modus auf False setzen.
PROTOCOL_VERSION = 1
MAX_PLAYERS = 10
STATE_BROADCAST_INTERVAL = 0.05
SOCKET_CONNECT_TIMEOUT = 3.0
MAX_LINE_BYTES = 16_384
MAX_NAME_LENGTH = 20


def _safe_name(value: Any) -> str:
    name = str(value or "Spieler").strip()
    if not name:
        name = "Spieler"
    return name[:MAX_NAME_LENGTH]


def _safe_int(value: Any, default: int = 0, minimum: int = 0, maximum: int = 2_147_483_647) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def _safe_float(value: Any, default: float = 0.0, minimum: float = -10_000_000.0, maximum: float = 10_000_000.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def _send_line(sock: socket.socket, payload: Dict[str, Any]) -> None:
    data = (json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
    if len(data) > MAX_LINE_BYTES:
        raise ValueError("Netzwerkpaket ist zu groß")
    sock.sendall(data)


def _read_lines(sock: socket.socket):
    buffer = bytearray()
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            return
        buffer.extend(chunk)
        if len(buffer) > MAX_LINE_BYTES * 2:
            raise ValueError("Netzwerkpuffer ist zu groß")
        while b"\n" in buffer:
            line, _, buffer = buffer.partition(b"\n")
            if not line:
                continue
            if len(line) > MAX_LINE_BYTES:
                raise ValueError("Netzwerkpaket ist zu groß")
            yield json.loads(line.decode("utf-8"))


class _Connection:
    """One socket plus a dedicated sender queue/thread."""

    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.sock.settimeout(None)
        self.send_queue: queue.Queue[Optional[Dict[str, Any]]] = queue.Queue()
        self.closed = threading.Event()
        self.sender_thread = threading.Thread(target=self._sender_loop, daemon=True)

    def start_sender(self) -> None:
        self.sender_thread.start()

    def send(self, payload: Dict[str, Any]) -> None:
        if not self.closed.is_set():
            self.send_queue.put(payload)

    def close(self) -> None:
        if self.closed.is_set():
            return
        self.closed.set()
        try:
            self.send_queue.put_nowait(None)
        except queue.Full:
            pass
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass

    def _sender_loop(self) -> None:
        while not self.closed.is_set():
            try:
                payload = self.send_queue.get(timeout=0.25)
            except queue.Empty:
                continue
            if payload is None:
                return
            try:
                _send_line(self.sock, payload)
            except (OSError, ValueError):
                self.close()
                return


class LANServer:
    """LAN lobby/game server.

    The server stores the latest player state and broadcasts snapshots.  It
    does not simulate any game object.
    """

    def __init__(self, port: int = LAN_PORT, max_players: int = MAX_PLAYERS, debug: bool = True, game_mode: str = "lan"):
        self.port = int(port)
        self.max_players = max(1, min(MAX_PLAYERS, int(max_players)))
        self.debug = debug
        self.game_mode = str(game_mode or "lan")
        self._socket: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._broadcast_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._connections: Dict[str, _Connection] = {}
        self._players: Dict[str, Dict[str, Any]] = {}
        self._host_id: Optional[str] = None
        self._phase = "lobby"
        self._start_requested = False
        self._started_at = 0.0
        self._pvp_inputs: Dict[str, Dict[str, Any]] = {}
        self._pvp_fire_queue: Dict[str, List[Dict[str, Any]]] = {}

    @property
    def host_id(self) -> Optional[str]:
        with self._lock:
            return self._host_id

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.settimeout(0.5)
        self._socket.bind(("0.0.0.0", self.port))
        self._socket.listen(self.max_players)
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self._thread.start()
        self._broadcast_thread.start()
        self._log(f"Server gestartet auf Port {self.port}")

    def stop(self, reason: str = "server_stopped") -> None:
        if self._stop_event.is_set():
            return
        self._stop_event.set()
        if reason:
            self._broadcast({"type": "server_stopped", "reason": reason})
        with self._lock:
            connections = list(self._connections.values())
            self._connections.clear()
            self._players.clear()
        for connection in connections:
            connection.close()
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass
        self._log("Server beendet")

    def get_local_addresses(self) -> List[str]:
        addresses = {"127.0.0.1"}
        try:
            hostname = socket.gethostname()
            for item in socket.getaddrinfo(hostname, None, socket.AF_INET):
                addresses.add(item[4][0])
        except OSError:
            pass
        return sorted(addresses)

    def _accept_loop(self) -> None:
        assert self._socket is not None
        while not self._stop_event.is_set():
            try:
                client_socket, address = self._socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            with self._lock:
                can_join = self._phase == "lobby" and len(self._players) < self.max_players

            connection = _Connection(client_socket)
            connection.start_sender()
            if not can_join:
                connection.send({"type": "error", "reason": "Lobby voll oder bereits gestartet."})
                time.sleep(0.02)
                connection.close()
                continue

            thread = threading.Thread(
                target=self._client_loop,
                args=(connection, address),
                daemon=True,
            )
            thread.start()

    def _client_loop(self, connection: _Connection, address) -> None:
        player_id: Optional[str] = None
        try:
            iterator = _read_lines(connection.sock)
            first = next(iterator)
            if not isinstance(first, dict) or first.get("type") != "hello":
                connection.send({"type": "error", "reason": "Ungültiger Handshake."})
                return
            if _safe_int(first.get("version"), -1) != PROTOCOL_VERSION:
                connection.send({"type": "error", "reason": "Protokollversion passt nicht."})
                return
            requested_mode = str(first.get("game_mode") or "lan")[:24]
            if requested_mode != self.game_mode:
                connection.send({"type": "error", "reason": "Dieser Server erwartet einen anderen Spielmodus."})
                return

            with self._lock:
                if self._phase != "lobby" or len(self._players) >= self.max_players:
                    connection.send({"type": "error", "reason": "Lobby ist bereits geschlossen oder voll."})
                    return
                player_id = uuid.uuid4().hex[:8]
                if self._host_id is None:
                    self._host_id = player_id
                self._connections[player_id] = connection
                self._players[player_id] = {
                    "id": player_id,
                    "name": _safe_name(first.get("name")),
                    "x": 0.0,
                    "y": 0.0,
                    "width": 800,
                    "height": 600,
                    "ship": "xwing",
                    "score": 0,
                    "lives": 3,
                    "alive": True,
                    "ready": False,
                    "connected": True,
                    "address": str(address[0]) if address else "",
                }
                self._pvp_inputs[player_id] = {"left": False, "right": False}
                self._pvp_fire_queue[player_id] = []

            connection.send({
                "type": "welcome",
                "id": player_id,
                "host_id": self._host_id,
                "port": self.port,
                "game_mode": self.game_mode,
            })
            self._log(f"Player connected: {self._players[player_id]['name']}")
            self._broadcast_lobby()

            for message in iterator:
                if not isinstance(message, dict):
                    continue
                self._handle_message(player_id, message)
                if connection.closed.is_set():
                    break
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError, StopIteration):
            pass
        finally:
            if player_id is not None:
                self._remove_player(player_id)
            connection.close()

    def _handle_message(self, player_id: str, message: Dict[str, Any]) -> None:
        message_type = message.get("type")
        if message_type == "state":
            with self._lock:
                player = self._players.get(player_id)
                if not player:
                    return
                player["x"] = _safe_float(message.get("x"), player["x"], -10000, 10000)
                player["y"] = _safe_float(message.get("y"), player["y"], -10000, 10000)
                player["width"] = _safe_int(message.get("width"), player["width"], 320, 10000)
                player["height"] = _safe_int(message.get("height"), player["height"], 240, 10000)
                player["ship"] = str(message.get("ship") or player["ship"])[:32]
                player["score"] = _safe_int(message.get("score"), player["score"], 0, 2_147_483_647)
                player["lives"] = _safe_int(message.get("lives"), player["lives"], 0, 99)
                player["alive"] = bool(message.get("alive", player["alive"]))
            return

        if message_type == "pvp_input":
            if self.game_mode != "pvp":
                return
            with self._lock:
                if player_id in self._pvp_inputs:
                    self._pvp_inputs[player_id] = {
                        "left": bool(message.get("left", False)),
                        "right": bool(message.get("right", False)),
                    }
            return

        if message_type == "pvp_fire":
            if self.game_mode != "pvp":
                return
            weapon = str(message.get("weapon") or "laser")[:16]
            if weapon not in {"laser", "torpedo"}:
                return
            sequence = _safe_int(message.get("sequence"), 0, 0, 2_147_483_647)
            with self._lock:
                queue_for_player = self._pvp_fire_queue.setdefault(player_id, [])
                if len(queue_for_player) < 16:
                    queue_for_player.append({"weapon": weapon, "sequence": sequence})
            return

        if message_type == "name":
            with self._lock:
                player = self._players.get(player_id)
                if player:
                    player["name"] = _safe_name(message.get("name"))
            self._broadcast_lobby()
            return

        if message_type == "start_request":
            with self._lock:
                if player_id != self._host_id or self._phase != "lobby":
                    return
                if self.game_mode == "pvp" and len(self._players) != 2:
                    connection = self._connections.get(player_id)
                    if connection:
                        connection.send({"type": "error", "reason": "Für PvP-Duell müssen genau zwei Spieler verbunden sein."})
                    return
                self._phase = "setup"
                self._start_requested = True
                for player in self._players.values():
                    player["ready"] = False
            self._log("Host startet die Spielvorbereitung")
            self._broadcast({"type": "setup_started"})
            self._broadcast_lobby()
            return

        if message_type == "ready":
            with self._lock:
                player = self._players.get(player_id)
                if not player or self._phase != "setup":
                    return
                player["ready"] = True
                player["name"] = _safe_name(message.get("name", player["name"]))
                player["ship"] = str(message.get("ship") or "xwing")[:32]
                player["difficulty"] = str(message.get("difficulty") or "normal")[:24]
                if self.game_mode == "pvp":
                    rule = str(message.get("game_rule") or "last_survivor")[:24]
                    if rule in {"last_survivor", "points"}:
                        player["game_rule"] = rule
            self._maybe_start_countdown()
            return

        if message_type == "disconnect":
            self._remove_player(player_id)

    def _maybe_start_countdown(self) -> None:
        with self._lock:
            if self._phase != "setup" or not self._start_requested or not self._players:
                return
            if not all(bool(player.get("ready")) for player in self._players.values()):
                return
            self._phase = "countdown"
            self._started_at = time.time() + 3.0
            started_at = self._started_at
        self._log("Alle Spieler bereit – Countdown startet")
        self._broadcast({"type": "countdown", "started_at": started_at})

    def _broadcast_loop(self) -> None:
        while not self._stop_event.is_set():
            started = time.monotonic()
            with self._lock:
                if self._phase == "countdown" and time.time() >= self._started_at:
                    self._phase = "game"
                    game_message = {"type": "game_started"}
                else:
                    game_message = None
            if game_message:
                self._broadcast(game_message)

            with self._lock:
                should_snapshot = self._phase in {"lobby", "setup", "countdown", "game"}
            if should_snapshot:
                self._broadcast_snapshot()

            elapsed = time.monotonic() - started
            self._stop_event.wait(max(0.0, STATE_BROADCAST_INTERVAL - elapsed))

    def _broadcast_snapshot(self) -> None:
        with self._lock:
            players = [dict(player) for player in self._players.values()]
            host_id = self._host_id
            phase = self._phase
        self._broadcast({
            "type": "snapshot",
            "phase": phase,
            "host_id": host_id,
            "players": players,
        })

    def _broadcast_lobby(self) -> None:
        self._broadcast_snapshot()

    def _broadcast(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            connections = list(self._connections.values())
        for connection in connections:
            connection.send(payload)

    def _remove_player(self, player_id: str) -> None:
        with self._lock:
            player = self._players.pop(player_id, None)
            connection = self._connections.pop(player_id, None)
            self._pvp_inputs.pop(player_id, None)
            self._pvp_fire_queue.pop(player_id, None)
            is_host = player_id == self._host_id
            if is_host:
                self._host_id = None
        if connection:
            connection.close()
        if player:
            self._log(f"Player disconnected: {player['name']}")
        if is_host and not self._stop_event.is_set():
            self._broadcast({"type": "server_stopped", "reason": "Der Host hat das Spiel beendet."})
            self.stop(reason="Der Host hat das Spiel beendet.")
        else:
            with self._lock:
                if self._phase == "setup":
                    self._start_requested = True
            self._broadcast_lobby()
            self._maybe_start_countdown()

    def consume_pvp_inputs(self) -> tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
        """Return the latest inputs and one-shot fire events collected by the server."""
        with self._lock:
            inputs = {player_id: dict(state) for player_id, state in self._pvp_inputs.items()}
            fires = []
            for player_id, queue_for_player in self._pvp_fire_queue.items():
                for item in queue_for_player:
                    fires.append({"player_id": player_id, **dict(item)})
            for queue_for_player in self._pvp_fire_queue.values():
                queue_for_player.clear()
        return inputs, fires

    def broadcast_pvp_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Broadcast an authoritative PvP world snapshot to every player."""
        if self.game_mode != "pvp":
            return
        payload = dict(snapshot)
        payload["type"] = "pvp_snapshot"
        self._broadcast(payload)

    def _log(self, message: str) -> None:
        if self.debug:
            print(f"[NETWORK] {message}")


class LANClient:
    """Non-blocking-in-the-game-loop client for a LANServer."""

    def __init__(self, debug: bool = True):
        self.debug = debug
        self._connection: Optional[_Connection] = None
        self._receiver_thread: Optional[threading.Thread] = None
        self._connect_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._incoming: queue.Queue[Dict[str, Any]] = queue.Queue()
        self._lock = threading.RLock()
        self.player_id: Optional[str] = None
        self.host_id: Optional[str] = None
        self.connected = False
        self.connecting = False
        self.error: Optional[str] = None
        self.phase = "lobby"
        self.players: Dict[str, Dict[str, Any]] = {}
        self.started_at = 0.0
        self.host_disconnected = False
        self.game_mode = "lan"

    def connect_async(self, host: str, port: int, name: str, game_mode: str = "lan") -> None:
        self.disconnect()
        self._stop_event.clear()
        self.connecting = True
        self.error = None
        self.host_disconnected = False
        self.game_mode = str(game_mode or "lan")[:24]
        self._connect_thread = threading.Thread(
            target=self._connect_worker,
            args=(str(host).strip(), int(port), _safe_name(name)),
            daemon=True,
        )
        self._connect_thread.start()

    def _connect_worker(self, host: str, port: int, name: str) -> None:
        sock: Optional[socket.socket] = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_CONNECT_TIMEOUT)
            sock.connect((host, port))
            connection = _Connection(sock)
            connection.start_sender()
            self._connection = connection
            self.connecting = False
            self.connected = True
            connection.send({"type": "hello", "version": PROTOCOL_VERSION, "name": name, "game_mode": self.game_mode})
            self._receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._receiver_thread.start()
            self._log(f"Mit {host}:{port} verbunden")
        except (OSError, ValueError) as exc:
            self.connecting = False
            self.error = f"Verbindung fehlgeschlagen: {exc}"
            self.connected = False
            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass

    def _receive_loop(self) -> None:
        connection = self._connection
        if connection is None:
            return
        try:
            for payload in _read_lines(connection.sock):
                if isinstance(payload, dict):
                    self._incoming.put(payload)
                if connection.closed.is_set() or self._stop_event.is_set():
                    break
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
            pass
        finally:
            was_connected = self.connected
            self.connected = False
            connection.close()
            if was_connected and not self._stop_event.is_set():
                self._incoming.put({
                    "type": "server_stopped",
                    "reason": "Die Verbindung zum Host wurde unterbrochen.",
                })

    def send(self, payload: Dict[str, Any]) -> None:
        connection = self._connection
        if connection is not None and self.connected:
            connection.send(payload)

    def send_state(self, *, x: float, y: float, width: int, height: int, ship: str, score: int, lives: int, alive: bool, system_index: int = 0, system_name: str = "") -> None:
        self.send({
            "type": "state",
            "x": _safe_float(x),
            "y": _safe_float(y),
            "width": _safe_int(width, 800, 320, 10000),
            "height": _safe_int(height, 600, 240, 10000),
            "ship": str(ship or "xwing")[:32],
            "score": _safe_int(score, 0, 0),
            "lives": _safe_int(lives, 0, 0, 99),
            "alive": bool(alive),
            "system_index": _safe_int(system_index, 0, 0, 99),
            "system_name": str(system_name or "")[:40],
        })

    def send_pvp_input(self, left: bool, right: bool) -> None:
        self.send({"type": "pvp_input", "left": bool(left), "right": bool(right)})

    def send_pvp_fire(self, weapon: str, sequence: int) -> None:
        self.send({"type": "pvp_fire", "weapon": str(weapon)[:16], "sequence": int(sequence)})

    def send_name(self, name: str) -> None:
        self.send({"type": "name", "name": _safe_name(name)})

    def request_start(self) -> None:
        self.send({"type": "start_request"})

    def send_ready(self, name: str, ship: str, difficulty: str, game_rule: Optional[str] = None) -> None:
        payload = {
            "type": "ready",
            "name": _safe_name(name),
            "ship": str(ship)[:32],
            "difficulty": str(difficulty)[:32],
        }
        if game_rule in {"last_survivor", "points"}:
            payload["game_rule"] = game_rule
        self.send(payload)

    def poll(self) -> List[Dict[str, Any]]:
        events = []
        while True:
            try:
                payload = self._incoming.get_nowait()
            except queue.Empty:
                break
            events.append(payload)
            self._apply_event(payload)
        return events

    def _apply_event(self, payload: Dict[str, Any]) -> None:
        message_type = payload.get("type")
        if message_type == "welcome":
            self.player_id = str(payload.get("id") or "") or None
            self.host_id = str(payload.get("host_id") or "") or None
        elif message_type == "snapshot":
            with self._lock:
                self.phase = str(payload.get("phase") or self.phase)
                self.host_id = payload.get("host_id") or self.host_id
                players = payload.get("players", [])
                if isinstance(players, list):
                    self.players = {
                        str(player.get("id")): dict(player)
                        for player in players
                        if isinstance(player, dict) and player.get("id")
                    }
        elif message_type == "countdown":
            self.started_at = _safe_float(payload.get("started_at"), 0.0)
            self.phase = "countdown"
        elif message_type == "game_started":
            self.phase = "game"
        elif message_type == "setup_started":
            self.phase = "setup"
        elif message_type == "server_stopped":
            self.host_disconnected = True
            self.phase = "stopped"
            self.error = str(payload.get("reason") or "Host beendet")
            self.connected = False
        elif message_type == "error":
            self.error = str(payload.get("reason") or "Unbekannter Netzwerkfehler")

    def disconnect(self, graceful: bool = True) -> None:
        if graceful:
            self.send({"type": "disconnect"})
        self._stop_event.set()
        connection = self._connection
        self._connection = None
        self.connected = False
        self.connecting = False
        if connection is not None:
            connection.close()
        self.player_id = None
        self.host_id = None
        self.players = {}
        self.phase = "lobby"
        self.started_at = 0.0
        self.host_disconnected = False

    def _log(self, message: str) -> None:
        if self.debug:
            print(f"[NETWORK] {message}")
