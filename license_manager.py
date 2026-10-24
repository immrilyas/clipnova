
import json
import secrets
import string
from datetime import datetime, timezone, timedelta
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
LICENSE_DIR = APP_DIR / "license_data"
LICENSE_FILE = LICENSE_DIR / "licenses.json"


def _now():
    return datetime.now(timezone.utc)


def _read_database():
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)

    if not LICENSE_FILE.exists():
        return {"licenses": {}}

    try:
        data = json.loads(LICENSE_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"licenses": {}}
        data.setdefault("licenses", {})
        return data
    except (OSError, json.JSONDecodeError):
        return {"licenses": {}}


def _write_database(data):
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    LICENSE_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )


def generate_key():
    alphabet = string.ascii_uppercase + string.digits
    groups = [
        "".join(secrets.choice(alphabet) for _ in range(5))
        for _ in range(4)
    ]
    return "CLIP-" + "-".join(groups)


def create_license(plan, customer=""):
    """
    Creates a local prototype license.
    Monthly plans expire after 30 days.
    Lifetime plans have no expiry.
    """
    plan = plan.strip().lower()

    durations = {
        "starter": 30,
        "premium": 30,
        "starter plus": None,
        "ultra pro": None,
    }

    if plan not in durations:
        raise ValueError("Unknown plan.")

    key = generate_key()
    days = durations[plan]
    expires = (
        (_now() + timedelta(days=days)).isoformat()
        if days is not None
        else None
    )

    data = _read_database()
    data["licenses"][key] = {
        "plan": plan,
        "customer": customer.strip(),
        "created_at": _now().isoformat(),
        "expires_at": expires,
        "revoked": False,
    }
    _write_database(data)

    return key


def validate_license(key):
    key = key.strip().upper()

    if not key:
        return False, "Please enter a license key.", None

    data = _read_database()
    record = data["licenses"].get(key)

    if not record:
        return False, "License key not found on this computer.", None

    if record.get("revoked"):
        return False, "This license has been revoked.", None

    expires = record.get("expires_at")
    if expires:
        try:
            expiry_date = datetime.fromisoformat(expires)
            if expiry_date <= _now():
                return False, "This license has expired.", None
        except ValueError:
            return False, "License expiry information is invalid.", None

    return True, "License activated.", record


def revoke_license(key):
    data = _read_database()
    key = key.strip().upper()

    if key not in data["licenses"]:
        return False

    data["licenses"][key]["revoked"] = True
    _write_database(data)
    return True


def list_licenses():
    return _read_database()["licenses"]
