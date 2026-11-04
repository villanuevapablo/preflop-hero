"""
database.py — SQLite persistence layer for the Preflop Hero poker analyzer.

Manages the database connection and CRUD operations on the
hand_statistics table.
"""

import sqlite3
import os


class PokerDatabase:
    """Manages the SQLite database for poker hand statistics."""

    def __init__(self, db_path="poker_stats.db"):
        """
        Initializes the database connection parameters.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        """Opens database connection and creates tables if they do not exist."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
        return False

    def _create_tables(self):
        """Creates the relational schema with duplicate prevention."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS hand_statistics (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                hand_id     TEXT    NOT NULL,
                platform    TEXT    NOT NULL,
                hero_cards  TEXT,
                vpip        INTEGER NOT NULL,
                pfr         INTEGER NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(hand_id, platform)
            )
        """)
        self.conn.commit()

    def insert_hand(self, hand_id, platform, hero_cards, vpip, pfr):
        """
        Inserts a single hand record into the database. Safely ignores duplicates.

        Args:
            hand_id:    Unique hand identifier.
            platform:   Source platform ('winamax' or '888poker').
            hero_cards: Hero hole cards (e.g., 'Ah Kd').
            vpip:       1 if Hero voluntarily put money in pot, 0 otherwise.
            pfr:        1 if Hero raised preflop, 0 otherwise.

        Returns:
            True if inserted, False if hand already existed (duplicate).
        """
        try:
            self.conn.execute(
                """
                INSERT INTO hand_statistics (hand_id, platform, hero_cards, vpip, pfr)
                VALUES (?, ?, ?, ?, ?)
                """,
                (hand_id, platform, hero_cards, vpip, pfr),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_hands(self):
        """
        Retrieves all recorded hand entries.

        Returns:
            List of dictionaries containing each hand record.
        """
        cursor = self.conn.execute(
            "SELECT id, hand_id, platform, hero_cards, vpip, pfr FROM hand_statistics ORDER BY id"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self):
        """
        Calculates aggregate VPIP, PFR, and cold-call gap statistics.

        Returns:
            Dictionary containing total_hands, vpip_count, pfr_count,
            vpip_pct, pfr_pct, and gap (VPIP - PFR spread).
        """
        cursor = self.conn.execute(
            """
            SELECT
                COUNT(*)      AS total_hands,
                SUM(vpip)     AS vpip_count,
                SUM(pfr)      AS pfr_count
            FROM hand_statistics
            """
        )
        row = cursor.fetchone()
        total = row["total_hands"] or 0
        vpip_count = row["vpip_count"] or 0
        pfr_count = row["pfr_count"] or 0

        vpip_pct = (vpip_count / total * 100) if total > 0 else 0.0
        pfr_pct = (pfr_count / total * 100) if total > 0 else 0.0
        gap = vpip_pct - pfr_pct

        return {
            "total_hands": total,
            "vpip_count": vpip_count,
            "pfr_count": pfr_count,
            "vpip_pct": round(vpip_pct, 2),
            "pfr_pct": round(pfr_pct, 2),
            "gap": round(gap, 2),
        }

    def clear_all(self):
        """Deletes all records (useful for automated testing)."""
        self.conn.execute("DELETE FROM hand_statistics")
        self.conn.commit()
