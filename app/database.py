
import os
import json
import sqlite3

from datetime import datetime, timezone
from pathlib import Path


class Database:

    def __init__(self, database_path=None):

        if database_path is None:
            configured_path = os.getenv("DATABASE_PATH")

            if configured_path:
                database_path = configured_path
            else:
                project_root = Path(__file__).resolve().parent.parent
                database_path = project_root / "data" / "conversations.db"

        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.initialize()

    def connect(self):
        connection = sqlite3.connect(
            self.database_path,
            timeout=30,
        )

        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):

        with self.connect() as connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    citations TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations(id)
                )
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id, id)
            """)

    def create_conversation(self, conversation_id):

        with self.connect() as connection:

            connection.execute(
                """
                INSERT INTO conversations (id, created_at)
                VALUES (?, ?)
                """,
                (
                    conversation_id,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def conversation_exists(self, conversation_id):

        with self.connect() as connection:

            row = connection.execute(
                "SELECT id FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()

        return row is not None

    def add_message(
        self,
        conversation_id,
        role,
        content,
        citations=None,
    ):

        with self.connect() as connection:

            connection.execute(
                """
                INSERT INTO messages (
                    conversation_id,
                    role,
                    content,
                    citations,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    role,
                    content,
                    json.dumps(citations or []),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def get_messages(self, conversation_id):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT role, content, citations, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id ASC
                """,
                (conversation_id,),
            ).fetchall()

        return [
            {
                "role": row["role"],
                "content": row["content"],
                "citations": json.loads(row["citations"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
