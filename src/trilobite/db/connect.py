from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional

import psycopg

@dataclass(frozen=True)
class DbSettings:
    dbname: str = "trilobite"
    host: str = "/run/postgresql"
    user: Optional[str] = None # None means use current OS user
    port: int = 5432

def connect(settings: DbSettings | None = None) -> psycopg.Connection:
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

