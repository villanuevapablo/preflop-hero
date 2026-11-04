"""
parser.py — Poker hand history extraction engine.

Parses text files containing hand histories from Winamax and 888poker,
extracting hand_id, Hero hole cards, and preflop VPIP/PFR flags.
"""

import re


class HandParser:
    """Parser for raw poker hand histories from Winamax and 888poker."""

    # ─── Winamax Regular Expression Patterns ────────────────────────────
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

    # ─── 888poker Regular Expression Patterns ───────────────────────────
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
        Parses an entire hand history file.

        Args:
            filepath: Path to the text file containing raw hand histories.

        Returns:
            List of dictionaries, one per valid hand, containing keys:
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
        Splits complete text into individual hand blocks.

        Detects the beginning of each hand by matching platform-specific headers.

        Returns:
            List of strings, each containing a complete hand.
        """
        split_pattern = re.compile(
            r"(?=Winamax Poker -|\*{5}\s*888poker Hand History)"
        )
        hands = split_pattern.split(text)
        return [h for h in hands if h.strip()]

    def _detect_platform(self, hand_text):
        """
        Identifies the source poker platform of an individual hand.

        Returns:
            'winamax', '888poker', or None if unrecognized.
        """
        if hand_text.strip().startswith("Winamax Poker"):
            return "winamax"
        elif "888poker Hand History" in hand_text:
            return "888poker"
        return None

    def _parse_winamax(self, hand_text):
        """
        Extracts hand data from a Winamax hand block.

        Returns:
            Dictionary with hand_id, platform, hero_cards, vpip, pfr,
            or None if extraction fails.
        """
        header_match = self.RE_WINAMAX_HEADER.search(hand_text)
        if not header_match:
            return None
        hand_id = header_match.group(1)

        dealt_match = self.RE_WINAMAX_DEALT.search(hand_text)
        hero_cards = dealt_match.group(1).strip() if dealt_match else None

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
        Extracts hand data from an 888poker hand block.

        Returns:
            Dictionary with hand_id, platform, hero_cards, vpip, pfr,
            or None if extraction fails.
        """
        header_match = self.RE_888_HEADER.search(hand_text)
        if not header_match:
            return None
        hand_id = header_match.group(1)

        dealt_match = self.RE_888_DEALT.search(hand_text)
        hero_cards = None
        if dealt_match:
            raw_cards = dealt_match.group(1).strip()
            hero_cards = raw_cards.replace(",", "").replace("  ", " ").strip()

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
        Evaluates Hero's preflop actions.

        VPIP = 1 if Hero voluntarily calls, raises, or bets.
        PFR  = 1 if Hero raises.
        Posting blinds (ante / small blind / big blind) does NOT count toward VPIP.

        Args:
            hand_text:     Full raw hand text.
            section_regex: Regex extracting the preflop section.
            action_regex:  Regex detecting Hero actions.

        Returns:
            Tuple (vpip, pfr) with integer flags (0 or 1).
        """
        vpip = 0
        pfr = 0

        section_match = section_regex.search(hand_text)
        if not section_match:
            return vpip, pfr

        preflop_text = section_match.group(1)
        actions = action_regex.findall(preflop_text)

        for action in actions:
            action = action.lower()
            if action in ("calls", "bets"):
                vpip = 1
            elif action == "raises":
                vpip = 1
                pfr = 1

        return vpip, pfr
