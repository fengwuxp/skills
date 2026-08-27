# Mixed answer intent fixture

## Scenario

Owner 对两个候选回答 `A + 部分 B`：先救人，同时保留 B 中对阻路者短促出手的部分；没有确认是否命中、逼退或解除控制。

## Expected decision record

问题 ID: Q-INTENT-001
当前交付: 场景动作骨架
设计分辨率: 动作意图
裁决动作: ask-owner
最终结论：confirmed
行动意图: 先接近并带人撤开；受阻后朝阻路者短促出手，试图争取空隙
结果：pending
queue_state: active
下一阶段输入: 具体招式、是否命中、对手如何截断和控制另行设计

记录不得把“试图争取空隙”写成已经逼退、命中或解除控制；组合答案不推定命中与结果。
