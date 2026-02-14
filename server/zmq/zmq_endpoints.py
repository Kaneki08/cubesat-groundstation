# zmq_endpoints.py
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass(frozen=True)
class ZmqEndpoints:
    """
    Creates ZMQ endpoints that work whether you use TCP or IPC.
    transport:
      - "tcp": tcp://HOST:PORT
      - "ipc": ipc:///path/to.sock
      - "auto": return both (try in order)
    """
    transport: str
    host: str
    pub_port: int
    pull_port: int
    ipc_dir: Path

    @staticmethod
    def from_env() -> "ZmqEndpoints":
        transport = os.getenv("ZMQ_TRANSPORT", "auto").strip().lower()
        host = os.getenv("ZMQ_HOST", "127.0.0.1").strip()
        pub_port = int(os.getenv("ZMQ_PUB_PORT", "5556"))
        pull_port = int(os.getenv("ZMQ_PULL_PORT", "6000"))
        ipc_dir = Path(os.getenv("ZMQ_IPC_DIR", "/tmp/cubesat-zmq")).expanduser()
        return ZmqEndpoints(transport, host, pub_port, pull_port, ipc_dir)

    def _ipc_pub(self) -> str:
        self.ipc_dir.mkdir(parents=True, exist_ok=True)
        return f"ipc://{(self.ipc_dir / 'pub.sock').as_posix()}"

    def _ipc_pull(self) -> str:
        self.ipc_dir.mkdir(parents=True, exist_ok=True)
        return f"ipc://{(self.ipc_dir / 'pull.sock').as_posix()}"

    def _tcp_pub_bind(self) -> str:
        # bind on all interfaces if you're the "server" side
        return f"tcp://0.0.0.0:{self.pub_port}"

    def _tcp_pub_connect(self) -> str:
        return f"tcp://{self.host}:{self.pub_port}"

    def _tcp_pull_connect(self) -> str:
        return f"tcp://{self.host}:{self.pull_port}"

    def _tcp_pull_bind(self) -> str:
        return f"tcp://0.0.0.0:{self.pull_port}"

    def pub_bind_candidates(self) -> List[str]:
        if self.transport == "tcp":
            return [self._tcp_pub_bind()]
        if self.transport == "ipc":
            return [self._ipc_pub()]
        # auto: try tcp first (more common if distributed), then ipc
        return [self._tcp_pub_bind(), self._ipc_pub()]

    def pub_connect_candidates(self) -> List[str]:
        if self.transport == "tcp":
            return [self._tcp_pub_connect()]
        if self.transport == "ipc":
            return [self._ipc_pub()]
        return [self._tcp_pub_connect(), self._ipc_pub()]

    def pull_connect_candidates(self) -> List[str]:
        if self.transport == "tcp":
            return [self._tcp_pull_connect()]
        if self.transport == "ipc":
            return [self._ipc_pull()]
        return [self._tcp_pull_connect(), self._ipc_pull()]

    def pull_bind_candidates(self) -> List[str]:
        if self.transport == "tcp":
            return [self._tcp_pull_bind()]
        if self.transport == "ipc":
            return [self._ipc_pull()]
        return [self._tcp_pull_bind(), self._ipc_pull()]
