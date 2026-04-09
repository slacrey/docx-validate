# 文档检测服务开发计划（V2）

> 技术栈：**Python + FastAPI + python-docx + PostgreSQL/MySQL + MinIO + Celery**  
> 目标：基于“标准文档 + 规则/要求文档”，自动检测待检文档并输出问题清单与可下载批注文档。

---

## 1. 业务目标与范围

### 1.1 核心目标
围绕 `.docx` 文档实现自动化质检，覆盖以下四项：
1. **格式正确性**：标题、字号、字体、段落等是否符合规范。
2. **模板一致性**：待检文档是否与标准文档在样式与结构上保持一致。
3. **指定位置内容校验**：关键位置内容是否与要求文档/规则一致。
4. **问题批注导出**：将问题写回文档（批注或可替代标注）并支持下载。

### 1.2 非目标（MVP阶段）
- 不支持 `.doc`（仅 `.docx`）
- 不支持多语言智能语义纠错（仅规则与结构化比对）
- 不做在线协同编辑，仅做离线检测与报告输出

---

## 2. 总体技术架构

### 2.1 组件与职责
- **FastAPI（API 层）**：上传文件、创建任务、查询状态、下载报告/批注文档。
- **Celery Worker（任务层）**：异步执行文档解析、检测、批注生成。
- **Redis（队列与结果后端）**：Celery Broker / Backend。
- **PostgreSQL/MySQL（元数据层）**：任务、规则、问题、结果索引。
- **MinIO（对象存储层）**：模板文档、待检文档、检测报告、批注文档。
- **python-docx + lxml（引擎层）**：解析文档结构、样式、文本、表格与底层XML。

### 2.2 架构图（逻辑）
```text
Client
  -> FastAPI
      -> DB (templates/rules/tasks/issues/results)
      -> MinIO (upload/download object)
      -> Celery.enqueue(task_no)

Celery Worker
  -> MinIO.get(template, rule, input)
  -> Parser(normalize docx)
  -> Detector(style/template/position checks)
  -> Annotator(generate annotated.docx)
  -> MinIO.put(report.json, annotated.docx)
  -> DB.update(task, issues, result)
```

### 2.3 部署建议
- **开发环境**：Docker Compose（api + worker + redis + postgres/mysql + minio）
- **生产环境**：K8s（可选），API 与 Worker 分开扩容
- **配置管理**：`.env` + 分环境配置（dev/staging/prod）

---

## 3. 检测引擎设计（重点）

### 3.1 文档中间模型（Document IR）
为保证可比对性，先将文档转换为统一中间结构：
- `sections[]`: 标题树（level, title, index_path）
- `paragraphs[]`: 文本、对齐、缩进、行距、样式ID
- `runs[]`: 字体、字号、加粗、斜体、颜色
- `tables[]`: 行列、单元格文本、单元格样式
- `anchors[]`: 锚点文本、书签、段落索引

> 说明：先“归一化”再“比对”，可显著降低误报。

### 3.2 检测器拆分
1. **StyleChecker（格式正确性）**
   - 校验标题层级样式（H1/H2/H3）
   - 校验字体、字号、段落格式（行距、对齐、缩进）
   - 输出 issue_type=`STYLE_MISMATCH`

2. **TemplateChecker（模板一致性）**
   - 基于章节标题/锚点进行结构对齐
   - 对齐成功后逐字段比对样式
   - 输出 issue_type=`TEMPLATE_DIFF`

3. **PositionContentChecker（指定位置内容）**
   - 定位策略：`bookmark > anchor_text + offset > paragraph_index`
   - 支持 `exact | normalized | regex` 三种匹配模式
   - 输出 issue_type=`CONTENT_MISMATCH`

### 3.3 规则优先级
`任务显式规则 > 规则集默认值 > 模板推断规则 > 系统默认值`

### 3.4 容错规则
- 文本比较可配置：去空格、全半角归一、中文标点归一、大小写忽略
- 浮点样式容差（例如行距、缩进）可配置阈值

---

## 4. 规则配置（JSON Schema 建议）

```json
{
  "style_rules": {
    "heading_1": {"font": "黑体", "size_pt": 16, "bold": true, "align": "center"},
    "heading_2": {"font": "黑体", "size_pt": 14, "bold": true, "align": "left"},
    "body": {"font": "宋体", "size_pt": 12, "line_spacing": 1.5}
  },
  "template_rules": {
    "compare_fields": ["font", "size_pt", "bold", "align", "line_spacing"],
    "ignore_sections": ["封面日期", "页脚页码"]
  },
  "position_rules": [
    {
      "id": "company_name",
      "locator": {"type": "anchor_text", "value": "公司名称", "offset": 1},
      "match": {"mode": "exact", "expected": "示例科技有限公司"}
    }
  ],
  "tolerance": {
    "ignore_whitespace": true,
    "normalize_punctuation": true,
    "ignore_case": false
  }
}
```

---

## 5. 数据库设计（PostgreSQL/MySQL）

### 5.1 表结构
1. `document_template`
   - `id(pk)`, `name`, `version`, `object_key`, `status`, `created_by`, `created_at`
2. `detection_rule_set`
   - `id(pk)`, `name`, `version`, `rule_json`, `status`, `created_by`, `created_at`
3. `document_task`
   - `id(pk)`, `task_no(unique)`, `template_id`, `rule_set_id`, `input_object_key`, `status`, `progress`, `error_message`, `created_at`, `finished_at`
4. `document_issue`
   - `id(pk)`, `task_id(fk)`, `issue_code`, `issue_type`, `severity`, `location_path`, `anchor_text`, `expected_value`, `actual_value`, `suggestion`, `created_at`
5. `document_result`
   - `id(pk)`, `task_id(fk)`, `report_object_key`, `annotated_object_key`, `summary_json`, `created_at`

