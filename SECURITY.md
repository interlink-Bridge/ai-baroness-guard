# Security model and exclusions

**Untrusted:** agent JSON, the agent's claims and proposed actions, `draft_text`, externally retrieved content; none of these may set trusted policy. A caller-controlled `--evidence` file is trusted *only if the caller protects its location and creation*. Neither its JSON format nor the digest authenticates it.

**Attack surfaces considered:** malformed JSON and duplicate keys, negative/oversized math, zero division, Python code execution via expression, unsafe proposed tools, extra JSON fields, mismatched evidence identifiers, substituted claims, unsupported assumptions, prompt injection in unused draft prose.

**Fail-closed behavior:** only narrow, exact, positive verification leads to a machine-generated release string. Unknown claim families and attempted tool invocations are not approved. No arbitrary prose is returned. Errors and missing evidence never produce release text.

**Limitations:** This is not a sandbox; does not cryptographically authenticate evidence or determine natural-language truth; does not scan arbitrary text for malicious commands; does not enforce downstream system permissions; no protection against a malicious caller who controls both files; not a complete prompt injection solution; not independently audited or production hardened. Tool authorization must be enforced by each executing application as well.

**Supply chain:** Python standard library only; no cloud, telemetry, RPC, hardware, TP-CERT engine, or protected research code.
