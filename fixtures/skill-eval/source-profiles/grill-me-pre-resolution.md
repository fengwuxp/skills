# grill-me pre-resolution source profile

## Purpose

This profile freezes the project-owned Grill behavior before the resolution, deferral, intent/result, and writeback-checkpoint repair. It is an evaluation source, not an installed Skill or current authority.

## Baseline Instructions

Before implementation, close key branches until the Owner and Agent reach shared understanding.

- Check facts, current implementation, historical decisions, risks, and red lines before asking.
- Reuse confirmed, rejected, or semantically duplicate decisions; do not rephrase and ask again.
- Ask only one unresolved Owner decision at a time and provide a recommendation, evidence, impact, and stop point.
- Use `fact-confirmed`, `decision-reused`, `self-decided`, or `ask-owner`; preserve the final conclusion as confirmed, rejected, pending, self-decided, conflict, or superseded.
- Record every question, evidence, user answer, final conclusion, red lines, next-stage input, and affected writeback position.
- Retain process assets whose omission would change later artifacts, handoff, verification, risk, or responsibility. Process assets do not replace the final decision or domain authority.
- High-fidelity questions first require the smallest observable artifact; returned evidence goes back to the original question.
- Stop when key branches are confirmed, rejected, self-decided, or explicitly pending, then output a decision snapshot.

The baseline has no explicit current-deliverable resolution gate, no active/deferred queue state, no deferred reactivation condition, no required separation between action intent and result, and no derived-writeback checkpoint.
