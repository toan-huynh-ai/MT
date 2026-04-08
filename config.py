import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def _resolve_path(env_val: str, default_rel: str) -> Path:
    """Return an absolute path resolved from the local project root.

    For legacy relative values from older experiments, also try resolving
    relative to the parent folder if the first candidate does not exist.
    """
    candidates: list[Path] = []
    if env_val:
        raw_path = Path(env_val)
        if raw_path.is_absolute():
            candidates.append(raw_path)
        else:
            candidates.append(BASE_DIR / raw_path)
            candidates.append(BASE_DIR.parent / raw_path)
    else:
        default_path = Path(default_rel)
        candidates.append(default_path if default_path.is_absolute() else (BASE_DIR / default_path))

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _resolve_chroma_path(env_val: str, default_rel: str) -> Path:
    candidate = _resolve_path(env_val, default_rel)
    sibling_candidate = BASE_DIR.parent / Path(env_val or default_rel)
    candidates: list[Path] = []
    if sibling_candidate not in candidates:
        candidates.append(sibling_candidate)
    if candidate not in candidates:
        candidates.append(candidate)

    for path in candidates:
        if path.is_dir() and (path / "chroma.sqlite3").exists():
            return path
    return candidate


class Config:
    # --- Project paths ---
    PROJECT_ROOT = BASE_DIR
    CHROMA_PATH = _resolve_chroma_path(os.getenv("CHROMA_PATH", ""), "../chromaDatabase")
    CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "documents")

    DATA_PATH = _resolve_path(os.getenv("DATA_PATH", ""), "data")
    PDFS_DIR = _resolve_path(os.getenv("PDFS_DIR", ""), "data/PDFs")
    ASSETS_DIR = _resolve_path(os.getenv("ASSETS_DIR", ""), "data/PDFs/assets")
    PDF_WORKERS = int(os.getenv("PDF_WORKERS", "4"))
    PARAMS_JSON_PATH = _resolve_path(os.getenv("PARAMS_JSON_PATH", ""), "data/ParamsFolder/paramDB.json")
    PARAMS_JSON_FOLDER = _resolve_path(os.getenv("PARAMS_JSON_FOLDER", ""), "data/ParamsFolder")
    INPUT_DIR = _resolve_path(os.getenv("INPUT_DIR", ""), "data")
    INPUT_DB_PATH = _resolve_path(os.getenv("INPUT_DB_PATH", ""), "data/RTA-FLOW_DB_full.json")
    INPUT_RULES_DIR = _resolve_path(os.getenv("INPUT_RULES_DIR", ""), "data/rules")
    EMBED_CACHE_PATH = _resolve_path(os.getenv("EMBED_CACHE_PATH", ""), "data/embedding_cache.jsonl")
    OUTPUT_DIR = _resolve_path(os.getenv("OUTPUT_DIR", ""), "outputs")
    DEFAULT_CSV_PATH = OUTPUT_DIR / os.getenv("ANALYSIS_CSV_NAME", "analysis.csv")
    DEFAULT_PDF_PATH = OUTPUT_DIR / os.getenv("REPORT_PDF_NAME", "report.pdf")

    # --- Azure auth ---
    TENANT_ID = os.getenv("AZURE_TENANT_ID")
    CLIENT_ID = os.getenv("APPLICATION_AI_VOS_USERS_ID")
    CLIENT_SECRET = os.getenv("APPLICATION_AI_VOS_USERS_SECRET")

    # --- Azure endpoints & models ---
    AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-05-01-preview")
    AZURE_CHAT_DEPLOYMENT = os.getenv("AZURE_CHAT_DEPLOYMENT")
    AZURE_CHAT_MODEL = os.getenv("AZURE_CHAT_MODEL", "gpt-4o")
    AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")

    # --- Pipeline runtime ---
    DEFAULT_TOP_K = int(os.getenv("AUTOGEN_TOP_K", "8"))
    MAX_REVIEW_ROUNDS = int(os.getenv("AUTOGEN_MAX_REVIEW_ROUNDS", "3"))
    CSV_ENCODING = os.getenv("AUTOGEN_CSV_ENCODING", "utf-8-sig")
    PDF_AUTHOR = os.getenv("AUTOGEN_PDF_AUTHOR", "AutoGen Multi-Agent Pipeline")
    LOG_AGENT_STEPS = _env_bool("AUTOGEN_LOG_AGENT_STEPS", True)

    # --- Optional feature bridge (legacy compatibility) ---
    LNM_DB_PATH = _resolve_path(os.getenv("DB_JSON", ""), "data/RTA-FLOW_DB_full.json")
    LNM_RULES_PATH = _resolve_path(
        os.getenv("DB_JSON_RULES", ""),
        "data/rules/step5_SUM_LNM_rules_with_relationships.json",
    )
    RULES_DEDUP = _env_bool("NEW_RAG_RULES_DEDUP", True)
    FEATURE_BRIDGE_CONFIG = os.getenv("FEATURE_BRIDGE_CONFIG")

    @staticmethod
    def ensure_output_dir() -> Path:
        Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return Config.OUTPUT_DIR

    @staticmethod
    def validate() -> None:
        """Ensure critical variables are loaded for Azure AD auth."""
        missing: list[str] = []
        if not Config.TENANT_ID:
            missing.append("AZURE_TENANT_ID")
        if not Config.CLIENT_ID:
            missing.append("APPLICATION_AI_VOS_USERS_ID")
        if not Config.CLIENT_SECRET:
            missing.append("APPLICATION_AI_VOS_USERS_SECRET")
        if not Config.AZURE_ENDPOINT:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not Config.AZURE_CHAT_DEPLOYMENT:
            missing.append("AZURE_CHAT_DEPLOYMENT")

        if missing:
            raise ValueError(f"Missing required environment variables in .env: {', '.join(missing)}")
