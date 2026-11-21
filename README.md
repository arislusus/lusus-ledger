# lusus · 宏观判断公证链

这里只放**哈希、时间戳证明和已结算条目的原文**。判断在立案当天以哈希形式上链并交第三方盖时间戳，结算后公开原文，
任何人都能核对：它在那个时间之前就存在、措辞没改过、中间没删过条目。

本仓库内容是对宏观变量的可证伪判断记录，**不构成任何证券、期货或投资建议**。

## 结构

| 路径 | 内容 |
|---|---|
| `chain/<年>/<批次>.jsonl` | 每行一条：`seq`、编号、类型、来源（新立 / 补登）、条目日期、`leaf`、`prev`、`link`、上链时间（UTC） |
| `chain/.../*.jsonl.ots` | OpenTimestamps 证明（锚定比特币区块） |
| `chain/.../*.jsonl.tsr` | FreeTSA（RFC 3161）时间戳回执 |
| `reveals/<编号>.json` | 揭晓的原文 `payload`（含随机盐） |
| `verify.py` | 独立校验脚本，只用 Python 标准库 |

条目类型：`J` 判断，`TH` 检测条件（含证伪定义、读法与处置），`K` 结算记录，`FC` 过关概率，`PW` 判别力。

## 规则

- `leaf = SHA-256(payload 的 UTF-8 字节)`；`link_n = SHA-256(link_{n-1} ‖ leaf_n)`（按 32 字节拼接），`link_0` 为 64 个 0。
- `seq` 从 1 连续；`J`、`TH`、`K` 的编号各自从 1 连续。删掉任何一条都会断链或留下编号缺口。
- 每个批次文件整体交 OpenTimestamps 与 FreeTSA 盖章。批次文件里有链头 `link`，盖一个批次即证明了它之前的整条链。
- 条目不修改：修订是新条目，改判是新的结算记录，旧的原样保留。
- **补登**：公证链启用（2026-11-21）时账本里已有的条目。它们只证明「至迟在上链时已存在」，不证明立案时间，不应计入事前记录。
- **新立**：之后的条目。可信的事前记录 = 新立、且上链时间不晚于条目日期次日。
- 证伪的、作废的，和过关的一样揭晓。

## 自己校验

```bash
python3 verify.py                     # 链完整性、编号连续性、揭晓原文与 leaf 是否相符
ots verify chain/2026/<批次>.jsonl.ots   # 需 opentimestamps-client；也可上传到 https://opentimestamps.org
openssl ts -verify -data chain/2026/<批次>.jsonl -in chain/2026/<批次>.jsonl.tsr \
  -CAfile tsa/cacert.pem -untrusted tsa/tsa.crt
```

---

*English summary: hash-chained, externally timestamped (Bitcoin via OpenTimestamps + RFC 3161 via FreeTSA) record of
falsifiable macro calls by the pseudonym lusus. Payloads are revealed after settlement, failures included. Run
`python3 verify.py`. Not investment advice.*
