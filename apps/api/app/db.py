from __future__ import annotations

import json
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class CaseStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS image_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    original_filename TEXT NOT NULL,
                    stored_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    media_type TEXT NOT NULL DEFAULT 'image',
                    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self._ensure_column(conn, "image_cases", "user_id", "INTEGER")
            self._ensure_column(conn, "image_cases", "media_type", "TEXT NOT NULL DEFAULT 'image'")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS image_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER NOT NULL,
                    real_score REAL NOT NULL,
                    ai_score REAL NOT NULL,
                    manipulated_score REAL NOT NULL,
                    final_verdict TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    reasons_json TEXT NOT NULL,
                    model_results_json TEXT NOT NULL DEFAULT '[]',
                    report_path TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(case_id) REFERENCES image_cases(id)
                )
                """
            )
            self._ensure_column(conn, "image_analysis", "model_results_json", "TEXT NOT NULL DEFAULT '[]'")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    first_name TEXT NOT NULL DEFAULT '',
                    last_name TEXT NOT NULL DEFAULT '',
                    email TEXT NOT NULL DEFAULT '',
                    phone TEXT NOT NULL DEFAULT '',
                    organization TEXT NOT NULL DEFAULT '',
                    role TEXT NOT NULL DEFAULT '',
                    bio TEXT NOT NULL DEFAULT '',
                    avatar_path TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self._ensure_column(conn, "users", "first_name", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "users", "last_name", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "users", "email", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "users", "phone", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "users", "organization", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "users", "role", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "users", "bio", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "users", "avatar_path", "TEXT")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    expires_at TEXT NOT NULL,
                    ip_address TEXT NOT NULL DEFAULT '',
                    user_agent TEXT NOT NULL DEFAULT '',
                    browser TEXT NOT NULL DEFAULT '',
                    os TEXT NOT NULL DEFAULT '',
                    device_type TEXT NOT NULL DEFAULT 'desktop',
                    device_name TEXT NOT NULL DEFAULT '',
                    login_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    logout_at TEXT,
                    last_active_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            self._ensure_column(conn, "user_sessions", "ip_address", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "user_sessions", "user_agent", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "user_sessions", "browser", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "user_sessions", "os", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "user_sessions", "device_type", "TEXT NOT NULL DEFAULT 'desktop'")
            self._ensure_column(conn, "user_sessions", "device_name", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "user_sessions", "login_at", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "user_sessions", "logout_at", "TEXT")
            self._ensure_column(conn, "user_sessions", "last_active_at", "TEXT NOT NULL DEFAULT ''")

    def create_user(
        self,
        username: str,
        password_hash: str,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        phone: str = "",
        organization: str = "",
        role: str = "",
        bio: str = "",
        avatar_path: str | None = None,
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (
                    username,
                    password_hash,
                    first_name,
                    last_name,
                    email,
                    phone,
                    organization,
                    role,
                    bio,
                    avatar_path
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    username,
                    password_hash,
                    first_name,
                    last_name,
                    email,
                    phone,
                    organization,
                    role,
                    bio,
                    avatar_path,
                ),
            )
            return int(cursor.lastrowid)

    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM users WHERE lower(email) = lower(?) AND email != ''", (email,)).fetchone()
        return dict(row) if row else None

    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT
                    id,
                    username,
                    first_name,
                    last_name,
                    email,
                    phone,
                    organization,
                    role,
                    bio,
                    avatar_path,
                    created_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()
        return dict(row) if row else None

    def update_user_profile(
        self,
        user_id: int,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        organization: str,
        role: str,
        bio: str,
        avatar_path: str | None,
    ) -> dict[str, Any] | None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE users
                SET
                    first_name = ?,
                    last_name = ?,
                    email = ?,
                    phone = ?,
                    organization = ?,
                    role = ?,
                    bio = ?,
                    avatar_path = ?
                WHERE id = ?
                """,
                (
                    first_name,
                    last_name,
                    email,
                    phone,
                    organization,
                    role,
                    bio,
                    avatar_path,
                    user_id,
                ),
            )
        return self.get_user_by_id(user_id)

    def create_session(self, user_id: int, device_info: dict[str, str] | None = None) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
        now = datetime.now(timezone.utc).isoformat()
        device_info = device_info or {}
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO user_sessions (
                    token,
                    user_id,
                    expires_at,
                    ip_address,
                    user_agent,
                    browser,
                    os,
                    device_type,
                    device_name,
                    login_at,
                    last_active_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    token,
                    user_id,
                    expires_at,
                    device_info.get("ip_address", ""),
                    device_info.get("user_agent", ""),
                    device_info.get("browser", ""),
                    device_info.get("os", ""),
                    device_info.get("device_type", "desktop"),
                    device_info.get("device_name", ""),
                    now,
                    now,
                ),
            )
        return token

    def get_user_by_session(self, token: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            conn.execute(
                "UPDATE user_sessions SET last_active_at = ? WHERE token = ? AND expires_at > ? AND logout_at IS NULL",
                (datetime.now(timezone.utc).isoformat(), token, datetime.now(timezone.utc).isoformat()),
            )
            row = conn.execute(
                """
                SELECT
                    u.id,
                    u.username,
                    u.first_name,
                    u.last_name,
                    u.email,
                    u.phone,
                    u.organization,
                    u.role,
                    u.bio,
                    u.avatar_path,
                    u.created_at
                FROM user_sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.token = ? AND s.expires_at > ? AND s.logout_at IS NULL
                """,
                (token, datetime.now(timezone.utc).isoformat()),
            ).fetchone()
        return dict(row) if row else None

    def delete_session(self, token: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE user_sessions SET logout_at = ?, last_active_at = ? WHERE token = ?", (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat(), token))

    def logout_session(self, token: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE user_sessions SET logout_at = ?, last_active_at = ? WHERE token = ?",
                (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat(), token),
            )

    def list_sessions_for_user(self, user_id: int, current_token: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT
                    token,
                    user_id,
                    ip_address,
                    user_agent,
                    browser,
                    os,
                    device_type,
                    device_name,
                    login_at,
                    logout_at,
                    last_active_at,
                    expires_at
                FROM user_sessions
                WHERE user_id = ?
                ORDER BY login_at DESC
                LIMIT 100
                """,
                (user_id,),
            ).fetchall()
        sessions = []
        now = datetime.now(timezone.utc).isoformat()
        for row in rows:
            item = dict(row)
            item["is_current"] = bool(current_token and item["token"] == current_token)
            item["is_active"] = bool(not item.get("logout_at") and str(item.get("expires_at") or "") > now)
            item["token"] = str(item["token"])[:10] + "..."
            sessions.append(item)
        return sessions

    def create_case(
        self,
        original_filename: str,
        stored_path: Path,
        file_hash: str,
        user_id: int,
        media_type: str = "image",
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO image_cases (user_id, original_filename, stored_path, file_hash, status, media_type)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, original_filename, str(stored_path), file_hash, "uploaded", media_type),
            )
            return int(cursor.lastrowid)

    def save_analysis(
        self,
        case_id: int,
        scores: dict[str, float],
        final_verdict: str,
        confidence: str,
        reasons: list[str],
        report_path: Path,
        model_version: str,
        model_results: list[dict[str, Any]] | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO image_analysis (
                    case_id,
                    real_score,
                    ai_score,
                    manipulated_score,
                    final_verdict,
                    confidence,
                    reasons_json,
                    model_results_json,
                    report_path,
                    model_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    case_id,
                    scores["real_score"],
                    scores["ai_score"],
                    scores["manipulated_score"],
                    final_verdict,
                    confidence,
                    json.dumps(reasons, ensure_ascii=False),
                    json.dumps(model_results or [], ensure_ascii=False),
                    str(report_path),
                    model_version,
                ),
            )
            conn.execute("UPDATE image_cases SET status = ? WHERE id = ?", ("analyzed", case_id))

    def get_case(self, case_id: int, user_id: int | None = None) -> dict[str, Any] | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            params: tuple[Any, ...] = (case_id,)
            user_filter = ""
            if user_id is not None:
                user_filter = "AND c.user_id = ?"
                params = (case_id, user_id)
            row = conn.execute(
                f"""
                SELECT
                    c.id,
                    c.user_id,
                    c.original_filename,
                    c.stored_path,
                    c.file_hash,
                    c.status,
                    c.media_type,
                    c.uploaded_at,
                    a.real_score,
                    a.ai_score,
                    a.manipulated_score,
                    a.final_verdict,
                    a.confidence,
                    a.model_results_json,
                    a.report_path,
                    a.model_version
                FROM image_cases c
                LEFT JOIN image_analysis a ON a.case_id = c.id
                WHERE c.id = ? {user_filter}
                ORDER BY a.id DESC
                LIMIT 1
                """,
                params,
            ).fetchone()

        return dict(row) if row else None

    def list_cases(self, limit: int = 50, user_id: int | None = None) -> list[dict[str, Any]]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            params: tuple[Any, ...] = (limit,)
            user_filter = ""
            if user_id is not None:
                user_filter = "WHERE c.user_id = ?"
                params = (user_id, limit)
            else:
                user_filter = ""
            rows = conn.execute(
                f"""
                WITH latest_analysis AS (
                    SELECT *
                    FROM image_analysis
                    WHERE id IN (
                        SELECT MAX(id) FROM image_analysis GROUP BY case_id
                    )
                )
                SELECT
                    c.id,
                    c.user_id,
                    c.original_filename,
                    c.stored_path,
                    c.file_hash,
                    c.status,
                    c.media_type,
                    c.uploaded_at,
                    a.real_score,
                    a.ai_score,
                    a.manipulated_score,
                    a.final_verdict,
                    a.confidence,
                    a.model_results_json,
                    a.report_path,
                    a.model_version
                FROM image_cases c
                LEFT JOIN latest_analysis a ON a.case_id = c.id
                {user_filter}
                ORDER BY c.id DESC
                LIMIT ?
                """,
                params,
            ).fetchall()

        return [dict(row) for row in rows]

    def stats_for_user(self, user_id: int) -> dict[str, Any]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT
                    COUNT(c.id) AS total_cases,
                    SUM(CASE WHEN a.ai_score >= 0.55 OR a.manipulated_score >= 0.55 THEN 1 ELSE 0 END) AS flagged_cases,
                    AVG(a.real_score) AS avg_real_score
                FROM image_cases c
                LEFT JOIN image_analysis a ON a.case_id = c.id
                WHERE c.user_id = ?
                """,
                (user_id,),
            ).fetchone()
        stats = dict(row) if row else {}
        return {
            "total_cases": int(stats.get("total_cases") or 0),
            "flagged_cases": int(stats.get("flagged_cases") or 0),
            "avg_real_score": float(stats.get("avg_real_score") or 0.0),
        }

    def _ensure_column(self, conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
        columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in columns:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)




