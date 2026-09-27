"""Deprecated import path; install the ``snowflake`` extra.

Move connection construction into the owning API or data repository before
removal. The optional implementation remains here for migration compatibility.
"""

from .infrastructure.snowflake import connect, connection_parameters

__all__ = ["connect", "connection_parameters"]
