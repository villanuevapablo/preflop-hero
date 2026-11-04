"""
parser.py — Motor de extracción de historiales de manos de poker.

Parsea archivos de texto con manos de Winamax y 888poker,
extrayendo hand_id, cartas del Hero, y los flags VPIP/PFR.
"""

import re


class HandParser:
    """Parser de historiales de manos de poker para Winamax y 888poker."""

    # ─── Patrones Winamax ───────────────────────────────────────────────
    RE_WINAMAX_HEADER = re.compile(
        r"Winamax Poker.*HandId:\s*#([\w\-]+)"
    )
    RE_WINAMAX_DEALT = re.compile(
        r"Dealt to Hero \[([^\]]+)\]"
    )
    RE_WINAMAX_PREFLOP_SECTION = re.compile(
        r"\*\*\* PRE-FLOP \*\*\*(.*?)(?:\*\*\* FLOP \*\*\*|\*\*\* SUMMARY \*\*\*)",
        re.DOTALL,
    )
    RE_WINAMAX_HERO_ACTION = re.compile(
        r"^Hero\s+(raises|calls|bets|checks|folds)",
        re.MULTILINE,
    )

    # ─── Patrones 888poker ──────────────────────────────────────────────
    RE_888_HEADER = re.compile(
        r"\*{5}\s*888poker Hand History for Game (\d+)\s*\*{5}"
    )
    RE_888_DEALT = re.compile(
        r"Dealt to Hero \[\s*([^\]]+)\s*\]"
    )
    RE_888_PREFLOP_SECTION = re.compile(
        r"\*\* Dealing down cards \*\*(.*?)(?:\*\* Dealing Flop \*\*|\*\*\* SUMMARY \*\*\*)",
        re.DOTALL,
    )
    RE_888_HERO_ACTION = re.compile(
        r"^Hero\s+(raises|calls|bets|checks|folds)",
        re.MULTILINE,
    )

    def parse_file(self, filepath):
        """
        Parsea un archivo completo de historiales de manos.

        Args:
            filepath: Ruta al archivo de texto con los historiales.

        Returns:
            Lista de diccionarios, uno por mano, con las claves:
            hand_id, platform, hero_cards, vpip, pfr.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        raw_hands = self._split_hands(content)
        results = []

        for hand_text in raw_hands:
            hand_text = hand_text.strip()
            if not hand_text:
                continue

            platform = self._detect_platform(hand_text)
            if platform is None:
                continue

            if platform == "winamax":
                parsed = self._parse_winamax(hand_text)
            else:
                parsed = self._parse_888poker(hand_text)

            if parsed:
                results.append(parsed)

        return results

    def _split_hands(self, text):
        """
        Separa el texto completo en bloques individuales por mano.

        Detecta el inicio de cada mano por las cabeceras de Winamax o 888poker
        y divide el texto en segmentos.

        Returns:
            Lista de strings, cada uno conteniendo una mano completa.
        """
        # Patrón que detecta el inicio de una mano de cualquier plataforma
        split_pattern = re.compile(
            r"(?=Winamax Poker -|\*{5}\s*888poker Hand History)"
        )
        hands = split_pattern.split(text)
        return [h for h in hands if h.strip()]

    def _detect_platform(self, hand_text):
        """
        Identifica la plataforma de una mano individual.

        Returns:
            'winamax', '888poker', o None si no se reconoce.
        """
        if hand_text.strip().startswith("Winamax Poker"):
            return "winamax"
        elif "888poker Hand History" in hand_text:
            return "888poker"
        return None

    def _parse_winamax(self, hand_text):
        """
        Extrae los datos de una mano de Winamax.

        Returns:
            Diccionario con hand_id, platform, hero_cards, vpip, pfr,
            o None si no se puede parsear.
        """
        # Extraer hand_id
        header_match = self.RE_WINAMAX_HEADER.search(hand_text)
        if not header_match:
            return None
        hand_id = header_match.group(1)

        # Extraer cartas del Hero
        dealt_match = self.RE_WINAMAX_DEALT.search(hand_text)
        hero_cards = dealt_match.group(1).strip() if dealt_match else None

        # Extraer acciones preflop
        vpip, pfr = self._evaluate_preflop_actions(
            hand_text,
            self.RE_WINAMAX_PREFLOP_SECTION,
            self.RE_WINAMAX_HERO_ACTION,
        )

        return {
            "hand_id": hand_id,
            "platform": "winamax",
            "hero_cards": hero_cards,
            "vpip": vpip,
            "pfr": pfr,
        }

    def _parse_888poker(self, hand_text):
        """
        Extrae los datos de una mano de 888poker.

        Returns:
            Diccionario con hand_id, platform, hero_cards, vpip, pfr,
            o None si no se puede parsear.
        """
        # Extraer hand_id
        header_match = self.RE_888_HEADER.search(hand_text)
        if not header_match:
            return None
        hand_id = header_match.group(1)

        # Extraer cartas del Hero
        dealt_match = self.RE_888_DEALT.search(hand_text)
        hero_cards = None
        if dealt_match:
            # Normalizar formato: "Qd, Qs" → "Qd Qs"
            raw_cards = dealt_match.group(1).strip()
            hero_cards = raw_cards.replace(",", "").replace("  ", " ").strip()

        # Extraer acciones preflop
        vpip, pfr = self._evaluate_preflop_actions(
            hand_text,
            self.RE_888_PREFLOP_SECTION,
            self.RE_888_HERO_ACTION,
        )

        return {
            "hand_id": hand_id,
            "platform": "888poker",
            "hero_cards": hero_cards,
            "vpip": vpip,
            "pfr": pfr,
        }

    def _evaluate_preflop_actions(self, hand_text, section_regex, action_regex):
        """
        Evalúa las acciones del Hero en la sección preflop.

        VPIP = 1 si Hero hace call, raise o bet (acción voluntaria).
        PFR  = 1 si Hero hace raise.
        Postear ciegas NO cuenta como VPIP.

        Args:
            hand_text:     Texto completo de la mano.
            section_regex: Regex para extraer la sección preflop.
            action_regex:  Regex para detectar acciones del Hero.

        Returns:
            Tupla (vpip, pfr) con valores 0 o 1.
        """
        vpip = 0
        pfr = 0

        section_match = section_regex.search(hand_text)
        if not section_match:
            return vpip, pfr

        preflop_text = section_match.group(1)

        # Buscar todas las acciones del Hero en la sección preflop
        actions = action_regex.findall(preflop_text)

        for action in actions:
            action = action.lower()
            if action in ("calls", "bets"):
                vpip = 1
            elif action == "raises":
                vpip = 1
                pfr = 1

        return vpip, pfr
