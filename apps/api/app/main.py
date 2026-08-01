import json
import os
import re
import sqlite3
from pathlib import Path
from sqlite3 import IntegrityError
from uuid import uuid4

from fastapi import Body, Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.auth import clear_session_cookie, hash_password, require_user_from_store, session_token_cookie, set_session_cookie, verify_password
from app.db import CaseStore
from app.schemas import AnalysisResponse, CaseListResponse, CaseSummary, MediaAnalysisResponse, ModelListResponse
from app.services.analyzer import ImageAnalyzer
from app.services.audio_visuals import create_audio_artifacts
from app.services.docx_report import load_report, write_docx_report
from app.services.media_analyzer import MediaAnalyzer
from app.services.model_registry import ModelRegistry, models_as_dicts, write_external_model_registry


PROJECT_ROOT = Path(__file__).resolve().parents[3]
API_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = PROJECT_ROOT / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
REPORT_DIR = STORAGE_DIR / "reports"
PROFILE_DIR = STORAGE_DIR / "profiles"
DB_PATH = STORAGE_DIR / "xabarnavis.sqlite3"
STATIC_DIR = API_DIR / "static"
EXTERNAL_MODELS_DIR = PROJECT_ROOT / "artifacts" / "models" / "external"

app = FastAPI(
    title="Xabarnavis AI Local Forensic API",
    version="0.1.0",
    description="Local forensic pipeline for real, AI-generated, and manipulated image analysis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = CaseStore(DB_PATH)
analyzer = ImageAnalyzer(UPLOAD_DIR, REPORT_DIR, store)
media_analyzer = MediaAnalyzer(UPLOAD_DIR, REPORT_DIR, store)
model_registry = ModelRegistry()


@app.on_event("startup")
def startup() -> None:
    STORAGE_DIR.mkdir(exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    EXTERNAL_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    store.init()
    sync_model_admin_settings()
    write_external_model_registry(EXTERNAL_MODELS_DIR / "registry.json", model_registry.list_models())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/xabarnavis-logo.png")
def xabarnavis_logo() -> FileResponse:
    logo_path = PROJECT_ROOT / "apps" / "web" / "public" / "xabarnavis-logo.png"
    if not logo_path.is_file():
        raise HTTPException(status_code=404, detail="Logo not found.")
    return FileResponse(logo_path, media_type="image/png")


def current_user(token: str | None = Depends(session_token_cookie)) -> dict:
    return require_user_from_store(store, token)


def is_admin_user(user: dict) -> bool:
    role = str(user.get("role") or "").strip().lower()
    username = str(user.get("username") or "").strip().lower()
    return username == "admin" or role in {"admin", "superadmin"}


def current_admin(user: dict = Depends(current_user)) -> dict:
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user


def clean_form_text(value: str | None, max_length: int = 240) -> str:
    return (value or "").strip()[:max_length]


def ensure_model_admin_settings() -> None:
    with store._connect() as conn:
        ensure_user_admin_columns(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS model_admin_settings (
                model_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                family TEXT NOT NULL DEFAULT '',
                media_type TEXT NOT NULL DEFAULT '',
                status_snapshot TEXT NOT NULL DEFAULT '',
                purpose TEXT NOT NULL DEFAULT '',
                repository TEXT NOT NULL DEFAULT '',
                local_path TEXT NOT NULL DEFAULT '',
                sort_order INTEGER NOT NULL DEFAULT 1000,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_user_id INTEGER,
                actor_username TEXT NOT NULL DEFAULT '',
                action TEXT NOT NULL,
                target_type TEXT NOT NULL DEFAULT '',
                target_id TEXT NOT NULL DEFAULT '',
                details_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_user_id INTEGER,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                audience TEXT NOT NULL DEFAULT 'all',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def ensure_user_admin_columns(conn: sqlite3.Connection) -> None:
    columns = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "is_active" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
    if "is_blocked" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN is_blocked INTEGER NOT NULL DEFAULT 0")


def write_admin_audit(user: dict, action: str, target_type: str = "", target_id: object = "", details: dict | None = None) -> None:
    ensure_model_admin_settings()
    with store._connect() as conn:
        conn.execute(
            """
            INSERT INTO admin_audit_logs (actor_user_id, actor_username, action, target_type, target_id, details_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(user.get("id") or 0),
                str(user.get("username") or ""),
                action,
                target_type,
                str(target_id),
                json.dumps(details or {}, ensure_ascii=False),
            ),
        )


def infer_model_media_type(model_id: str, family: str, local_path: str | None) -> str:
    text = " ".join([model_id, family, local_path or ""]).lower()
    if "audio" in text or "jabberjay" in text or "rawgat" in text or "spectra" in text:
        return "audio"
    if "video" in text or "genconvit" in text or "deepfakebench" in text or "faceforensics" in text:
        return "video"
    if "text" in text:
        return "text"
    return "photo"


def sync_model_admin_settings() -> dict[str, int]:
    ensure_model_admin_settings()
    previous = os.environ.get("XABARNAVIS_IGNORE_MODEL_ADMIN_SETTINGS")
    os.environ["XABARNAVIS_IGNORE_MODEL_ADMIN_SETTINGS"] = "1"
    try:
        registered_models = model_registry.list_models()
    finally:
        if previous is None:
            os.environ.pop("XABARNAVIS_IGNORE_MODEL_ADMIN_SETTINGS", None)
        else:
            os.environ["XABARNAVIS_IGNORE_MODEL_ADMIN_SETTINGS"] = previous

    created = 0
    updated = 0
    with store._connect() as conn:
        for index, model in enumerate(registered_models, start=1):
            media_type = infer_model_media_type(model.id, model.family, model.local_path)
            existing = conn.execute(
                "SELECT 1 FROM model_admin_settings WHERE model_id = ?",
                (model.id,),
            ).fetchone()
            if existing is None:
                conn.execute(
                    """
                    INSERT INTO model_admin_settings (
                        model_id, display_name, enabled, family, media_type, status_snapshot,
                        purpose, repository, local_path, sort_order
                    )
                    VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        model.id,
                        model.name,
                        model.family,
                        media_type,
                        model.status,
                        model.purpose,
                        model.repository or "",
                        model.local_path or "",
                        index,
                    ),
                )
                created += 1
            else:
                conn.execute(
                    """
                    UPDATE model_admin_settings
                    SET family = ?, media_type = ?, status_snapshot = ?, purpose = ?,
                        repository = ?, local_path = ?, sort_order = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE model_id = ?
                    """,
                    (
                        model.family,
                        media_type,
                        model.status,
                        model.purpose,
                        model.repository or "",
                        model.local_path or "",
                        index,
                        model.id,
                    ),
                )
                updated += 1
    return {"created": created, "updated": updated}


def list_model_admin_settings() -> list[dict]:
    sync_model_admin_settings()
    with store._connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT model_id, display_name, enabled, family, media_type, status_snapshot,
                   purpose, repository, local_path, sort_order, created_at, updated_at
            FROM model_admin_settings
            ORDER BY sort_order ASC, model_id ASC
            """
        ).fetchall()
    return [dict(row) | {"enabled": bool(row["enabled"])} for row in rows]


def list_admin_users() -> list[dict]:
    ensure_model_admin_settings()
    with store._connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                u.id, u.username, u.first_name, u.last_name, u.email, u.phone,
                u.organization, u.role, u.bio, u.avatar_path, u.created_at,
                u.is_active, u.is_blocked,
                COUNT(DISTINCT c.id) AS case_count,
                COUNT(DISTINCT s.token) AS session_count
            FROM users u
            LEFT JOIN image_cases c ON c.user_id = u.id
            LEFT JOIN user_sessions s ON s.user_id = u.id
            GROUP BY u.id
            ORDER BY u.id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def list_admin_reports(limit: int = 300) -> list[dict]:
    with store._connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            WITH latest_analysis AS (
                SELECT *
                FROM image_analysis
                WHERE id IN (SELECT MAX(id) FROM image_analysis GROUP BY case_id)
            )
            SELECT
                c.id, c.user_id, u.username, c.original_filename, c.stored_path,
                c.file_hash, c.status, c.media_type, c.uploaded_at,
                a.real_score, a.ai_score, a.manipulated_score, a.final_verdict,
                a.confidence, a.model_results_json, a.report_path, a.model_version
            FROM image_cases c
            LEFT JOIN users u ON u.id = c.user_id
            LEFT JOIN latest_analysis a ON a.case_id = c.id
            ORDER BY c.id DESC
            LIMIT ?
            """,
            (max(1, min(limit, 500)),),
        ).fetchall()
    return [dict(row) for row in rows]


def list_admin_audit_logs(limit: int = 300) -> list[dict]:
    ensure_model_admin_settings()
    with store._connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, actor_user_id, actor_username, action, target_type, target_id, details_json, created_at
            FROM admin_audit_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (max(1, min(limit, 500)),),
        ).fetchall()
    return [dict(row) for row in rows]


def parse_device_info(request: Request) -> dict[str, str]:
    user_agent = request.headers.get("user-agent", "")
    forwarded_for = request.headers.get("x-forwarded-for", "")
    ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "")
    lower = user_agent.lower()

    if "edg/" in lower:
        browser = "Microsoft Edge"
    elif "chrome/" in lower and "chromium" not in lower:
        browser = "Chrome"
    elif "firefox/" in lower:
        browser = "Firefox"
    elif "safari/" in lower and "chrome/" not in lower:
        browser = "Safari"
    elif "opr/" in lower or "opera" in lower:
        browser = "Opera"
    else:
        browser = "Unknown browser"

    if "windows" in lower:
        os_name = "Windows"
    elif "android" in lower:
        os_name = "Android"
    elif "iphone" in lower or "ipad" in lower or "ios" in lower:
        os_name = "iOS"
    elif "mac os" in lower or "macintosh" in lower:
        os_name = "macOS"
    elif "linux" in lower:
        os_name = "Linux"
    else:
        os_name = "Unknown OS"

    if "ipad" in lower or "tablet" in lower:
        device_type = "tablet"
    elif "mobile" in lower or "iphone" in lower or "android" in lower:
        device_type = "mobile"
    else:
        device_type = "desktop"

    device_name = f"{browser} on {os_name}"
    return {
        "ip_address": ip_address,
        "user_agent": user_agent[:1000],
        "browser": browser,
        "os": os_name,
        "device_type": device_type,
        "device_name": device_name,
    }


