"""Deprecated import path; install the ``snowflake`` extra.

Move service settings into the owning API or data repository before removal.
"""

from .infrastructure.settings import SnowflakeSettings

__all__ = ["SnowflakeSettings"]
