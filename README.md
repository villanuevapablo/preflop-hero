# ♠ Poker Preflop Analyzer

Analizador de manos de poker que procesa historiales de **Winamax** y **888poker**, calcula las estadísticas **VPIP** y **PFR** del jugador principal (Hero), y evalúa la estrategia preflop contra los estándares óptimos de mesas 6-max.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-green?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 ¿Qué mide?

| Estadística | Descripción | Rango Óptimo 6-max |
|---|---|---|
| **VPIP** | % de manos jugadas voluntariamente preflop | 20–27% |
| **PFR** | % de manos con raise preflop | 17–23% |
| **Brecha** | Diferencia VPIP − PFR (indica cold-call) | 3–6pp |

## 🚀 Uso

### Interfaz Web (recomendado)

1. Abre `index.html` en tu navegador
2. Arrastra tu archivo de historiales o pega el texto
3. Haz clic en **"Analizar Manos"**

> Todo se procesa localmente en tu navegador. No se envía nada a ningún servidor.

### Línea de comandos (CLI)

```bash
python main.py
```

Procesa `history.txt`, almacena en SQLite y genera un reporte en consola.

## 📂 Estructura

```
poker_analyzer/
├── index.html      # App web visual (drag & drop)
├── main.py         # Script principal CLI
├── parser.py       # Motor de extracción regex
├── database.py     # Persistencia SQLite
├── analyzer.py     # Cálculo de estadísticas
└── history.txt     # Manos de ejemplo
```

## 🃏 Plataformas soportadas

- **Winamax** — formato con `HandId: #...` y `*** PRE-FLOP ***`
- **888poker** — formato con `888poker Hand History for Game ...` y `** Dealing down cards **`

## 📐 Arquitectura

- **Motor de Extracción**: Parser basado en expresiones regulares que fragmenta el archivo, extrae cartas del Hero y evalúa acciones preflop.
- **Módulo de Persistencia**: Esquema SQLite con constraint `UNIQUE(hand_id, platform)` para ignorar duplicados.
- **Módulo de Análisis**: Calcula porcentajes y evalúa la brecha VPIP-PFR contra estándares matemáticos.

## ⚙️ Requisitos

- Python 3 (solo librerías estándar: `sqlite3`, `re`, `os`)
- Navegador moderno para la interfaz web

---

Hecho con ♠ ♥ ♦ ♣