### 5.2 索引建议
- `document_task(task_no)` 唯一索引
- `document_issue(task_id, severity)` 组合索引
- `document_result(task_id)` 唯一索引

### 5.3 MinIO 对象路径规范
- `templates/{template_id}/{version}.docx`
- `rules/{rule_set_id}/{version}.json`
- `inputs/{task_no}/source.docx`
- `results/{task_no}/report.json`
- `results/{task_no}/annotated.docx`

---

## 6. API 设计（V1）

### 6.1 模板与规则
- `POST /api/v1/templates`：上传标准模板
- `POST /api/v1/rules`：创建规则集
- `GET /api/v1/rules/{id}`：查询规则详情

### 6.2 任务与结果
- `POST /api/v1/tasks`：提交待检文档 + template_id + rule_set_id
- `GET /api/v1/tasks/{task_no}`：任务状态（PENDING/RUNNING/SUCCESS/FAILED）
- `GET /api/v1/tasks/{task_no}/issues`：问题列表（分页）
- `GET /api/v1/tasks/{task_no}/download/report`：下载 JSON/CSV 报告
- `GET /api/v1/tasks/{task_no}/download/annotated`：下载带批注文档

### 6.3 响应规范
统一返回：
```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

错误返回：
```json
{
  "code": 40001,
  "message": "invalid rule config",
  "data": null
}
```

---

## 7. 异步任务编排（Celery）

### 7.1 任务链
`validate_document_task(task_no)`：
1. 更新任务状态为 RUNNING
2. 下载模板、规则、待检文档
3. 文档解析与归一化
4. 执行三类检测并汇总 issue
5. 生成 `report.json`
6. 生成 `annotated.docx`（或高亮替代版本）
7. 上传结果到 MinIO
8. 持久化 issue/result 并置任务 SUCCESS

### 7.2 失败与重试
- 自动重试：网络类错误（MinIO/Redis抖动）
- 不重试：规则格式错误、文档损坏
- 最大重试次数：3（指数退避）

### 7.3 幂等控制
- 以 `task_no` 做幂等键，防止重复执行
- 重复请求返回已有任务结果

---

## 8. 批注输出设计

### 8.1 批注能力分级
- **优先方案**：真实批注（若库能力满足）
- **兼容方案**：高亮 + 尾注说明 + `issue_id` 映射

### 8.2 问题描述模板
每个问题包含：
- 问题类型（STYLE/TEMPLATE/CONTENT）
- 位置（章节/段落索引/锚点）
- 期望值 vs 实际值
- 修复建议

### 8.3 下载能力
- `report.json`（机器可读）
- `report.csv`（业务可读）
- `annotated.docx`（可视化整改）

---

## 9. 安全、性能与可观测

### 9.1 安全
- 文件白名单：仅 `.docx`
- 文件大小限制（例如 20MB）
- MinIO 私有桶 + 时效签名 URL
- JWT 鉴权 + 操作审计日志

### 9.2 性能
- 单任务超时：120~300 秒（按文档大小可配）
- Worker 并发：`CPU核数 * 2` 起步压测后调优
- 大文档分阶段检测，及时上报进度

### 9.3 可观测
- 结构化日志：`trace_id/task_no/stage`
- 关键指标：任务成功率、平均耗时、误报率、队列积压长度
- 告警：任务失败率阈值告警 + 队列堆积告警

---

## 10. 研发排期（8 周）

### 第 1-2 周：基础设施
- FastAPI 工程骨架、数据库迁移、MinIO/Redis/Celery 接入
- 模板/规则/任务 API 初版

### 第 3-4 周：检测引擎 MVP
- Parser + IR
- StyleChecker + PositionContentChecker
- 任务状态与问题列表查询

### 第 5-6 周：一致性比对与批注
- TemplateChecker
- annotated.docx 导出
- 报告导出（JSON/CSV）

### 第 7-8 周：稳定性与上线
- 压测与性能优化
- 安全与审计
- 灰度上线与运维文档

---

## 11. 测试计划

### 11.1 单元测试
- 规则解析、定位器、比较器（exact/normalized/regex）
- 样式字段比较（字体、字号、行距、对齐）

### 11.2 集成测试
- API 上传 + 异步任务 + 结果下载全链路
- MinIO 故障、Redis 抖动、任务重试验证

### 11.3 回归数据集
准备 3 类样本集：
- 标准合规样本（应全通过）
- 轻微偏差样本（应产出 WARN）
- 严重违规样本（应产出 ERROR）

---

## 12. 验收标准（DoD）
1. 上传模板、规则、待检文档后可创建并完成任务。
2. 三类检测均可输出结构化问题列表。
3. 可下载报告（JSON/CSV）及批注/高亮文档。
4. 任务失败可追踪、可重试、结果可回放。
5. 在 10 页以内普通文档，平均处理时长满足预期（可设SLO）。

---

## 13. 风险与应对
- **批注能力限制**：python-docx 对复杂批注写入能力有限  
  **应对**：先做能力验证 PoC；必要时采用“高亮 + 尾注 + 外部报告”组合。
- **样式继承复杂导致误报**  
  **应对**：增加样式归一化层、忽略项配置、人工复核开关。
- **定位不稳定**  
  **应对**：多策略定位与回退链（bookmark -> anchor -> index）。
- **大文档性能波动**  
  **应对**：分阶段检测、并发调优、超时与熔断策略。

---

## 14. 推荐落地顺序（可直接执行）
1. 先打通上传/任务/下载主链路（不做全部检测能力）。
2. 先实现格式检测与指定位置检测，再补模板一致性。
3. 先输出 `report.json`，再迭代 `annotated.docx` 的完整批注能力。
4. 最后做性能与可观测性加固，进入试运行。