async def save_profile_avatar(avatar: UploadFile | None) -> str | None:
    if avatar is None or not avatar.filename:
        return None
    if not avatar.content_type or not avatar.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Profile image must be an image file.")

    suffix = Path(avatar.filename).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".png"

    target = PROFILE_DIR / f"{uuid4().hex}{suffix}"
    contents = await avatar.read()
    if len(contents) > 3 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Profile image must be 3MB or smaller.")
    target.write_bytes(contents)
    return f"/api/profile/avatar/{target.name}"


@app.post("/api/auth/register")
async def register(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(default=""),
    last_name: str = Form(default=""),
    email: str = Form(default=""),
    phone: str = Form(default=""),
    organization: str = Form(default=""),
    role: str = Form(default=""),
    bio: str = Form(default=""),
    avatar: UploadFile | None = File(default=None),
) -> dict[str, object]:
    username = username.strip().lower()
    if not re.fullmatch(r"[a-z0-9._-]{3,40}", username):
        raise HTTPException(
            status_code=400,
            detail="Username must be 3-40 characters and use only letters, numbers, dots, hyphens, or underscores.",
        )
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    normalized_email = clean_form_text(email, 160).lower()
    if normalized_email and store.get_user_by_email(normalized_email):
        raise HTTPException(status_code=409, detail="Email already exists.")
    avatar_path = await save_profile_avatar(avatar)
    try:
        user_id = store.create_user(
            username,
            hash_password(password),
            clean_form_text(first_name, 80),
            clean_form_text(last_name, 80),
            normalized_email,
            clean_form_text(phone, 80),
            clean_form_text(organization, 160),
            clean_form_text(role, 120),
            clean_form_text(bio, 800),
            avatar_path,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Username already exists.") from None
    token = store.create_session(user_id, parse_device_info(request))
    set_session_cookie(response, token)
    return {"user": store.get_user_by_id(user_id)}


@app.get("/api/auth/google")
def google_auth_unconfigured() -> dict[str, str]:
    return {
        "status": "not_configured",
        "detail": "Google login uchun GOOGLE_CLIENT_ID va GOOGLE_CLIENT_SECRET sozlanishi kerak.",
    }


@app.post("/api/auth/login")
def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)) -> dict[str, object]:
    user = store.get_user_by_username(username.strip().lower())
    if user is None and "@" in username:
        user = store.get_user_by_email(username.strip().lower())
    if user is None or not verify_password(password, str(user["password_hash"])):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = store.create_session(int(user["id"]), parse_device_info(request))
    set_session_cookie(response, token)
    return {"user": store.get_user_by_id(int(user["id"]))}


