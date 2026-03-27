"""
shared_prompts — runtime prompt registry and loading utilities.

Usage:
    from shared_prompts import get_contract, loader

    contract = get_contract("normalization")          # current default version
    contract = get_contract("normalization", "1")     # explicit version

    text    = loader.load_prompt_text(contract)       # system instruction string
    schema  = loader.load_schema(contract)            # JSON schema dict
    rfmt    = loader.build_response_format(contract)  # LM Studio response_format payload
    missing = loader.missing_assets(contract)         # [] if all files present

Build prompts (prompts/build/) are NOT represented here.
"""

from .contracts import PromptContract
from .registry import REGISTRY, DEFAULT_VERSION, all_contracts, get_contract
from . import loader

__all__ = [
    "PromptContract",
    "REGISTRY",
    "DEFAULT_VERSION",
    "get_contract",
    "all_contracts",
    "loader",
]
