# Process asset retention fixture

## Scenario

The payment team must decide whether a provider timeout should trigger an automatic retry or manual review. The owner has not decided yet.

## Process assets that must survive the pending decision

- 资产 ID: PA-001
  类型: constraint
  内容 / 作者原意: 重试必须保持幂等，不能因超时重复扣款。
  来源锚点: product-requirements.md#timeout
  状态: confirmed
  正典效力: handoff-only
  queue_state: active
  deferred_until:
  适用范围 / 时点 / 视角: provider-timeout; payment flow
  影响 / 下游消费者: retry design, ledger reconciliation, test cases
  升格条件 / 复审条件: provider commitment and idempotency evidence
  写回 / 交接位置: payment design handoff

- 资产 ID: PA-002
  类型: accepted-detail
  内容 / 作者原意: A single retry reduces transient failure but increases duplicate-charge investigation cost.
  来源锚点: observation-run-2026-08-27
  状态: candidate
  正典效力: process-only
  queue_state: active
  deferred_until:
  适用范围 / 时点 / 视角: provider timeout; current proposal
  影响 / 下游消费者: owner decision, support runbook
  升格条件 / 复审条件: same-runner observation and provider behavior evidence
  写回 / 交接位置: decision package DP-PA-001

- 资产 ID: PA-003
  类型: handoff
  内容 / 作者原意: The next artifact must include timeout, retry, manual-review, and reconciliation states.
  来源锚点: product-requirements.md#acceptance
  状态: confirmed
  正典效力: handoff-only
  queue_state: active
  deferred_until:
  适用范围 / 时点 / 视角: next payment design
  影响 / 下游消费者: product and engineering reviewers
  升格条件 / 复审条件: none; consume as handoff input
  写回 / 交接位置: product design review

## Question record

问题 ID: Q-PA-001
决策主题: provider-timeout retry policy
裁决动作: ask-owner
最终结论：pending
过程资产索引: PA-001, PA-002, PA-003
正典效力: process assets are not the business decision
替代记录 / replacement: none