@app.post("/api/auth/logout")
def logout(response: Response, token: str | None = Depends(session_token_cookie)) -> dict[str, str]:
    if token:
        store.logout_session(token)
    clear_session_cookie(response)
    return {"status": "ok"}


@app.get("/api/auth/me")
def me(user: dict = Depends(current_user)) -> dict[str, object]:
    return {"user": user}


@app.get("/api/devices")
def devices(user: dict = Depends(current_user), token: str | None = Depends(session_token_cookie)) -> dict[str, object]:
    sessions = store.list_sessions_for_user(int(user["id"]), token)
    return {"devices": sessions}


@app.get("/api/login-history")
def login_history(user: dict = Depends(current_user), token: str | None = Depends(session_token_cookie)) -> dict[str, object]:
    sessions = store.list_sessions_for_user(int(user["id"]), token)
    return {"sessions": sessions}


@app.post("/api/auth/sessions/{session_token_prefix}/logout")
def logout_device(session_token_prefix: str, user: dict = Depends(current_user), token: str | None = Depends(session_token_cookie)) -> dict[str, str]:
    sessions = store.list_sessions_for_user(int(user["id"]), token)
    target = next((item for item in sessions if str(item.get("token", "")).startswith(session_token_prefix)), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    if target.get("is_current"):
        raise HTTPException(status_code=400, detail="Current session cannot be revoked here. Use logout.")
    # token is masked in list output, so use a prefix update guarded by user id.
    with store._connect() as conn:  # local admin action for this SQLite-backed app
        conn.execute(
            "UPDATE user_sessions SET logout_at = CURRENT_TIMESTAMP, last_active_at = CURRENT_TIMESTAMP WHERE user_id = ? AND token LIKE ?",
            (int(user["id"]), f"{session_token_prefix}%"),
        )
    return {"status": "ok"}


@app.post("/api/auth/profile")
async def update_profile(
    first_name: str = Form(default=""),
    last_name: str = Form(default=""),
    email: str = Form(default=""),
    phone: str = Form(default=""),
    organization: str = Form(default=""),
    role: str = Form(default=""),
    bio: str = Form(default=""),
    avatar: UploadFile | None = File(default=None),
    user: dict = Depends(current_user),
) -> dict[str, object]:
    avatar_path = await save_profile_avatar(avatar) or user.get("avatar_path")
    updated_user = store.update_user_profile(
        int(user["id"]),
        clean_form_text(first_name, 80),
        clean_form_text(last_name, 80),
        clean_form_text(email, 160),
        clean_form_text(phone, 80),
        clean_form_text(organization, 160),
        clean_form_text(role, 120),
        clean_form_text(bio, 800),
        str(avatar_path) if avatar_path else None,
    )
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"user": updated_user}


