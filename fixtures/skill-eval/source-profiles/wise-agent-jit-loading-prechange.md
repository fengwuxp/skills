# Wise-agent JIT loading before unique-heading query fallback

This frozen profile captures the relevant pre-change boundary. It is not an
installed Skill and is not current authority.

- Task-index rows can route exact or sufficiently similar task language to
  bounded reference sections.
- Explicit `--heading` selection can resolve one unique H2 or H3 section.
- Ordinary `--query` selection does not fall back to a unique section heading
  when no task-index row matches.
- Ambiguous, missing, cross-file, high-risk, and low-savings cases retain their
  existing stop or full-file fallback behavior.
- Token counts are static mixed-text estimates, not model billing telemetry or
  proof that end-to-end task cost decreased.
