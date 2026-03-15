#!/usr/bin/env python3
"""
Standalone auth API smoke test.

What it verifies:
1) API server is reachable
2) Database connectivity via /api/v1/health/db
3) Register endpoint works
4) Login endpoint works and returns access_token
5) (Optional) Duplicate register is rejected

Usage:
  python scripts/test_auth_api.py --base-url http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10.0,
) -> tuple[int, dict[str, Any]]:
    body = None
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = Request(url=url, data=body, headers=req_headers, method=method.upper())

    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw) if raw else {}
            return resp.status, data
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            data = {"raw": raw}
        return exc.code, data
    except URLError as exc:
        raise RuntimeError(f"Network error when calling {url}: {exc}") from exc


def assert_step(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test register/login API against real backend.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend base URL")
    parser.add_argument("--password", default="12345678", help="Password used for test register/login")
    parser.add_argument(
        "--omit-email",
        action="store_true",
        help="Do not send email in register payload (tests backend auto email generation).",
    )
    parser.add_argument("--gender", default="不填写", help="Gender used in register payload")
    parser.add_argument("--age-range", default="不填写", help="Age range used in register payload")
    parser.add_argument(
        "--skip-duplicate-check",
        action="store_true",
        help="Skip duplicate register negative test",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    username = f"test002"
    email = f"{username}@example.com"
    phone = f"13{random.randint(100000000, 999999999)}"

    print(f"[INFO] Base URL: {base_url}")
    print(f"[INFO] Test user: username={username}, email={email}, phone={phone}")

    # 1) Health check
    status, data = request_json("GET", f"{base_url}/api/v1/health/db")
    print(f"[STEP] GET /api/v1/health/db -> {status} {data}")
    assert_step(status == 200, "health/db endpoint failed")
    assert_step(data.get("status") == "ok", f"health/db status not ok: {data}")
    assert_step(data.get("database") == "connected", f"database not connected: {data}")

    # 2) Register
    register_payload = {
        "username": username,
        "phone": phone,
        "password": args.password,
        "confirm_password": args.password,
        "nickname": "api smoke test",
        "gender": args.gender,
        "age_range": args.age_range,
    }
    if not args.omit_email:
        register_payload["email"] = email

    status, data = request_json("POST", f"{base_url}/api/v1/auth/register", payload=register_payload)
    print(f"[STEP] POST /api/v1/auth/register -> {status} {data}")
    assert_step(status == 201, f"register failed: {status} {data}")
    assert_step(data.get("username") == username, f"register response mismatch: {data}")
    if args.omit_email:
        got_email = data.get("email", "")
        assert_step(
            got_email == f"{username}@xinjing.local",
            f"auto generated email mismatch, got: {got_email}",
        )
    else:
        assert_step(data.get("email") == email, f"register email mismatch: {data}")

    # 3) Login
    login_payload = {"username": username, "password": args.password}
    status, data = request_json("POST", f"{base_url}/api/v1/auth/login", payload=login_payload)
    token_preview = (data.get("access_token", "")[:24] + "...") if data.get("access_token") else None
    print(
        "[STEP] POST /api/v1/auth/login -> "
        f"{status} {{'token_type': {data.get('token_type')}, 'access_token': {token_preview}}}"
    )
    assert_step(status == 200, f"login failed: {status} {data}")
    assert_step(bool(data.get("access_token")), "login did not return access_token")
    assert_step(data.get("token_type") == "bearer", f"unexpected token_type: {data}")

    # 4) Duplicate register (optional)
    if not args.skip_duplicate_check:
        status, data = request_json("POST", f"{base_url}/api/v1/auth/register", payload=register_payload)
        print(f"[STEP] duplicate POST /api/v1/auth/register -> {status} {data}")
        assert_step(status in (400, 409), f"duplicate register should fail, got: {status} {data}")

    print("[PASS] Auth API smoke test passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        raise SystemExit(1)
