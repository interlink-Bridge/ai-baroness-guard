# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Alexanja Senke.

"""Offline CLI. JSON only. No tool execution, network access, or implicit authority."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from .core import assess, decision

MAX_FILE_BYTES = 32768


def no_duplicates(pairs):
    d = {}
    for key, value in pairs:
        if key in d:
            raise ValueError("duplicate JSON key")
        d[key] = value
    return d


def load_bounded(path: str):
    p = pathlib.Path(path)
    if not p.is_file() or p.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("missing or oversized JSON input")
    return json.loads(p.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError("invalid JSON constant")))


def main(argv=None):
    parser = argparse.ArgumentParser(description="AI Baroness: offline, structured arithmetic guard")
    parser.add_argument("--agent", required=True, help="UNTRUSTED agent proposal JSON")
    parser.add_argument("--evidence", required=True, help="INDEPENDENT caller-controlled evidence registry JSON")
    args = parser.parse_args(argv)
    try:
        # Both files are parsed here, but their trust comes from the CALLER and file permissions.
        agent = load_bounded(args.agent)
        evidence = load_bounded(args.evidence)
        result = assess(agent, evidence)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        result = decision("ERROR", "INPUT_READ_OR_PARSE_ERROR")
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    return {"VERIFIED": 0, "OPEN": 2, "REJECTED": 3, "ERROR": 4}[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
