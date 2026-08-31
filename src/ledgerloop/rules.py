"""Stage 1: Deterministic matching rules (R1–R5)."""

from decimal import Decimal
from typing import Dict, Optional

from .models import Invoice, Transaction, MatchDecision, MatchStatus

# TODO: Implement rules per §6
# - R1: Exact match
# - R2: Fuzzy counterparty + amount tolerance
# - R3: TDS/bank-charge adjusted amounts
# - R4: Invoice subset matching
# - R5: Confidence routing
