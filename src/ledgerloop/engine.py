"""Stage 3 & 4: Orchestration, routing, and exception handling."""

from typing import List, Tuple

from .models import LedgerEntry, BankTransaction, MatchDecision

# TODO: Implement engine per §9
# - Run all stages in sequence
# - Route by confidence
# - Populate exception queue
# - Append audit trail
