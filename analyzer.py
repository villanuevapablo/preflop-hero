"""
analyzer.py — Módulo de análisis estadístico de poker.

Consulta la base de datos, calcula porcentajes VPIP/PFR,
y evalúa la estrategia preflop contra estándares óptimos 6-max.
"""


class PokerAnalyzer:
    """Analiza estadísticas de poker y genera reportes de diagnóstico."""

    # Rangos óptimos para mesas 6-max (cash game)
    OPTIMAL_VPIP_MIN = 20.0
    OPTIMAL_VPIP_MAX = 27.0
    OPTIMAL_PFR_MIN = 17.0
    OPTIMAL_PFR_MAX = 23.0
    OPTIMAL_GAP_MIN = 3.0
    OPTIMAL_GAP_MAX = 6.0

    def __init__(self, database):
        """
        Inicializa el analizador con una referencia a la base de datos.

        Args:
            database: Instancia de PokerDatabase ya conectada.
        """
        self.db = database

    def calculate_stats(self):
        """
        Obtiene las estadísticas agregadas de la base de datos.

        Returns:
            Diccionario con total_hands, vpip_count, pfr_count,
            vpip_pct, pfr_pct y gap.
        """
        return self.db.get_stats()

    def evaluate_strategy(self, stats):
        """
        Evalúa la estrategia preflop comparándola con los rangos óptimos.

        Args:
            stats: Diccionario de estadísticas (de calculate_stats).

        Returns:
            Diccionario con diagnósticos para vpip, pfr y gap.
            Cada diagnóstico tiene 'status' ('ÓPTIMO', 'ALTO', 'BAJO')
            y 'message' con recomendación.
        """
        diagnostics = {}

        # ─── Evaluación VPIP ────────────────────────────────────────
        vpip = stats["vpip_pct"]
        if vpip < self.OPTIMAL_VPIP_MIN:
            diagnostics["vpip"] = {
                "status": "⚠️  BAJO",
                "message": (
                    f"VPIP {vpip:.1f}% está por debajo del rango óptimo "
                    f"({self.OPTIMAL_VPIP_MIN}-{self.OPTIMAL_VPIP_MAX}%). "
                    "Estás jugando demasiado tight. Considera abrir más manos, "
                    "especialmente en posición tardía (CO, BTN)."
                ),
            }
        elif vpip > self.OPTIMAL_VPIP_MAX:
            diagnostics["vpip"] = {
                "status": "⚠️  ALTO",
                "message": (
                    f"VPIP {vpip:.1f}% está por encima del rango óptimo "
                    f"({self.OPTIMAL_VPIP_MIN}-{self.OPTIMAL_VPIP_MAX}%). "
                    "Estás jugando demasiado loose. Reduce el rango de manos "
                    "desde posiciones tempranas (UTG, MP)."
                ),
            }
        else:
            diagnostics["vpip"] = {
                "status": "✅ ÓPTIMO",
                "message": (
                    f"VPIP {vpip:.1f}% está dentro del rango óptimo "
                    f"({self.OPTIMAL_VPIP_MIN}-{self.OPTIMAL_VPIP_MAX}%)."
                ),
            }

        # ─── Evaluación PFR ─────────────────────────────────────────
        pfr = stats["pfr_pct"]
        if pfr < self.OPTIMAL_PFR_MIN:
            diagnostics["pfr"] = {
                "status": "⚠️  BAJO",
                "message": (
                    f"PFR {pfr:.1f}% está por debajo del rango óptimo "
                    f"({self.OPTIMAL_PFR_MIN}-{self.OPTIMAL_PFR_MAX}%). "
                    "Estás entrando demasiado pasivamente (cold-calling). "
                    "Prioriza 3-bet sobre call cuando tengas manos fuertes."
                ),
            }
        elif pfr > self.OPTIMAL_PFR_MAX:
            diagnostics["pfr"] = {
                "status": "⚠️  ALTO",
                "message": (
                    f"PFR {pfr:.1f}% está por encima del rango óptimo "
                    f"({self.OPTIMAL_PFR_MIN}-{self.OPTIMAL_PFR_MAX}%). "
                    "Estás siendo demasiado agresivo preflop. Reduce la "
                    "frecuencia de open-raise desde posiciones tempranas."
                ),
            }
        else:
            diagnostics["pfr"] = {
                "status": "✅ ÓPTIMO",
                "message": (
                    f"PFR {pfr:.1f}% está dentro del rango óptimo "
                    f"({self.OPTIMAL_PFR_MIN}-{self.OPTIMAL_PFR_MAX}%)."
                ),
            }

        # ─── Evaluación de la Brecha VPIP - PFR ────────────────────
        gap = stats["gap"]
        if gap < self.OPTIMAL_GAP_MIN:
            diagnostics["gap"] = {
                "status": "⚠️  BAJO",
                "message": (
                    f"Brecha {gap:.1f}pp está por debajo del rango óptimo "
                    f"({self.OPTIMAL_GAP_MIN}-{self.OPTIMAL_GAP_MAX}pp). "
                    "Tu juego es muy agresivo con poco cold-calling. "
                    "Considera incorporar más calls con manos especulativas "
                    "(suited connectors, pocket pairs bajos)."
                ),
            }
        elif gap > self.OPTIMAL_GAP_MAX:
            diagnostics["gap"] = {
                "status": "⚠️  ALTO",
                "message": (
                    f"Brecha {gap:.1f}pp está por encima del rango óptimo "
                    f"({self.OPTIMAL_GAP_MIN}-{self.OPTIMAL_GAP_MAX}pp). "
                    "Estás haciendo demasiado cold-call. Convierte parte de "
                    "tus calls en 3-bets para ganar más botes preflop."
                ),
            }
        else:
            diagnostics["gap"] = {
                "status": "✅ ÓPTIMO",
                "message": (
                    f"Brecha {gap:.1f}pp está dentro del rango óptimo "
                    f"({self.OPTIMAL_GAP_MIN}-{self.OPTIMAL_GAP_MAX}pp)."
                ),
            }

        return diagnostics

    def generate_report(self):
        """
        Genera e imprime un reporte completo de estadísticas y diagnóstico.
        """
        stats = self.calculate_stats()
        hands = self.db.get_all_hands()
        diagnostics = self.evaluate_strategy(stats)

        separator = "═" * 72
        thin_sep = "─" * 72

        print(f"\n{separator}")
        print("  ♠ ♥ ♦ ♣   REPORTE DE ESTADÍSTICAS PREFLOP   ♣ ♦ ♥ ♠")
        print(separator)

        # ─── Tabla de manos individuales ────────────────────────────
        print(f"\n{'N°':<4} {'HAND ID':<30} {'PLATAFORMA':<12} {'CARTAS':<10} {'VPIP':<6} {'PFR':<6}")
        print(thin_sep)
        for i, hand in enumerate(hands, 1):
            vpip_sym = "✔" if hand["vpip"] else "✘"
            pfr_sym = "✔" if hand["pfr"] else "✘"
            cards = hand["hero_cards"] or "N/A"
            print(
                f"{i:<4} {hand['hand_id']:<30} {hand['platform']:<12} "
                f"{cards:<10} {vpip_sym:<6} {pfr_sym:<6}"
            )

        # ─── Estadísticas globales ──────────────────────────────────
        print(f"\n{separator}")
        print("  📊  ESTADÍSTICAS GLOBALES")
        print(separator)
        print(f"  Total de manos analizadas:  {stats['total_hands']}")
        print(f"  Manos con VPIP:             {stats['vpip_count']}  ({stats['vpip_pct']:.2f}%)")
        print(f"  Manos con PFR:              {stats['pfr_count']}  ({stats['pfr_pct']:.2f}%)")
        print(f"  Brecha VPIP - PFR:          {stats['gap']:.2f}pp")

        # ─── Rangos de referencia ───────────────────────────────────
        print(f"\n{separator}")
        print("  📐  RANGOS ÓPTIMOS 6-MAX (REFERENCIA)")
        print(separator)
        print(f"  VPIP:   {self.OPTIMAL_VPIP_MIN:.0f}% – {self.OPTIMAL_VPIP_MAX:.0f}%")
        print(f"  PFR:    {self.OPTIMAL_PFR_MIN:.0f}% – {self.OPTIMAL_PFR_MAX:.0f}%")
        print(f"  Brecha: {self.OPTIMAL_GAP_MIN:.0f}pp – {self.OPTIMAL_GAP_MAX:.0f}pp")

        # ─── Diagnóstico ───────────────────────────────────────────
        print(f"\n{separator}")
        print("  🔍  DIAGNÓSTICO DE ESTRATEGIA")
        print(separator)

        labels = {"vpip": "VPIP", "pfr": "PFR", "gap": "BRECHA VPIP-PFR"}
        for key in ["vpip", "pfr", "gap"]:
            diag = diagnostics[key]
            print(f"\n  [{labels[key]}] {diag['status']}")
            print(f"  {diag['message']}")

        print(f"\n{separator}")

        # ─── Advertencia de muestra pequeña ─────────────────────────
        if stats["total_hands"] < 100:
            print(
                f"\n  ⚠️  NOTA: La muestra es de solo {stats['total_hands']} mano(s). "
                "Para resultados estadísticamente significativos, se recomienda "
                "un mínimo de 1.000 manos."
            )
            print()
