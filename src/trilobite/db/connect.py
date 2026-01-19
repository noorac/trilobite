from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional

import psycopg

@dataclass(frozen=True)
class DbSettings:
    """
    Connection settings for a PostgreSQL database.

    Attributes:
    - dbname: database name
    - host: host or unix socket directory, peer-auth setup use unix socket at 
    /run/postgresql
    -user: database username, if None psycopg defaults to current OS user
    -port: database port, usually 5432
    """
    dbname: str = "trilobite"
    host: str = "/run/postgresql"
    user: Optional[str] = None # None means use current OS user
    port: int = 5432

def connect(settings: DbSettings | None = None) -> psycopg.Connection:
    """
    Creates a psycopg connection using explicit settings or env defaults

    Params:
    - settings: optional explicit dbsettings. If omitted values are constructed
    from env variable with module defaults as fallback

    Returns:
    - psycopg.Connection: a new database connection with autocommit disabled
    """
    s = settings or DbSettings(
        dbname=os.getenv("TRILOBITE_DBNAME", "trilobite"),
        host=os.getenv("TRILOBITE_DBHOST", "/run/postgresql"),
        user=os.getenv("TRILOBITE_DBUSER") or None,
        port=int(os.getenv("TRILOBITE_DBPORT", "5432")),
    )

    return psycopg.connect(
        dbname=s.dbname,
        host=s.host,
        user=s.user,
        port=s.port,
        autocommit=False,
    )