@app.get("/api/profile/avatar/{filename}")
def profile_avatar(filename: str) -> FileResponse:
    avatar_path = (PROFILE_DIR / filename).resolve()
    if not avatar_path.is_file() or PROFILE_DIR.resolve() not in avatar_path.parents:
        raise HTTPException(status_code=404, detail="Profile image not found.")
    return FileResponse(avatar_path)


@app.get("/api/stats")
def stats(user: dict = Depends(current_user)) -> dict[str, object]:
    return store.stats_for_user(int(user["id"]))


@app.get("/api/models", response_model=ModelListResponse)
def list_models() -> ModelListResponse:
    return ModelListResponse(models=models_as_dicts(model_registry.list_models()))


@app.get("/api/admin/overview")
def admin_overview(user: dict = Depends(current_admin)) -> dict[str, object]:
    users = list_admin_users()
    reports = list_admin_reports(300)
    models = list_model_admin_settings()
    return {
        "models": models,
        "users": users,
        "reports": reports,
        "stats": {
            "models": len(models),
            "enabled_models": sum(1 for item in models if item["enabled"]),
            "users": len(users),
            "reports": len(reports),
        },
    }


@app.get("/api/admin/stats")
def admin_stats(user: dict = Depends(current_admin)) -> dict[str, object]:
    users = list_admin_users()
    reports = list_admin_reports(500)
    models = list_model_admin_settings()
    blocked_users = sum(1 for item in users if item.get("is_blocked"))
    return {
        "models": len(models),
        "enabled_models": sum(1 for item in models if item["enabled"]),
        "users": len(users),
        "active_users": sum(1 for item in users if item.get("is_active") and not item.get("is_blocked")),
        "blocked_users": blocked_users,
        "reports": len(reports),
        "image_reports": sum(1 for item in reports if item.get("media_type") == "image"),
        "video_reports": sum(1 for item in reports if item.get("media_type") == "video"),
        "audio_reports": sum(1 for item in reports if item.get("media_type") == "audio"),
        "text_reports": sum(1 for item in reports if item.get("media_type") == "text"),
    }


