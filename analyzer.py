"""
analyzer.py — Statistical analysis and GTO strategy audit module.

Queries SQLite persistence, calculates aggregate VPIP/PFR metrics,
and evaluates preflop strategy against 6-max No-Limit Hold'em GTO benchmarks.
"""


class PokerAnalyzer:
    """Analyzes poker statistics and generates diagnostic strategy reports."""

    # 6-Max NLHE theoretical optimal targets (cash game)
    OPTIMAL_VPIP_MIN = 20.0
    OPTIMAL_VPIP_MAX = 27.0
    OPTIMAL_PFR_MIN = 17.0
    OPTIMAL_PFR_MAX = 23.0
    OPTIMAL_GAP_MIN = 3.0
    OPTIMAL_GAP_MAX = 6.0

    def __init__(self, database):
        """
        Initializes the analyzer with an active database instance.

        Args:
            database: Connected PokerDatabase instance.
        """
        self.db = database

    def calculate_stats(self):
        """
        Retrieves aggregate statistics from the database.

        Returns:
            Dict containing total_hands, vpip_count, pfr_count,
            vpip_pct, pfr_pct, and gap.
        """
        return self.db.get_stats()

    def evaluate_strategy(self, stats):
        """
        Evaluates preflop strategy against optimal 6-max benchmarks.

        Args:
            stats: Dict of aggregated statistics (from calculate_stats).

        Returns:
            Dict with diagnostics for vpip, pfr, and gap.
        """
        diagnostics = {}

        # ─── VPIP Evaluation ─────────────────────────────────────────
        vpip = stats["vpip_pct"]
        if vpip < self.OPTIMAL_VPIP_MIN:
            diagnostics["vpip"] = {
                "status": "⚠️  TOO LOW",
                "message": (
                    f"VPIP {vpip:.1f}% is below the optimal target "
                    f"({self.OPTIMAL_VPIP_MIN}-{self.OPTIMAL_VPIP_MAX}%). "
                    "You are playing too tight (nit). Consider opening more hands, "
                    "especially from late position (CO, BTN)."
                ),
            }
        elif vpip > self.OPTIMAL_VPIP_MAX:
            diagnostics["vpip"] = {
                "status": "⚠️  TOO HIGH",
                "message": (
                    f"VPIP {vpip:.1f}% is above the optimal target "
                    f"({self.OPTIMAL_VPIP_MIN}-{self.OPTIMAL_VPIP_MAX}%). "
                    "You are playing too loose. Tighten your opening range "
                    "from early positions (UTG, MP)."
                ),
            }
        else:
            diagnostics["vpip"] = {
                "status": "✅ OPTIMAL",
                "message": (
                    f"VPIP {vpip:.1f}% is within the optimal target "
                    f"({self.OPTIMAL_VPIP_MIN}-{self.OPTIMAL_VPIP_MAX}%)."
                ),
            }

        # ─── PFR Evaluation ──────────────────────────────────────────
        pfr = stats["pfr_pct"]
        if pfr < self.OPTIMAL_PFR_MIN:
            diagnostics["pfr"] = {
                "status": "⚠️  TOO LOW",
                "message": (
                    f"PFR {pfr:.1f}% is below the optimal target "
                    f"({self.OPTIMAL_PFR_MIN}-{self.OPTIMAL_PFR_MAX}%). "
                    "Entering pots too passively (excessive cold-calling). "
                    "Prioritize 3-betting over flat-calling with premium holdings."
                ),
            }
        elif pfr > self.OPTIMAL_PFR_MAX:
            diagnostics["pfr"] = {
                "status": "⚠️  TOO HIGH",
                "message": (
                    f"PFR {pfr:.1f}% is above the optimal target "
                    f"({self.OPTIMAL_PFR_MIN}-{self.OPTIMAL_PFR_MAX}%). "
                    "Preflop aggression is excessively high. Trim speculative "
                    "open-raises from early seats."
                ),
            }
        else:
            diagnostics["pfr"] = {
                "status": "✅ OPTIMAL",
                "message": (
                    f"PFR {pfr:.1f}% is within the optimal target "
                    f"({self.OPTIMAL_PFR_MIN}-{self.OPTIMAL_PFR_MAX}%)."
                ),
            }

        # ─── VPIP - PFR Gap Evaluation ───────────────────────────────
        gap = stats["gap"]
        if gap < self.OPTIMAL_GAP_MIN:
            diagnostics["gap"] = {
                "status": "⚠️  TOO LOW",
                "message": (
                    f"Gap {gap:.1f} pp is below optimal "
                    f"({self.OPTIMAL_GAP_MIN}-{self.OPTIMAL_GAP_MAX} pp). "
                    "Hyper-aggressive play with almost no cold-calling. "
                    "Consider flat-calling suited connectors and small pocket pairs "
                    "when multiway pot odds justify it."
                ),
            }
        elif gap > self.OPTIMAL_GAP_MAX:
            diagnostics["gap"] = {
                "status": "⚠️  TOO HIGH",
                "message": (
                    f"Gap {gap:.1f} pp is above optimal "
                    f"({self.OPTIMAL_GAP_MIN}-{self.OPTIMAL_GAP_MAX} pp). "
                    "Excessive cold-calling (passive leak). Rebalance by turning "
                    "speculative flat-calls into 3-bets or disciplined folds."
                ),
            }
        else:
            diagnostics["gap"] = {
                "status": "✅ OPTIMAL",
                "message": (
                    f"Gap {gap:.1f} pp is within the optimal target "
                    f"({self.OPTIMAL_GAP_MIN}-{self.OPTIMAL_GAP_MAX} pp)."
                ),
            }

        return diagnostics

    def generate_report(self):
        """
        Generates and prints a complete statistical report and leak diagnosis.
        """
        stats = self.calculate_stats()
        hands = self.db.get_all_hands()
        diagnostics = self.evaluate_strategy(stats)

        separator = "═" * 72
        thin_sep = "─" * 72

        print(f"\n{separator}")
        print("  ♠ ♥ ♦ ♣   PREFLOP HERO — STRATEGY AUDIT REPORT   ♣ ♦ ♥ ♠")
        print(separator)

        # ─── Individual Hand Breakdown ───────────────────────────────
        print(f"\n{'#':<4} {'HAND ID':<30} {'PLATFORM':<12} {'CARDS':<10} {'VPIP':<6} {'PFR':<6}")
        print(thin_sep)
        for i, hand in enumerate(hands, 1):
            vpip_sym = "✔" if hand["vpip"] else "✘"
            pfr_sym = "✔" if hand["pfr"] else "✘"
            cards = hand["hero_cards"] or "N/A"
            print(
                f"{i:<4} {hand['hand_id']:<30} {hand['platform']:<12} "
                f"{cards:<10} {vpip_sym:<6} {pfr_sym:<6}"
            )

        # ─── Aggregate Metrics ───────────────────────────────────────
        print(f"\n{separator}")
        print("  📊  AGGREGATE METRICS")
        print(separator)
        print(f"  Total Hands Analyzed:       {stats['total_hands']}")
        print(f"  Hands with VPIP:            {stats['vpip_count']}  ({stats['vpip_pct']:.2f}%)")
        print(f"  Hands with PFR:             {stats['pfr_count']}  ({stats['pfr_pct']:.2f}%)")
        print(f"  PFR / VPIP Gap:             {stats['gap']:.2f} pp")

        # ─── Benchmark Targets ───────────────────────────────────────
        print(f"\n{separator}")
        print("  📐  6-MAX THEORETICAL BENCHMARKS")
        print(separator)
        print(f"  Optimal VPIP:   {self.OPTIMAL_VPIP_MIN:.0f}% – {self.OPTIMAL_VPIP_MAX:.0f}%")
        print(f"  Optimal PFR:    {self.OPTIMAL_PFR_MIN:.0f}% – {self.OPTIMAL_PFR_MAX:.0f}%")
        print(f"  Optimal Gap:    {self.OPTIMAL_GAP_MIN:.0f} pp – {self.OPTIMAL_GAP_MAX:.0f} pp")

        # ─── Strategy Diagnostics ────────────────────────────────────
        print(f"\n{separator}")
        print("  🔍  STRATEGY DIAGNOSTICS & LEAK DETECTION")
        print(separator)

        labels = {"vpip": "VPIP", "pfr": "PFR", "gap": "GAP (VPIP − PFR)"}
        for key in ["vpip", "pfr", "gap"]:
            diag = diagnostics[key]
            print(f"\n  [{labels[key]}] {diag['status']}")
            print(f"  {diag['message']}")

        print(f"\n{separator}")

        # ─── Sample Size Advisory ────────────────────────────────────
        if stats["total_hands"] < 100:
            print(
                f"\n  ⚠️  NOTE: Sample size is only {stats['total_hands']} hand(s). "
                "For statistically reliable leak detection, a minimum of 1,000 hands is recommended."
            )
            print()
