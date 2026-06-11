# preferences.md — how to work with Sebas

- **Plan-first, then build.** 3+ steps or architectural choices → plan and get approval first. If something
  goes sideways, STOP and re-plan rather than pushing on.
- **Verify before claiming done.** Always a command + output + PASS/FAIL. Never "should/probably" without a
  number or cited source.
- **Surgical / minimal.** Minimum code that solves it; 80/20; nothing speculative ("just in case" = no).
- **Provenance always.** Source + UTC + URL on every datum; `PROBABLE` for unconfirmed; ≥2 sources on
  critical inputs; never fabricate news.
- **HITL.** I recommend; Sebas approves and submits. I never finalize.
- **Edit approval = manual** (Sebas reviews each edit). Don't assume auto-apply.
- **Push back** when something is wrong, risky, over/under-scoped, or inconsistent — grounded in evidence,
  before building.
- **Self-improvement.** After a correction, log the pattern + a preventing rule in `tasks/lessons.md`.
-**Goal-Driven Execution**
Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

"Add validation" → "Write tests for invalid inputs, then make them pass"
"Fix the bug" → "Write a test that reproduces it, then make it pass"
"Refactor X" → "Ensure tests pass before and after"
For multi-step tasks, state a brief plan:

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
