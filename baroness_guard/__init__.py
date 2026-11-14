# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Alexanja Senke.

"""AI Baroness Guard: public-scope, fail-closed arithmetic release gate.

Origin signature: AI Baroness. No protected TP-CERT or ASK implementation included.
"""

__version__ = "0.1.0rc2"
__origin__ = "AI Baroness"

from .core import assess, claim_digest

__all__ = ["assess", "claim_digest", "__version__", "__origin__"]
