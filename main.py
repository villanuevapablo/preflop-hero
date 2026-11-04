"""
main.py — Main CLI orchestrator for the Preflop Hero poker analyzer.

Execution pipeline:
1. Parses history.txt using HandParser.
2. Inserts extracted hands into SQLite via PokerDatabase.
3. Generates statistical & diagnostic report via PokerAnalyzer.
"""

import os
import sys
from parser import HandParser
from database import PokerDatabase
from analyzer import PokerAnalyzer


def main():
    # Resolve paths relative to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, "history.txt")
    db_file = os.path.join(script_dir, "poker_stats.db")

    # ─── Step 1: Parse hand histories ──────────────────────────────
    print("🔄 Parsing hand history files...")

    parser_engine = HandParser()

    if not os.path.exists(history_file):
        print(f"❌ Error: File not found '{history_file}'.")
        sys.exit(1)

    hands = parser_engine.parse_file(history_file)
    print(f"   → Discovered {len(hands)} valid hand(s) in source file.")

    if not hands:
        print("⚠️  No valid hands found. Please verify the history format.")
        sys.exit(0)

    # ─── Step 2: Persist into SQLite database ───────────────────────
    print(f"💾 Storing records into SQLite: {db_file}")

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

        print(f"   → Inserted: {inserted} | Duplicates (safely ignored): {duplicates}")

        # ─── Step 3: Run analysis & print report ────────────────────
        analyzer = PokerAnalyzer(db)
        analyzer.generate_report()


if __name__ == "__main__":
    main()
