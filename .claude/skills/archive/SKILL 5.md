---
name: evaluate
description: Grade a finished deliverable, plan, or phase (architecture / execution / delivery) before declaring it done — and validate the gate that checked it. Two nested layers merged from Sebas's principles rubric (reasoning/EV/leverage) + Anthropic's eval-quality criteria. Use at a phase boundary for non-trivial work, or before trusting a new gate/benchmark/LLM-judge. Composes with plan-preflight (the ladder), karpathy-guidelines, grill-me.
license: MIT
---

# Evaluate

Two **nested** layers, not two scores to average. **Layer 1 grades the WORK** (was it done right?). **Layer 2 grades the JUDGE** (can I trust the check that said it was?). Most of Layer 2 already lives in the workspace rules — this skill is the rubric + the index, not a re-teach.

Depth follows the **verification ladder** (`plan-preflight`): trivial → skip · routine → Layer 1 self-score · high-impact / first delivery / stakeholder-cross-checked numbers → Layer 1 + Layer 2 by an **independent** agent (not self-review).

## Layer 1 — Principles eval (grades REASONING, not prose)
Score each 0–2; **total < 7 = FAIL**.
1. **First principles** — reasoned from the actual mechanics, or pattern-matched "what people usually do"? Cargo-cult without a stated reason = 0.
2. **EV discipline** — Impact × P(success) / Effort. Was the impact **ceiling estimated BEFORE** spending effort? A polished low-ceiling deliverable = 0.
3. **Sebas's time minimized** — hands back a **decision**, not homework. > 5 min of Sebas-work when 1 min was possible = 0.
4. **Verified, not plausible** — every claim/option checked against the **live source** (file read, API/gate run, price confirmed). "Sounds right" presented as fact = 0.
5. **Leverage** — was a 10x lever ignored: an existing script/skill, an automation, a delegation to agents, a reusable path instead of a one-off?

**Auto-fail** (regardless of score): invented statistic or unverified citation · an option infeasible for Sebas's real constraints (stack, infra, env) · optimized something whose impact ceiling was never estimated.

Output:
```
VERDICT: PASS | FAIL
SCORES: [1..5, one-line justification each]
BIGGEST MISS: [the single highest-leverage thing done wrong or skipped]
```

## Layer 2 — validate the eval/gate (only when building or trusting one)
A gate / benchmark / LLM-judge must clear the 8 eval-quality criteria before you trust it: *evaluability · coverage · realism · difficulty · redundancy · discriminative power · semantic ambiguity · data selection*. The three that are **not** already enforced elsewhere, so check them explicitly:
- **Discriminative power** — does it actually separate good from bad, or would it pass almost anything? (A gate that never fails proves nothing.)
- **Redundancy** — are checks duplicating signal without adding coverage? Cut them.
- **Semantic ambiguity** — can a criterion be read two ways? Pin the wording.

The rest is the workspace's existing anti-reward-hacking discipline — **apply it, don't restate it**: *meta-check* (inject a known defect, confirm the gate/judge catches it) · *verificador independiente* (re-implement the check apart from who produced the work) · *cap = canario* (report the crossed threshold, never tune it to pass) · *bidireccional* (watch fail-open AND fail-closed). Sources: project `CLAUDE.md` verificación anti-reward-hacking · `.memory/lessons.md` LESSON-008.

## Index — why nothing above is redundant
- Q1 / Q4 ≈ Reglas Fable #1–2 (fuente viva > memoria) + causa-raíz. Cross-referenced, not re-taught.
- Q2 **sharpens** Fable #5 (esfuerzo presupuestado) into EV / impact-ceiling-before-effort.
- Q3 / Q5 **sharpen** answer-first (#3) + karpathy simplicity into decision-not-homework + leverage.
- Layer 2 = the anti-reward-hacking block generalized from one project to any gate.
- **Dropped from the source deck** ("refine from user sessions daily"): no daily-session stream in this workspace → building it would be over-engineering (karpathy §2). Re-add only if that stream ever exists.
