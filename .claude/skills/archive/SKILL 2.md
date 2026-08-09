---
name: plan-preflight
description: Disciplined plan-mode/preflight runbook for any project. Paste the session goal and run it; it routes by task type, drives triaged exploration + forensic input scrutiny + contradiction-checking, resolves dependencies deterministically, makes architecture calls, and writes a spec with stress-test/premortem + binary DoD gates, a tracked task list, and ExitPlanMode. Use at the start of any non-trivial task (code, data, or research) to plan before acting. Composes with grill-me and karpathy-guidelines.
---

# Plan Preflight

The user pastes a **session goal** and runs this. Your job: turn it into a verified, minimal, executable plan — autonomously. Read the project's `CLAUDE.md`, any SPEC it points to, and recalled memory **if present**; if none exist, treat the goal as the spec. Honor every project invariant.

**Default to action; match effort to complexity. Route first:**
- **Trivial / ≤1 file:** state the fix inline, skip the ritual.
- **No codebase (research/analysis):** skip reuse-hunt and file-dive; explore authoritative/external sources instead; DoD = verifiable claim-checks.
- **Greenfield (empty repo):** skip reuse and regression; lead with architecture + scaffolding.
- **Otherwise (multi-file/multi-phase, or touching a proven path):** run all phases.

## Operating contract (NON-NEG)
Think before acting (root cause → minimal change → downstream blast radius); don't assume, don't hide confusion, surface tradeoffs. **Minimum that solves it, nothing speculative, surgical — every changed line traces to the goal; clean up only your own mess.** Senior bar: "would a staff engineer call this overcomplicated?" → if yes, simplify. Nothing is "done" without a binary gate actually run. (See `karpathy-guidelines`.)

## Phase A — Explore (parallel, read-only)
**Triage first:** list candidate files/areas, rank by how directly the goal depends on them, deep-dive only the few it hinges on, skim or skip the rest. Under-reading and reading-everything are both failures; once a question is grounded, stop pulling files for it. Launch up to 3 Explore agents by focus (reuse code · the inputs/data · spec/intent · or external sources when there's no codebase); one agent when localized.

**Forensic deep-dive on the artifacts that matter — especially new or changed inputs.** Open them and dump their *real* structure (fields, headers, sample records — whatever the format exposes); never reason from the filename or an assumed schema. When two things are "the same kind" (two configs, two schemas, two APIs, two data drops), open **both** and diff.

## Phase B — Resolve dependencies deterministically
Walk the decision tree branch by branch. For each open question: answer it from code/data/context, cross-checking independent signals (labels **and** magnitudes, not one alone). **When sources disagree** (spec vs data, doc vs code, config vs config), the conflict is itself a finding — surface both values, reconcile from ground truth (data/code beats prose) or escalate the fork; never silently pick one. Keep a running list of what's **missing / unstated / assumed** → each is resolved from ground truth or carried into the spec. Only the genuinely indeterminable (true semantics, an external fact, a real scope/effort fork) goes to the user via `AskUserQuestion`, recommendation first. Never block on what's sitting in the file.

**Second look (before locking the design):** re-question your own findings once — what did I not open, which assumption is load-bearing, does each finding survive scrutiny? Re-investigate anything that wobbles, then move on. (See `grill-me`.)

## Phase C — Design (architecture calls)
- **Additive, fail-loud**: isolate new behavior from proven paths (a new module/endpoint/ingester rather than overloading a shared glob/schema an audited path assumes) — one instance of the rule; for in-place fixes, the smallest correct edit. Contaminating the proven path is the real risk.
- **Premortem the codebase/data, not just your plan**: find the edge case the current code silently mishandles and the *second* input shape it never anticipated. Name each failure mode now and pair it with a gate.
- Scope to the verifiable part; defer and **name** what would need a guess. A correct partial beats a complete-but-invented whole.

## Phase D — Write the spec (prompt contract)
Compact, scannable buckets: **Context/why · Findings** (with evidence) **· Architecture decision** (recommended only, and why) **· Phased decomposition** (files touched, reused utils with paths, output schema, integration points) **· Stress-test/premortem** (failure modes Fn → mitigating gate) **· DoD binary gates · Verification** (exact commands) **· Out-of-scope/deferred · Branch discipline** when relevant. Write to project convention or `docs/plans/<slug>.md`.

**DoD gate** = a concrete golden value where numeric; otherwise a reproducible command + its expected observable output. Never a no-op. Include a **regression gate** for any proven path you touch ("suite X still N/N", if a suite exists).

## Phase E — Task manager + gates (mandatory for multi-phase work)
Set up the to-do list before executing: one task per phase, each carrying its DoD gates. `in_progress` on start; **never mark `completed` until its gate is run and passes — show the output.** On a failing gate: stay in_progress, root-cause, fix, re-run.

**Code phases carry a review gate:** any task that writes/edits code includes, in its DoD, a `/code-review` pass on the staged diff before commit (`/code-review --fix` for cleanups); a diff touching a frozen/proven path makes it MANDATORY. Apply receiving-code-review: verify each finding against the code before adopting, push back with reasoning when wrong, no performative agreement. Data-ops / cadence / re-running validated code = N/A (no diff).

## Phase F — ExitPlanMode
Only after the spec is complete and every fork is resolved (via `AskUserQuestion` or grounded in data). Use `ExitPlanMode` to request approval (never a free-text "is this ok?"); if plan mode is unavailable, present the spec and request approval before executing. List the execution permissions needed.

## Pushbacks on the planning itself
- Don't over-ask: a fork with a conventional default isn't a question — pick it, state it, move on.
- Don't over-build: if you wrote "flexible/configurable/general" and the goal didn't ask for it, cut it.
- Don't declare a number/golden without computing it, or claim a gate passed without running it.
- If the goal is underspecified or self-contradictory, stop and name what's confusing — don't paper over it.
