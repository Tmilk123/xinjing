#!/usr/bin/env python3
"""
Standalone login API smoke test.

What it verifies:
1) API server is reachable
2) Login endpoint works and returns access_token

Usage:
  python scripts/test_login_api.py --username your_user --password your_password
"""

from __future__ import annotations

import argparse
import json
import sys
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
    parser = argparse.ArgumentParser(description="Smoke test login API against running backend.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend base URL")
    parser.add_argument("--username", required=True, help="Username or email used for login")
    parser.add_argument("--password", required=True, help="Password used for login")
    parser.add_argument(
        "--expect-fail",
        action="store_true",
        help="Expect login to fail (for negative test)",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    print(f"[INFO] Base URL: {base_url}")
    print(f"[INFO] Login user: {args.username}")

    # 1) Service health check
    status, data = request_json("GET", f"{base_url}/health")
    print(f"[STEP] GET /health -> {status} {data}")
    assert_step(status == 200, f"health check failed: {status} {data}")

    # 2) Login
    login_payload = {"username": args.username, "password": args.password}
    status, data = request_json("POST", f"{base_url}/api/v1/auth/login", payload=login_payload)
    token_preview = (data.get("access_token", "")[:24] + "...") if data.get("access_token") else None
    print(
        "[STEP] POST /api/v1/auth/login -> "
        f"{status} {{'token_type': {data.get('token_type')}, 'access_token': {token_preview}}}"
    )

    if args.expect_fail:
        assert_step(status in (400, 401, 403), f"expected login failure, got: {status} {data}")
        print("[PASS] Login negative test passed.")
        return 0

    assert_step(status == 200, f"login failed: {status} {data}")
    assert_step(bool(data.get("access_token")), "login did not return access_token")
    assert_step(data.get("token_type") == "bearer", f"unexpected token_type: {data}")
    print("[PASS] Login API smoke test passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        raise SystemExit(1)
