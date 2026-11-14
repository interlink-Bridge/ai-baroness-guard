# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Alexanja Senke.

"""A deliberately narrow, independent, deterministic output gate.

Copyright (c) 2026 Alexanja Senke.
AI Baroness: non-functional origin marker, not a hidden mechanism.
No protected engine code, proof adapter, hardware driver, or network interface.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import re
from fractions import Fraction
from typing import Any

SCOPE = "exact-integer-rational-arithmetic"
NONCLAIMS = [
    "No verification of arbitrary natural-language statements.",
    "No verification of external evidence truth, provenance custody, or signatures.",
    "No runtime enforcement of downstream tool authorization.",
    "No TP-CERT industrial certification or protected proof capability.",
]
MAX_EXPRESSION = 192
MAX_INTEGER_DIGITS = 24
MAX_BITS = 1024
MAX_ACTIONS = 8
NUMBER = re.compile(r"-?(?:0|[1-9][0-9]{0,23})(?:/[1-9][0-9]{0,23})?\Z")
EVIDENCE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}\Z")


class Invalid(Exception):
    def __init__(self, status: str, reason: str):
        super().__init__(reason)
        self.status = status
        self.reason = reason


def exact_keys(data: Any, required: set[str], optional: set[str] = frozenset()) -> None:
    if not isinstance(data, dict) or not required.issubset(data) or set(data) - required - optional:
        raise Invalid("REJECTED", "BAD_SCHEMA")


def claim_digest(claim: dict[str, str]) -> str:
    """SHA-256 binds the EXACT public claim; it is not evidence of its truth."""
    raw = json.dumps(claim, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def checked(value: Fraction) -> Fraction:
    if value.numerator.bit_length() > MAX_BITS or value.denominator.bit_length() > MAX_BITS:
        raise Invalid("REJECTED", "ARITHMETIC_LIMIT")
    return value


def parse_number(s: str) -> Fraction:
    if not isinstance(s, str) or not NUMBER.fullmatch(s):
        raise Invalid("REJECTED", "INVALID_EXACT_ANSWER")
    return checked(Fraction(s))


def evaluate_ast(expr: str) -> Fraction:
    try:
        tree = ast.parse(expr, mode="eval")
    except (SyntaxError, ValueError, RecursionError):
        raise Invalid("REJECTED", "UNSUPPORTED_EXPRESSION") from None
    count = 0

    def ev(node: ast.AST, depth: int = 0) -> Fraction:
        nonlocal count
        count += 1
        if count > 96 or depth > 32:
            raise Invalid("REJECTED", "EXPRESSION_LIMIT")
        if isinstance(node, ast.Expression):
            return ev(node.body, depth + 1)
        if isinstance(node, ast.Constant) and type(node.value) is int:
            if len(str(node.value)) > MAX_INTEGER_DIGITS:
                raise Invalid("REJECTED", "ARITHMETIC_LIMIT")
            return checked(Fraction(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            x = ev(node.operand, depth + 1)
            return checked(x if isinstance(node.op, ast.UAdd) else -x)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            a = ev(node.left, depth + 1)
            b = ev(node.right, depth + 1)
            if isinstance(node.op, ast.Add):
                return checked(a + b)
            if isinstance(node.op, ast.Sub):
                return checked(a - b)
            if isinstance(node.op, ast.Mult):
                return checked(a * b)
            if b == 0:
                raise Invalid("REJECTED", "DIVISION_BY_ZERO")
            return checked(a / b)
        raise Invalid("REJECTED", "UNSUPPORTED_EXPRESSION")

    return ev(tree)


def evaluate_countercheck(expr: str) -> Fraction:
    """Independent recursive-descent grammar and integer-pair arithmetic path."""
    tokens: list[str] = []
    pos = 0
    while pos < len(expr):
        if expr[pos].isspace():
            pos += 1
            continue
        match = re.match(r"[0-9]+|[()+*/-]", expr[pos:])
        if match is None:
            raise Invalid("REJECTED", "UNSUPPORTED_EXPRESSION")
        tok = match.group()
        if tok.isdigit() and len(tok) > MAX_INTEGER_DIGITS:
            raise Invalid("REJECTED", "ARITHMETIC_LIMIT")
        tokens.append(tok)
        pos += len(tok)
    if len(tokens) > 96:
        raise Invalid("REJECTED", "EXPRESSION_LIMIT")
    idx = 0

    def norm(n: int, d: int) -> tuple[int, int]:
        if d == 0:
            raise Invalid("REJECTED", "DIVISION_BY_ZERO")
        if d < 0:
            n, d = -n, -d
        g = math.gcd(n, d)
        n, d = n // g, d // g
        if n.bit_length() > MAX_BITS or d.bit_length() > MAX_BITS:
            raise Invalid("REJECTED", "ARITHMETIC_LIMIT")
        return (n, d)

    def expr_p(depth: int) -> tuple[int, int]:
        nonlocal idx
        x = term(depth + 1)
        while idx < len(tokens) and tokens[idx] in ("+", "-"):
            op = tokens[idx]
            idx += 1
            y = term(depth + 1)
            x = norm(x[0] * y[1] + (y[0] * x[1] if op == "+" else -y[0] * x[1]), x[1] * y[1])
        return x

    def term(depth: int) -> tuple[int, int]:
        nonlocal idx
        x = atom(depth + 1)
        while idx < len(tokens) and tokens[idx] in ("*", "/"):
            op = tokens[idx]
            idx += 1
            y = atom(depth + 1)
            x = norm(x[0] * y[0], x[1] * y[1]) if op == "*" else norm(x[0] * y[1], x[1] * y[0])
        return x

    def atom(depth: int) -> tuple[int, int]:
        nonlocal idx
        if depth > 48 or idx >= len(tokens):
            raise Invalid("REJECTED", "UNSUPPORTED_EXPRESSION")
        t = tokens[idx]
        idx += 1
        if t == "+":
            return atom(depth + 1)
        if t == "-":
            x = atom(depth + 1)
            return norm(-x[0], x[1])
        if t == "(":
            x = expr_p(depth + 1)
            if idx >= len(tokens) or tokens[idx] != ")":
                raise Invalid("REJECTED", "UNSUPPORTED_EXPRESSION")
            idx += 1
            return x
        if t.isdigit():
            return norm(int(t), 1)
        raise Invalid("REJECTED", "UNSUPPORTED_EXPRESSION")

    value = expr_p(0)
    if idx != len(tokens):
        raise Invalid("REJECTED", "UNSUPPORTED_EXPRESSION")
    return Fraction(*value)


def decision(status: str, reason: str, digest: str | None = None, message: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": "baroness-decision-v1",
        "status": status,
        "reason_code": reason,
        "scope": SCOPE,
        "nonclaims": NONCLAIMS[:],
        "action_executed": False,
    }
    if digest:
        result["claim_sha256"] = digest
    if message is not None:
        result["release_text"] = message
    return result


def assess(agent: Any, trusted_evidence: Any) -> dict[str, Any]:
    """Only a VERIFIED result has a guard-generated release_text.

    The agent cannot supply trusted_evidence. The caller must enforce its origin.
    The guard NEVER executes actions; the downstream tool boundary must re-authorize.
    """
    digest = None
    try:
        exact_keys(agent, {"schema", "claim", "evidence_id", "actions", "assumptions"}, {"draft_text"})
        if agent["schema"] != "baroness-agent-v1":
            raise Invalid("REJECTED", "BAD_SCHEMA_VERSION")
        if "draft_text" in agent and (not isinstance(agent["draft_text"], str) or len(agent["draft_text"]) > 4000):
            raise Invalid("REJECTED", "BAD_DRAFT_FORMAT")
        claim = agent["claim"]
        exact_keys(claim, {"kind", "expression", "answer"})
        if claim["kind"] != "exact_arithmetic":
            raise Invalid("REJECTED", "UNSUPPORTED_CLAIM_KIND")
        expr, answer = claim["expression"], claim["answer"]
        if not isinstance(expr, str) or len(expr) > MAX_EXPRESSION or not expr:
            raise Invalid("REJECTED", "EXPRESSION_LIMIT")
        if not isinstance(answer, str):
            raise Invalid("REJECTED", "INVALID_EXACT_ANSWER")
        if not isinstance(agent["assumptions"], list) or any(not isinstance(x, str) for x in agent["assumptions"]):
            raise Invalid("REJECTED", "BAD_ASSUMPTIONS")
        if agent["assumptions"] != [SCOPE]:
            raise Invalid("OPEN", "ASSUMPTIONS_NOT_ADMITTED")
        if not isinstance(agent["evidence_id"], str) or not EVIDENCE_ID.fullmatch(agent["evidence_id"]):
            raise Invalid("REJECTED", "BAD_EVIDENCE_ID")
        if not isinstance(agent["actions"], list) or len(agent["actions"]) > MAX_ACTIONS:
            raise Invalid("REJECTED", "BAD_ACTIONS")
        for a in agent["actions"]:
            exact_keys(a, {"tool", "arguments"})
            if a["tool"] != "evidence.read":
                raise Invalid("REJECTED", "ACTION_NOT_ADMITTED")
            exact_keys(a["arguments"], {"evidence_id"})
            if a["arguments"]["evidence_id"] != agent["evidence_id"]:
                raise Invalid("REJECTED", "ACTION_SCOPE_MISMATCH")
        digest = claim_digest(claim)
        first = evaluate_ast(expr)
        second = evaluate_countercheck(expr)
        if first != second:
            return decision("ERROR", "COUNTERCHECK_DISAGREEMENT", digest)
        submitted = parse_number(answer)
        if submitted != first:
            raise Invalid("REJECTED", "ARITHMETIC_MISMATCH")
        # Trusted registry is a separate input channel; digest prevents accidental claim substitution.
        if (not isinstance(trusted_evidence, dict)
                or set(trusted_evidence) != {"schema", "records"}
                or trusted_evidence["schema"] != "baroness-evidence-v1"
                or not isinstance(trusted_evidence["records"], dict)):
            raise Invalid("ERROR", "TRUSTED_EVIDENCE_BAD_SCHEMA")
        record = trusted_evidence["records"].get(agent["evidence_id"])
        if record is None:
            raise Invalid("OPEN", "EVIDENCE_MISSING")
        exact_keys(record, {"claim_sha256", "scope", "source"})
        if record["scope"] != SCOPE or not isinstance(record["source"], str) or not record["source"].strip():
            raise Invalid("REJECTED", "EVIDENCE_SCOPE_MISMATCH")
        if not isinstance(record["claim_sha256"], str) or record["claim_sha256"] != digest:
            raise Invalid("REJECTED", "EVIDENCE_BINDING_MISMATCH")
        # Never print agent draft text, even when it contains hostile instructions.
        # The only released text is constructed from a narrowly parsed mathematical expression.
        expression_clean = "".join(expr.split())
        return decision("VERIFIED", "EXACT_ARITHMETIC_WITH_BOUND_FIXTURE", digest,
                        f"Verified within {SCOPE}: {expression_clean} = {first}.")
    except Invalid as exc:
        return decision(exc.status, exc.reason, digest)
    except (ArithmeticError, OverflowError, RecursionError, MemoryError):
        return decision("ERROR", "EVALUATION_FAILED", digest)
