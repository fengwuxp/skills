# 安全工程来源地图

## 使用时机

引用公开安全框架、验证标准、协议或支付数据安全基线时读取。使用前按目标环境、版本、法域和组织责任复核。

## 不适用场景

- 不用来源名称替代项目威胁模型、合同、法律意见、目标环境配置或生产证据。
- 不把行业清单全量复制进交付；只吸收当前风险需要的控制与验证方法。

## 读取后必须产出

- 来源、版本/发布日期、核验日期、适用范围、采用项与不采用项。
- 需要专业 Owner 裁决的适用性和时效风险。

## 需要继续读取的 reference

- 场景选择读 `security-scenario-routing.md`。
- 将来源映射为项目控制与证据时读 `security-risk-control-and-evidence.md`。

## 公开来源

| 来源 | 版本/日期 | 本 Skill 吸收 | 边界 |
| --- | --- | --- | --- |
| [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) | NIST CSF 2.0，2024 | Govern、Identify、Protect、Detect、Respond、Recover 的完整治理闭环 | 自愿框架，不替代组织风险责任或监管判断 |
| [NIST Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final) | NIST SP 800-218 v1.1，2022 | 安全开发、供应链、构建制品和缺陷响应基线 | 需映射到项目 SDLC 和真实工具证据 |
| [OWASP SAMM](https://owaspsamm.org/model/) | v2，持续维护 | 软件安全治理、设计、实现、验证与运营能力模型 | 成熟度模型不证明单个系统安全 |
| [OWASP ASVS](https://github.com/OWASP/ASVS/releases/tag/v5.0.0) | OWASP ASVS 5.0.0，2025-05-30 | Web 应用与服务的可验证安全要求 | 按应用类型和风险裁剪，不机械全量套用 |
| [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) | OWASP API Security Top 10 2023 | API 对象/功能授权、资源滥用、业务流和资产管理风险入口 | 风险目录，不是完整验收标准 |
| [NIST Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final) | NIST SP 800-207，2020 | 不因网络位置隐式信任，持续校验主体、设备、资源与策略 | 不要求为“零信任”口号重建全部架构 |
| [PCI Security Standards Council Document Library](https://www.pcisecuritystandards.org/document_library/) | PCI DSS v4.0.1，2024 | 支付账户数据环境的保护与验证基线 | 只覆盖其适用数据环境，不替代完整资金安全、支付语义或合规评估 |
| [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446) | TLS 1.3，2018 | 传输机密性、完整性和握手安全边界 | 不自动提供业务授权、防重放、幂等或端到端消息真实性 |
| [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700) | OAuth 2.0 Security Best Current Practice，2025 | OAuth 威胁模型、弃用不安全模式和客户端/授权服务器安全建议 | 需结合实际 grant、客户端类型、部署与 provider 契约 |
| [CISA Secure by Design](https://www.cisa.gov/securebydesign) | 持续维护 | 默认安全、产品责任和减少用户安全负担 | 原则性倡议，不替代项目控制实现与验证 |

以上公开来源于 2026-08-10 核验索引与版本。时效性来源在正式交付前重新核验；任何来源都不替代安全、法务、合规、隐私、支付、财务或生产 Owner 的适用性决定。
