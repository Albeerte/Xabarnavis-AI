#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
API_DIR = BASE_DIR / "apps" / "api"
FRONTEND_DIR = BASE_DIR / "apps" / "web"
DEFAULT_FRONTEND_HOST = "127.0.0.1"
DEFAULT_FRONTEND_PORT = "8000"
DEFAULT_API_HOST = "127.0.0.1"
DEFAULT_API_PORT = "8001"
DEFAULT_ADMIN_HOST = "127.0.0.1"
DEFAULT_ADMIN_PORT = "8000"
LEGACY_ADMIN_PORT = "8002"


def add_local_runtime_to_path() -> None:
    """Prefer the bundled Codex Node runtime when global node is unavailable."""    
    bundled_root = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies"
    candidates = [
        bundled_root / "node" / "bin",
        bundled_root / "bin",
    ]
    existing = [str(path) for path in candidates if path.exists()]
    if existing:
        os.environ["PATH"] = os.pathsep.join(existing + [os.environ.get("PATH", "")])


def parse_addrport(value: str | None) -> tuple[str, str]:
    if not value:
        return DEFAULT_FRONTEND_HOST, DEFAULT_FRONTEND_PORT
    if ":" in value:
        host, port = value.rsplit(":", 1)
        return host or DEFAULT_FRONTEND_HOST, port or DEFAULT_FRONTEND_PORT
    return DEFAULT_FRONTEND_HOST, value


def stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "nt":
            process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            process.terminate()
        process.wait(timeout=8)
    except Exception:
        process.kill()


def find_running_project_server_pids() -> list[int]:
    """Find previous dev servers that were started from this project folder."""
    current_pid = os.getpid()
    if os.name == "nt":
        script = f"""
$base = {json.dumps(str(BASE_DIR))}
$current = {current_pid}
Get-CimInstance Win32_Process | Where-Object {{
  $_.ProcessId -ne $current -and
  $_.CommandLine -and
  $_.CommandLine.Contains($base) -and
  (
    $_.CommandLine -match 'next.*start-server' -or
    $_.CommandLine -match 'uvicorn.*app.main' -or
    $_.CommandLine -match 'manage.py.*runserver'
  )
}} | ForEach-Object {{ $_.ProcessId }}
"""
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            check=False,
        )
        return [int(line) for line in result.stdout.splitlines() if line.strip().isdigit()]

    result = subprocess.run(
        ["pgrep", "-f", str(BASE_DIR)],
        capture_output=True,
        text=True,
        check=False,
    )
    pids: list[int] = []
    for line in result.stdout.splitlines():
        if not line.strip().isdigit():
            continue
        pid = int(line)
        if pid != current_pid:
            pids.append(pid)
    return pids


def find_listening_port_pids(ports: list[str]) -> list[int]:
    current_pid = os.getpid()
    if os.name == "nt":
        result = subprocess.run(
            ["netstat", "-ano", "-p", "tcp"],
            capture_output=True,
            text=True,
            check=False,
        )
        pids: set[int] = set()
        wanted_ports = {str(port) for port in ports}
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 5 or parts[0].upper() != "TCP" or parts[3].upper() != "LISTENING":
                continue
            local_address = parts[1]
            pid_text = parts[-1]
            port = local_address.rsplit(":", 1)[-1]
            if port in wanted_ports and pid_text.isdigit():
                pid = int(pid_text)
                if pid not in {0, current_pid}:
                    pids.add(pid)
        return sorted(pids)

    result = subprocess.run(
        ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"],
        capture_output=True,
        text=True,
        check=False,
    )
    pids = set()
    wanted_ports = {str(port) for port in ports}
    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 9 or not parts[1].isdigit():
            continue
        port = parts[-1].rsplit(":", 1)[-1]
        if port in wanted_ports:
            pid = int(parts[1])
            if pid != current_pid:
                pids.add(pid)
    return sorted(pids)


def stop_existing_project_servers(ports: list[str] | None = None, verbose: bool = True) -> None:
    pids = set(find_running_project_server_pids())
    if ports:
        pids.update(find_listening_port_pids(ports))
    if not pids:
        return

    if verbose:
        print("Stopping existing Xabarnavis dev servers:", ", ".join(str(pid) for pid in sorted(pids)))

    for pid in sorted(pids):
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, capture_output=True)
        else:
            subprocess.run(["kill", "-TERM", str(pid)], check=False, capture_output=True)


def django_admin_command(args: list[str]) -> int:
    admin_manage = BASE_DIR / "django_admin" / "manage.py"
    if not admin_manage.exists():
        print("Django admin project not found:", admin_manage)
        return 1
    command = [sys.executable, str(admin_manage), *args]
    return subprocess.call(command, cwd=BASE_DIR)


