# AI Baroness Guard — independent public-scope prototype (v0.1.0-rc2)

**STATUS: Public prototype (v0.1.0) — BSD-3-Clause licensed.**

A small offline, Python-standard-library **adversarial release gate** for an AI agent that proposes an **exact arithmetic claim**. It checks a supported expression with two independent parsers, binds it to a separately supplied caller-controlled evidence record, checks proposed actions against a narrow allowlist, and produces its own bounded output. It never executes a tool.

This project *illustrates* a subset of published verification and countercheck principles. It does **not** contain TP-CERT industrial engine source, protected proof procedures, private ASK v2.6 text or rules, hardware adapters, secrets, signatures, or an industrial certification API. It is a new, small, independent implementation.

## 60-second local demo

Designed for Python 3.10+ using only the standard library; **locally tested with Python 3.13 only**. Run from this directory:

```bash
python -m baroness_guard --agent examples/agent_good.json --evidence examples/trusted_evidence.json
python -m baroness_guard --agent examples/agent_bad_math.json --evidence examples/trusted_evidence.json
python -m unittest discover -s tests -v
```

Exit codes: `0` VERIFIED, `2` OPEN, `3` REJECTED, `4` ERROR.

## Output contract

`VERIFIED` is only possible for exact arithmetic over integer literals with `+ - * /` and parentheses, an exact rational answer, the exact admitted assumption, approved read-only proposed actions, and a **caller-provided** matching evidence record. `VERIFIED` is *not* a certificate or endorsement of the agent's draft prose. The guard never forwards `draft_text`, even if the status is VERIFIED. It emits only a checked arithmetic statement built from the parsed expression.

`OPEN` means missing or inadmissible evidence/assumptions, without release. `REJECTED` is invalid arithmetic, invalid schema, binding mismatch or disallowed action. `ERROR` represents operational or independent-check failures. None of the latter statuses provides `release_text`.

## Integration boundary (critical)

- The agent supplies **only** the `--agent` proposal. The calling application supplies `--evidence` from its own independently managed trust domain. The included evidence file is a demo fixture, **not** an authenticated evidence vault.
- A matching SHA-256 digest is **binding, not proof** of source authenticity or truth. Whoever can write the evidence registry can forge a binding. In production use a genuine trusted store, access controls and, where applicable, signed provenance.
- No shell, network, filesystem, or other proposed tool runs here. The one recognized proposed action, `evidence.read`, is a structural preflight check, not execution authority. **Downstream code must enforce permissions again at the actual tool boundary.**
- There is no natural-language semantic proof checker and no general prompt-injection defense. Untrusted agent prose is **discarded rather than approved**. The project does not validate claims within arbitrary text.
- Input caps exist; this is still a prototype and must be threat-modeled before production embedding.

## About ASK and AI Baroness

The small public guard uses a generic **RECONSTRUCT → VERIFY → COUNTERCHECK → CLAIM-BOUND → RELEASE/ABSTAIN** pipeline. The private ASK governance architecture is not distributed. `AI Baroness` is a harmless, discoverable origin marker in the Python module (`__origin__`), not covert telemetry, enforcement, anti-debugging or ownership control.

**Origin:** Alexanja Senke / Interlink Bridge. **Reference (provenance only):** https://doi.org/10.5281/zenodo.23106126 — linked as the separate private/industrial research lineage, **not** as a dependency and **not** a statement about public access or licensing of its contents.

## License / release

**BSD 3-Clause License** (`SPDX-License-Identifier: BSD-3-Clause`). Copyright (c) 2026 Alexanja Senke. See the complete unmodified standard terms (with holder/year instantiated) in [`LICENSE`](LICENSE). All project-origin code in this package is subject to those terms. See [`TRADEMARKS.md`](TRADEMARKS.md) for non-binding identification/endorsement clarification, not extra licensing restrictions.

This is an open-source prototype released under the BSD 3-Clause License; it has not undergone external security certification. The protected TP-CERT industrial engine, hardware paths, internal ASK architecture, related research materials, and any Zenodo deposit are not licensed by this package.
