"""
main.py — Script principal del analizador de manos de poker.

Flujo:
1. Parsea history.txt con HandParser.
2. Inserta resultados en SQLite vía PokerDatabase.
3. Genera reporte con PokerAnalyzer.
"""

import os
import sys
from parser import HandParser
from database import PokerDatabase
from analyzer import PokerAnalyzer


def main():
    # Resolver rutas relativas al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, "history.txt")
    db_file = os.path.join(script_dir, "poker_stats.db")

    # ─── Paso 1: Parsear el archivo de historiales ──────────────────
    print("🔄 Parseando historiales de manos...")

    parser_engine = HandParser()

    if not os.path.exists(history_file):
        print(f"❌ Error: No se encontró el archivo '{history_file}'.")
        sys.exit(1)

    hands = parser_engine.parse_file(history_file)
    print(f"   → Se encontraron {len(hands)} mano(s) en el archivo.")

    if not hands:
        print("⚠️  No se encontraron manos válidas. Verifica el formato del archivo.")
        sys.exit(0)

    # ─── Paso 2: Almacenar en la base de datos ─────────────────────
    print(f"💾 Almacenando en base de datos: {db_file}")

    with PokerDatabase(db_file) as db:
        inserted = 0
        duplicates = 0

        for hand in hands:
            was_inserted = db.insert_hand(
                hand_id=hand["hand_id"],
                platform=hand["platform"],
                hero_cards=hand["hero_cards"],
                vpip=hand["vpip"],
                pfr=hand["pfr"],
            )
            if was_inserted:
                inserted += 1
            else:
                duplicates += 1

        print(f"   → Insertadas: {inserted} | Duplicadas (ignoradas): {duplicates}")

        # ─── Paso 3: Generar reporte ───────────────────────────────
        analyzer = PokerAnalyzer(db)
        analyzer.generate_report()


if __name__ == "__main__":
    main()