def runserver(addrport: str | None, api_addrport: str | None, frontend_only: bool) -> int:
    add_local_runtime_to_path()
    host, port = parse_addrport(addrport)
    api_host, api_port = parse_addrport(api_addrport or f"{DEFAULT_API_HOST}:{DEFAULT_API_PORT}")
    stop_existing_project_servers([port, api_port])

    if not FRONTEND_DIR.exists():
        print("frontend folder not found. Expected:", FRONTEND_DIR)
        return 1

    next_bin = FRONTEND_DIR / "node_modules" / ".bin" / ("next.cmd" if os.name == "nt" else "next")
    if not next_bin.exists():
        print("Next.js dependencies are missing.")
        print("Run this once:")
        print("  cd apps\\web")
        print("  pnpm install")
        return 1

    processes: list[tuple[str, subprocess.Popen[bytes]]] = []
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0

    print("Starting Xabarnavis AI full website...")
    print(f"Website: http://{host}:{port}")
    if frontend_only:
        print("API: disabled")
    else:
        print(f"API:     http://{api_host}:{api_port}")
    print("Stop all servers: Ctrl+C")
    print()

    try:
        if not frontend_only:
            api_command = [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                api_host,
                "--port",
                api_port,
            ]
            processes.append(
                (
                    "api",
                    subprocess.Popen(
                        api_command,
                        cwd=API_DIR,
                        creationflags=creationflags,
                    ),
                )
            )

        frontend_env = os.environ.copy()
        frontend_env["XABARNAVIS_API_URL"] = f"http://{api_host}:{api_port}"
        frontend_command = [str(next_bin), "dev", "--webpack", "--hostname", host, "--port", port]
        processes.append(
            (
                "website",
                subprocess.Popen(
                    frontend_command,
                    cwd=FRONTEND_DIR,
                    env=frontend_env,
                    creationflags=creationflags,
                ),
            )
        )

        while True:
            for name, process in processes:
                exit_code = process.poll()
                if exit_code is not None:
                    print(f"\n{name} server stopped with exit code {exit_code}.")
                    return exit_code
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping Xabarnavis AI servers...")
        return 0
    finally:
        for _, process in reversed(processes):
            stop_process(process)


def main() -> int:
    parser = argparse.ArgumentParser(description="Xabarnavis AI project manager")
    subparsers = parser.add_subparsers(dest="command")

    runserver_parser = subparsers.add_parser("runserver", help="Start the full Xabarnavis AI website")
    runserver_parser.add_argument(
        "addrport",
        nargs="?",
        help="Optional website port or host:port, for example 8000 or 127.0.0.1:8000",
    )
    runserver_parser.add_argument(
        "--api",
        default=f"{DEFAULT_API_HOST}:{DEFAULT_API_PORT}",
        help="Optional API host:port. Default: 127.0.0.1:8001",
    )
    runserver_parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="Start only the Next.js website without the FastAPI backend.",
    )
    website_parser = subparsers.add_parser("website", help="Start the full Xabarnavis AI website")
    website_parser.add_argument(
        "addrport",
        nargs="?",
        help="Optional website port or host:port, for example 8000 or 127.0.0.1:8000",
    )
    website_parser.add_argument(
        "--api",
        default=f"{DEFAULT_API_HOST}:{DEFAULT_API_PORT}",
        help="Optional API host:port. Default: 127.0.0.1:8001",
    )
    website_parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="Start only the Next.js website without the FastAPI backend.",
    )
    subparsers.add_parser("stopserver", help="Stop running Xabarnavis dev servers for this project")
    adminserver_parser = subparsers.add_parser("adminserver", help="Start the Django admin panel")
    adminserver_parser.add_argument(
        "addrport",
        nargs="?",
        default=f"{DEFAULT_ADMIN_HOST}:{DEFAULT_ADMIN_PORT}",
        help="Optional Django admin host:port. Default: 127.0.0.1:8000",
    )
    admin_parser = subparsers.add_parser("django", help="Pass a command to the Django admin project")
    admin_parser.add_argument("django_args", nargs=argparse.REMAINDER)

    args = parser.parse_args()
    if args.command == "runserver":
        return runserver(args.addrport, args.api, args.frontend_only)
    if args.command == "website":
        return runserver(args.addrport, args.api, args.frontend_only)
    if args.command == "stopserver":
        stop_existing_project_servers([DEFAULT_FRONTEND_PORT, DEFAULT_API_PORT, LEGACY_ADMIN_PORT])
        return 0
    if args.command == "adminserver":
        return django_admin_command(["runserver", args.addrport])
    if args.command == "django":
        django_args = args.django_args or ["help"]
        return django_admin_command(django_args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
