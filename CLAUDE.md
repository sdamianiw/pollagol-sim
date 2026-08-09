# Pollagol SIM — CLOSED

Deterministic predictor for a private FIFA World Cup 2026 pool on pollaya.com: per match, the scoreline that maximized **expected competition points** (not the most probable score), plus 5 pre-tournament locked picks. **Tournament finished 2026-07-21 — rank 1/27, 410 pts, prize won. Frozen; no further cadence.**

## I3 — NO result→model feedback (cardinal invariant, HARD)
No code path may read match results / `predictions/decisions.csv` and write a MODEL parameter (`fit_lambdas`, optimizer weights, ρ, σ, μ_eff, context factors, or any constant in `src/model.py`, `src/optimizer.py`, `src/strength.py`, `src/context.py`). Results flow ONE way: `decisions.csv` → `src/decision_score.py` → points/Brier, read-only. The engine consumes market odds only, never an outcome. Model constants change only via a separately-approved mechanical fix — never from live results. Structural guard, enforced by review/grep.

## Layout
`src/` per-match engine · `pool/` E[prize] engine · `council/` locked-pick council · `evals/` backtest · `predictions/` outputs + decisions.csv · `data/` cache + snapshots · `memory/` durable facts · `tasks/` todo + lessons.

Full session record: `tasks/HANDOFF.md`, `tasks/lessons.md` (L1–L63), and git history. Operating rules that outlived this project now live in `~/.claude/CLAUDE.md` and the global skills; the pool-specific ones in `~/.claude/projects/…-Pollagol-SIM/memory/` (closed-tournament detail under its `archive/`).
