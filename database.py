"""
database.py — Módulo de persistencia SQLite para el analizador de poker.

Gestiona la conexión a la base de datos y las operaciones CRUD
sobre la tabla hand_statistics.
"""

import sqlite3
import os


class PokerDatabase:
    """Gestiona la base de datos SQLite de estadísticas de manos de poker."""

    def __init__(self, db_path="poker_stats.db"):
        """
        Inicializa la conexión a la base de datos.

        Args:
            db_path: Ruta del archivo de la base de datos SQLite.
        """
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        """Abre la conexión y crea las tablas si no existen."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
        return False

    def _create_tables(self):
        """Crea el esquema relacional si no existe."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS hand_statistics (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                hand_id     TEXT    NOT NULL,
                platform    TEXT    NOT NULL,
                hero_cards  TEXT,
                vpip        INTEGER NOT NULL,
                pfr         INTEGER NOT NULL,
                UNIQUE(hand_id, platform)
            )
        """)
        self.conn.commit()

    def insert_hand(self, hand_id, platform, hero_cards, vpip, pfr):
        """
        Inserta una mano en la base de datos. Ignora duplicados.

        Args:
            hand_id:    Identificador único de la mano.
            platform:   Plataforma de origen ('winamax' o '888poker').
            hero_cards: Cartas del Hero (ej: 'Ah Kd').
            vpip:       1 si Hero puso dinero voluntariamente, 0 si no.
            pfr:        1 si Hero hizo raise preflop, 0 si no.

        Returns:
            True si se insertó, False si ya existía (duplicado).
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
        Obtiene todas las manos registradas.

        Returns:
            Lista de diccionarios con los datos de cada mano.
        """
        cursor = self.conn.execute(
            "SELECT id, hand_id, platform, hero_cards, vpip, pfr FROM hand_statistics ORDER BY id"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self):
        """
        Calcula las estadísticas agregadas de VPIP y PFR.

        Returns:
            Diccionario con total_hands, vpip_count, pfr_count,
            vpip_pct, pfr_pct y gap (brecha VPIP - PFR).
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
        """Elimina todos los registros (útil para testing)."""
        self.conn.execute("DELETE FROM hand_statistics")
        self.conn.commit()