@app.get("/api/admin/health")
def admin_health(user: dict = Depends(current_admin)) -> dict[str, object]:
    return {
        "status": "ok",
        "database": DB_PATH.exists(),
        "reports_dir": REPORT_DIR.exists(),
        "uploads_dir": UPLOAD_DIR.exists(),
        "models": len(list_model_admin_settings()),
    }


@app.post("/api/admin/models/sync")
def admin_sync_models(user: dict = Depends(current_admin)) -> dict[str, object]:
    result = sync_model_admin_settings()
    write_admin_audit(user, "models.sync", "model_admin_settings", "*", result)
    return {"status": "ok", **result, "models": list_model_admin_settings()}


@app.patch("/api/admin/models/{model_id}")
def admin_update_model(model_id: str, payload: dict = Body(...), user: dict = Depends(current_admin)) -> dict[str, object]:
    ensure_model_admin_settings()
    updates: dict[str, object] = {}
    if "display_name" in payload:
        name = clean_form_text(str(payload.get("display_name") or ""), 255)
        if not name:
            raise HTTPException(status_code=400, detail="Model name cannot be empty.")
        updates["display_name"] = name
    if "enabled" in payload:
        updates["enabled"] = 1 if bool(payload["enabled"]) else 0
    if "sort_order" in payload:
        updates["sort_order"] = int(payload["sort_order"])
    if not updates:
        raise HTTPException(status_code=400, detail="No supported fields were provided.")

    with store._connect() as conn:
        exists = conn.execute("SELECT 1 FROM model_admin_settings WHERE model_id = ?", (model_id,)).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="Model setting not found.")
        assignments = ", ".join(f"{key} = ?" for key in updates)
        conn.execute(
            f"UPDATE model_admin_settings SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE model_id = ?",
            (*updates.values(), model_id),
        )
    write_admin_audit(user, "model.update", "model", model_id, updates)
    return {"status": "ok", "models": list_model_admin_settings()}


@app.get("/api/admin/users")
def admin_users(user: dict = Depends(current_admin)) -> dict[str, object]:
    return {"users": list_admin_users()}


