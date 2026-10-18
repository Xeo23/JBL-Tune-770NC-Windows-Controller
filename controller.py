import os
import re
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
from settings import save_address, normalize_address


def get_windows_battery():
    cmd = r"""Get-PnpDevice -Class 'Bluetooth' | ForEach-Object {
        if ($_.FriendlyName -eq 'JBL Tune 770NC') {
            $b = $_ | Get-PnpDeviceProperty -KeyName '{104EA319-6EE2-4701-BD47-8DDBF425BBE5} 2' -ErrorAction SilentlyContinue
            if ($b.Type -ne 'Empty') { "$($b.Data)" }
        }
    }"""

    try:
        out = subprocess.check_output(
            ["powershell.exe", "-NoProfile", "-Command", cmd],
            text=True,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        for line in out.splitlines():
            if line.strip().isdigit():
                return int(line.strip())

    except Exception as e:
        print("Battery error:", e)

    return -1


class Signals(QObject):
    finished = Signal(str, object, object)


class Task(QRunnable):
    def __init__(self, address, command):
        super().__init__()
        self.address = address
        self.command = command
        self.signals = Signals()

    def run(self):
        try:
            result = self.execute()
            self.signals.finished.emit(self.command, result, None)
        except Exception as exc:
            self.signals.finished.emit(self.command, None, str(exc))

    def execute(self):
        # Locate the backend in development or in the PyInstaller bundle.
        if getattr(sys, "frozen", False):
            backend = Path(sys._MEIPASS) / "anc.py"
        else:
            backend = Path(__file__).resolve().with_name("anc.py")

        if not backend.is_file():
            raise RuntimeError(
                f"Cannot find anc.py:\n{backend}"
            )

        # Preserve the Bluetooth address for the backend process.
        env = os.environ.copy()
        if self.address:
            env["JBL_BD"] = self.address

        # Refresh and connection tests use the backend's "get" command.
        command = (
            "get"
            if self.command in ("refresh", "test")
            else self.command
        )

        # A frozen app must invoke its own hidden backend mode.
        # In development, launch anc.py using the regular Python interpreter.
        if getattr(sys, "frozen", False):
            args = [
                sys.executable,
                "--jbl-backend",
                command,
            ]
        else:
            args = [
                sys.executable,
                str(backend),
                command,
            ]

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=12,
                cwd=str(backend.parent),
                env=env,
                creationflags=getattr(
                    subprocess, "CREATE_NO_WINDOW", 0
                ),
            )

        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "The Bluetooth command timed out. Check that your "
                "headphones are powered on and paired."
            )

        output = "\n".join(
            part.strip()
            for part in (result.stdout, result.stderr)
            if part and part.strip()
        )

        if result.returncode != 0:
            raise RuntimeError(
                output
                or f"anc.py exited with code {result.returncode}."
            )

        if command == "poweroff":
            return {
                "status": "Power-off command sent.",
                "connected": False,
                "mode": "UNKNOWN",
                "output": output,
            }

        match = re.search(
            r"\(mode=([^)]+)\)", output, re.IGNORECASE
        )
        mode = (
            match.group(1).strip().upper()
            if match
            else "UNKNOWN"
        )

        if mode in ("AMBIENTAWARE", "AMBIENT AWARE"):
            shown = "Ambient Aware"
            mode = "AMBIENTAWARE"
        elif mode == "TALKTHRU":
            shown = "TalkThru"
        elif mode == "ANC":
            shown = "ANC"
        elif mode == "OFF":
            shown = "Off"
        else:
            shown = "Unknown"

        if match:
            status = f"Connected · Current mode: {shown}"
        elif command == "get":
            status = (
                "Command completed, but no mode response was received."
            )
        else:
            status = f"{command.title()} command completed."

        return {
            "status": status,
            "connected": True,
            "mode": mode,
            "output": output,
        }


class HeadsetController(QObject):
    status_changed = Signal(str)
    battery_changed = Signal(int)
    mode_changed = Signal(str)
    connection_changed = Signal(bool)

    def __init__(self, address=""):
        super().__init__()
        self.address = address
        self.pool = QThreadPool.globalInstance()
        self.busy = False
        self.task = None

    def set_address(self, address):
        self.address = normalize_address(address)
        save_address(self.address)
        self.status_changed.emit("Bluetooth address saved.")
        self.connection_changed.emit(False)
        self.mode_changed.emit("UNKNOWN")

    def run_command(self, command):
        if self.busy:
            self.status_changed.emit(
                "A Bluetooth command is already running…"
            )
            return

        self.busy = True

        messages = {
            "get": "Reading current mode…",
            "refresh": "Checking headphones…",
            "test": "Testing headphones…",
            "poweroff": "Sending power-off command…",
            "anc": "Enabling ANC…",
            "ambient": "Enabling Ambient Aware…",
            "talkthru": "Enabling TalkThru…",
            "off": "Turning ANC off…",
        }

        self.status_changed.emit(
            messages.get(command, f"Running {command}…")
        )

        self.task = Task(self.address, command)
        self.task.signals.finished.connect(self._finished)
        self.pool.start(self.task)

    def refresh(self):
        self.run_command("refresh")

    def test_connection(self):
        self.run_command("test")

    def _finished(self, command, result, error):
        self.busy = False

        if error:
            self.status_changed.emit(error)
            self.connection_changed.emit(False)
            self.mode_changed.emit("UNKNOWN")
            return

        self.status_changed.emit(result["status"])
        self.connection_changed.emit(
            result.get("connected", False)
        )
        self.mode_changed.emit(
            result.get("mode", "UNKNOWN")
        )
        self.battery_changed.emit(get_windows_battery())
