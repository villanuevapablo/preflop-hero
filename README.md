# ♠ Preflop Hero

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Supported Platforms](https://img.shields.io/badge/Platforms-Winamax%20%7C%20888poker-brightgreen)](#-supported-platforms)
[![GTO Benchmarks](https://img.shields.io/badge/Strategy-6--Max%20NLHE-orange)](#-what-does-it-measure)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A lightweight, high-performance poker hand history parser and preflop strategy auditor. It processes raw text hand histories from **Winamax** and **888poker**, extracts hole cards and preflop decisions, calculates key **VPIP** and **PFR** metrics for the Hero, persists records in a local **SQLite** database, and compares your gameplay against theoretical **6-max No-Limit Hold'em GTO benchmarks**.

Includes both a **Python CLI engine** and a standalone, zero-dependency **Dark-Mode Web Dashboard**.

---

## 🎯 What Does It Measure?

Preflop decisions account for the vast majority of leaks in modern poker. **Preflop Hero** tracks and audits the three fundamental preflop indicators:

| Metric | Full Name | Description | 6-Max Optimal Target |
|:---|:---|:---|:---:|
| **VPIP** | *Voluntarily Put $ in Pot* | Percentage of hands where Hero voluntarily commits chips preflop (calls, bets, or raises). Walks and check-options in the Big Blind do not count. | **20% – 27%** |
| **PFR** | *Preflop Raise* | Percentage of hands where Hero enters the pot with an open-raise or a 3-bet/cold 4-bet. | **17% – 23%** |
| **PFR/VPIP Gap** | *Cold-Call Spread* | The mathematical spread: $\text{VPIP} - \text{PFR}$. Measures passive calling tendencies vs. aggressive initiative. | **3 – 6 pp** |

### Strategy Diagnostic Profiles

```
               [HIGH VPIP / LOW PFR] ──> Loose-Passive ("Calling Station")
               [LOW VPIP / LOW PFR]  ──> Too Tight ("Rock / Nit")
               [HIGH VPIP / HIGH PFR] ──> Overly Aggressive ("Maniac")
               [22% VPIP / 19% PFR]  ──> Optimal TAG (Tight-Aggressive) ✅
```

---

## 🚀 Quick Start

### Option 1: Web Dashboard (Zero Installation)

1. Open [`index.html`](file:///C:/Users/USUARIO/.gemini/antigravity/scratch/poker_analyzer/index.html) directly in any modern web browser.
2. Drag & drop your hand history text file (`history.txt`) or paste hands directly.
3. Click **"Analyze Hands"**.

> 🔒 **100% Client-Side Privacy**: All parsing and computation run locally in your browser. No hand histories, hole cards, or personal data leave your machine.

---

### Option 2: Python CLI & SQLite Pipeline

Run the analysis pipeline locally with standard Python (no third-party dependencies required):

```bash
python main.py
```

#### Sample Terminal Output:

```text
========================================================================
  ♠ ♥ ♦ ♣   PREFLOP HERO — STRATEGY AUDIT REPORT   ♣ ♦ ♥ ♠
========================================================================

#    HAND ID                        PLATFORM     CARDS      VPIP   PFR   
────────────────────────────────────────────────────────────────────────
1    20261104-001-001               winamax      Ah Kd      ✔      ✔     
2    20261104-001-002               winamax      7c 2d      ✘      ✘     
3    20261104-001-003               winamax      Jh Js      ✔      ✘     
4    987654321                      888poker     Qh Qd      ✔      ✔     
5    987654322                      888poker     9s 8s      ✔      ✘     
6    987654323                      888poker     4c 2h      ✘      ✘     

========================================================================
  📊  AGGREGATE METRICS
========================================================================
  Total Hands Analyzed:       6
  Hands with VPIP:            4  (66.67%)
  Hands with PFR:             2  (33.33%)
  PFR / VPIP Gap:             33.33 pp

========================================================================
  📐  6-MAX THEORETICAL BENCHMARKS
========================================================================
  Optimal VPIP:   20% – 27%
  Optimal PFR:    17% – 23%
  Optimal Gap:    3 pp – 6 pp

========================================================================
  🔍  STRATEGY DIAGNOSTICS & LEAK DETECTION
========================================================================

  [VPIP] ⚠️  HIGH
  VPIP 66.7% is above optimal (20-27%). You are playing too loose. Tighten your opening range from early positions (UTG, MP).

  [PFR] ⚠️  HIGH
  PFR 33.3% is above optimal (17-23%). Preflop aggression is excessively high. Trim speculative opens from early seats.

  [GAP] ⚠️  HIGH
  Gap 33.3 pp is above optimal (3-6 pp). Excessive cold-calling. Convert passive calls into 3-bets or folds.
========================================================================
```

---

## 🃏 Supported Platforms & Formats

| Platform | Format Signature | Hand Delimiter |
|:---|:---|:---|
| **Winamax** | `Winamax Poker - CashGame - HandId: #...` | `*** PRE-FLOP ***` ... `*** FLOP ***` |
| **888poker** | `***** 888poker Hand History for Game ... *****` | `** Dealing down cards **` ... `** Dealing Flop **` |

---

## 🏗️ Architecture

```
poker_analyzer/
├── index.html       # Standalone Glassmorphism Web App (SVG gauges & card renderer)
├── main.py          # CLI entry point orchestrating parser, database & analyzer
├── parser.py        # Regex-based hand extractor for Winamax & 888poker
├── database.py      # SQLite connection manager with duplicate prevention
├── analyzer.py      # Metric calculations & 6-max GTO diagnostic rules
├── history.txt      # Sample raw hand histories for testing
├── README.md        # Project documentation
└── .gitignore       # Git ignore rules (*.db, __pycache__, etc.)
```

### Relational Schema (`poker_stats.db`)

```sql
CREATE TABLE IF NOT EXISTS hand_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hand_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    hero_cards TEXT,
    vpip INTEGER NOT NULL,
    pfr INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hand_id, platform)
);
```

Duplicate hand histories are safely ignored using `INSERT OR IGNORE`.

---

## ⚙️ Requirements

- **Python 3.10+** (Standard libraries only: `sqlite3`, `re`, `os`, `sys`).
- No external pip dependencies required.
- Any modern web browser (Chrome, Firefox, Safari, Edge) for `index.html`.

---

## 📄 License

This project is open-source and released under the [MIT License](LICENSE).