@app.post("/api/admin/users")
def admin_create_user(payload: dict = Body(...), user: dict = Depends(current_admin)) -> dict[str, object]:
    username = clean_form_text(str(payload.get("username") or ""), 80).lower()
    password = str(payload.get("password") or "")
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    email = clean_form_text(str(payload.get("email") or ""), 160)
    if email and store.get_user_by_email(email):
        raise HTTPException(status_code=409, detail="Email already exists.")
    try:
        user_id = store.create_user(
            username=username,
            password_hash=hash_password(password),
            first_name=clean_form_text(str(payload.get("first_name") or ""), 80),
            last_name=clean_form_text(str(payload.get("last_name") or ""), 80),
            email=email,
            phone=clean_form_text(str(payload.get("phone") or ""), 80),
            organization=clean_form_text(str(payload.get("organization") or ""), 160),
            role=clean_form_text(str(payload.get("role") or ""), 120),
            bio=clean_form_text(str(payload.get("bio") or ""), 800),
            avatar_path=None,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Username already exists.") from None
    write_admin_audit(user, "user.create", "user", user_id, {"username": username, "role": payload.get("role")})
    return {"status": "ok", "users": list_admin_users()}


@app.patch("/api/admin/users/{user_id}")
def admin_update_user(user_id: int, payload: dict = Body(...), user: dict = Depends(current_admin)) -> dict[str, object]:
    limits = {
        "first_name": 80,
        "last_name": 80,
        "email": 160,
        "phone": 80,
        "organization": 160,
        "role": 120,
        "bio": 800,
    }
    updates = {key: clean_form_text(str(payload.get(key) or ""), limit) for key, limit in limits.items() if key in payload}
    if "is_active" in payload:
        updates["is_active"] = 1 if bool(payload["is_active"]) else 0
        if bool(payload["is_active"]):
            updates["is_blocked"] = 0
    if "is_blocked" in payload:
        updates["is_blocked"] = 1 if bool(payload["is_blocked"]) else 0
        if bool(payload["is_blocked"]):
            updates["is_active"] = 0
    if not updates:
        raise HTTPException(status_code=400, detail="No supported fields were provided.")
    with store._connect() as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="User not found.")
        assignments = ", ".join(f"{key} = ?" for key in updates)
        conn.execute(f"UPDATE users SET {assignments} WHERE id = ?", (*updates.values(), user_id))
        if updates.get("is_blocked"):
            conn.execute("UPDATE user_sessions SET logout_at = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
    write_admin_audit(user, "user.update", "user", user_id, updates)
    return {"status": "ok", "users": list_admin_users()}


@app.delete("/api/admin/users/{user_id}")
def admin_delete_user(user_id: int, user: dict = Depends(current_admin)) -> dict[str, object]:
    if user_id == int(user["id"]):
        raise HTTPException(status_code=400, detail="Current user cannot be deleted.")
    with store._connect() as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="User not found.")
        conn.execute("UPDATE image_cases SET user_id = NULL WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    write_admin_audit(user, "user.delete", "user", user_id)
    return {"status": "ok", "users": list_admin_users(), "reports": list_admin_reports(300)}


@app.get("/api/admin/reports")
def admin_reports(limit: int = 300, user: dict = Depends(current_admin)) -> dict[str, object]:
    return {"reports": list_admin_reports(limit)}


@app.delete("/api/admin/reports/{case_id}")
def admin_delete_report(case_id: int, user: dict = Depends(current_admin)) -> dict[str, object]:
    with store._connect() as conn:
        exists = conn.execute("SELECT 1 FROM image_cases WHERE id = ?", (case_id,)).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="Report not found.")
        conn.execute("DELETE FROM image_analysis WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM reports WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM forensic_features WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM manipulation_masks WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM image_cases WHERE id = ?", (case_id,))
    write_admin_audit(user, "report.delete", "report", case_id)
    return {"status": "ok", "reports": list_admin_reports(300)}


@app.get("/api/admin/audit-logs")
def admin_audit_logs(limit: int = 300, user: dict = Depends(current_admin)) -> dict[str, object]:
    return {"logs": list_admin_audit_logs(limit)}


@app.post("/api/admin/broadcast")
def admin_broadcast(payload: dict = Body(...), user: dict = Depends(current_admin)) -> dict[str, object]:
    title = clean_form_text(str(payload.get("title") or ""), 160)
    message = clean_form_text(str(payload.get("message") or ""), 1200)
    audience = clean_form_text(str(payload.get("audience") or "all"), 80) or "all"
    if not title or not message:
        raise HTTPException(status_code=400, detail="Title and message are required.")
    ensure_model_admin_settings()
    with store._connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO admin_broadcasts (actor_user_id, title, message, audience)
            VALUES (?, ?, ?, ?)
            """,
            (int(user["id"]), title, message, audience),
        )
        broadcast_id = int(cursor.lastrowid)
    write_admin_audit(user, "broadcast.create", "broadcast", broadcast_id, {"title": title, "audience": audience})
    return {"status": "ok", "broadcast_id": broadcast_id}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    selected_models: list[str] = Form(default=[]),
    deep_scan: bool = Form(default=True),
    image_description: str = Form(default=""),
    user: dict = Depends(current_user),
) -> AnalysisResponse:
    model_ids = analyzer.model_registry.deep_scan_ids() if deep_scan else selected_models or None
    return await analyzer.analyze_upload(file, model_ids, image_description.strip() or None, int(user["id"]))


@app.post("/api/analyze/audio", response_model=MediaAnalysisResponse)
async def analyze_audio(file: UploadFile = File(...), user: dict = Depends(current_user)) -> MediaAnalysisResponse:
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio uploads are supported.")
    return await media_analyzer.analyze_audio(file, int(user["id"]))


@app.post("/api/analyze/video", response_model=MediaAnalysisResponse)
async def analyze_video(file: UploadFile = File(...), user: dict = Depends(current_user)) -> MediaAnalysisResponse:
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video uploads are supported.")
    return await media_analyzer.analyze_video(file, int(user["id"]))


@app.post("/api/analyze/text", response_model=MediaAnalysisResponse)
def analyze_text(
    text: str = Form(...),
    title: str = Form(default="text-evidence.txt"),
    user: dict = Depends(current_user),
) -> MediaAnalysisResponse:
    if len(text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Text must be at least 20 characters.")
    return media_analyzer.analyze_text(text.strip(), int(user["id"]), title.strip() or "text-evidence.txt")


@app.get("/api/cases/{case_id}", response_model=CaseSummary)
def get_case(case_id: int, user: dict = Depends(current_user)) -> CaseSummary:
    case = store.get_case(case_id, int(user["id"]))
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    return CaseSummary(**case)


@app.get("/api/cases", response_model=CaseListResponse)
def list_cases(limit: int = 50, user: dict = Depends(current_user)) -> CaseListResponse:
    safe_limit = max(1, min(limit, 200))
    return CaseListResponse(cases=[CaseSummary(**case) for case in store.list_cases(safe_limit, int(user["id"]))])


@app.get("/api/cases/{case_id}/report")
def get_case_report(case_id: int, user: dict = Depends(current_user)) -> FileResponse:
    case = store.get_case(case_id, int(user["id"]))
    if case is None or not case.get("report_path"):
        raise HTTPException(status_code=404, detail="Report not found.")

    report_path = Path(str(case["report_path"])).resolve()
    if not report_path.is_file() or REPORT_DIR.resolve() not in report_path.parents:
        raise HTTPException(status_code=404, detail="Report not found.")

    return FileResponse(report_path, media_type="application/json", filename=report_path.name)


@app.get("/api/cases/{case_id}/artifact/{kind}")
def get_case_artifact(case_id: int, kind: str, user: dict = Depends(current_user)) -> FileResponse:
    case = store.get_case(case_id, int(user["id"]))
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    allowed = {
        "original": None,
        "ela": "ela_image_path",
        "heatmap": "heatmap_path",
        "anomaly": "anomaly_overlay_path",
        "audio-waveform": "audio_waveform_path",
        "audio-timeline": "audio_timeline_path",
        "video-timeline": "video_timeline_path",
        "video-contact-sheet": "video_contact_sheet_path",
    }
    if kind not in allowed:
        raise HTTPException(status_code=404, detail="Artifact not found.")

    if kind == "original":
        target_path = Path(str(case.get("stored_path") or "")).resolve()
        allowed_root = UPLOAD_DIR.resolve()
    else:
        report_path = Path(str(case.get("report_path") or "")).resolve()
        if not report_path.is_file() or REPORT_DIR.resolve() not in report_path.parents:
            raise HTTPException(status_code=404, detail="Report not found.")
        payload = load_report(report_path)
        artifact_path = payload.get("forensic_artifacts", {}).get(allowed[kind])
        if not artifact_path and kind.startswith("audio-") and case.get("stored_path"):
            stored_path = Path(str(case["stored_path"])).resolve()
            if stored_path.is_file() and UPLOAD_DIR.resolve() in stored_path.parents:
                created = create_audio_artifacts(stored_path, REPORT_DIR, case_id, payload.get("model_results") or [])
                if created:
                    payload.setdefault("forensic_artifacts", {}).update(created)
                    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                    artifact_path = payload.get("forensic_artifacts", {}).get(allowed[kind])
        target_path = Path(str(artifact_path or "")).resolve()
        allowed_root = REPORT_DIR.resolve()

    if not target_path.is_file() or allowed_root not in target_path.parents:
        raise HTTPException(status_code=404, detail="Artifact not found.")
    return FileResponse(target_path)


@app.get("/api/cases/{case_id}/report.docx")
def get_case_docx_report(case_id: int, user: dict = Depends(current_user)) -> FileResponse:
    case = store.get_case(case_id, int(user["id"]))
    if case is None or not case.get("report_path"):
        raise HTTPException(status_code=404, detail="DOCX report not found.")

    json_report_path = Path(str(case["report_path"])).resolve()
    docx_path = json_report_path.with_suffix(".docx")
    if not docx_path.exists() and json_report_path.is_file():
        payload = load_report(json_report_path)
        if not payload.get("evidence_image_path") and case.get("stored_path"):
            payload["evidence_image_path"] = str(case["stored_path"])
        write_docx_report(json_report_path, payload)
    if not docx_path.is_file() or REPORT_DIR.resolve() not in docx_path.parents:
        raise HTTPException(status_code=404, detail="DOCX report not found.")

    return FileResponse(
        docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=docx_path.name,
    )


@app.websocket("/{path:path}")
async def close_unknown_websocket(websocket: WebSocket, path: str) -> None:
    await websocket.close(code=1000)


if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="web")




