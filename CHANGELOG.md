# Health Coach Changelog

> 精简记录关键变更，避免遗忘。按时间倒序，只保留重要决策和 breaking changes。

---

## 2026-03-29

### 硬编码问题修复 - Phase 1 & 2 完成
- **审计**: 发现 142 处硬编码的 `row[n]` 数据库列索引
- **方案**: 创建 `db_schema.py` 集中管理所有表结构定义
- **修复完成** (12 个文件):
  - `pantry_manager.py` - 使用 `PANTRY_COLUMNS`
  - `meal_logger.py` - 使用 `MEALS_COLUMNS`, `FOOD_ITEMS_COLUMNS`, `CUSTOM_FOODS_COLUMNS`
  - `body_metrics.py` - 使用 `BODY_METRICS_COLUMNS`
  - `food_analyzer.py` - 使用 `CUSTOM_FOODS_COLUMNS`
  - `diet_recommender.py` - 使用 `CUSTOM_FOODS_COLUMNS`
  - `export_data.py` - 使用 `MEALS_COLUMNS`, `FOOD_ITEMS_COLUMNS`
  - `smart_recipe.py` - 使用 `PANTRY_COLUMNS`, `CUSTOM_FOODS_COLUMNS`
  - `food_matcher.py`, `report_generator.py` - 基础修复
- **配置**: 默认值集中到 `DEFAULTS` 字典
- **文档**: 创建 `HARDCODING_AUDIT.md` 记录审计结果

### 测试验证完成
- **修复测试脚本**: 更新 `sys.path` 以支持新的模块结构
- **测试通过**:
  - `test_barcode_match.py` - 条形码匹配场景
  - `test_ocr_flow.py` - OCR 结果匹配
  - `test_silent_scan.py` - 静默扫描模式
- **模块导入测试**: 所有核心模块正常导入
- **Web 模块测试**: 配置、路由、工具函数正常

### 模块化重构完成 ( web_server.py v3 )
- **重构**: web_server.py 从 968 行精简到 1459 行（模块化后）
- **分离**:
  - `templates/dashboard.html` - HTML 模板
  - `scripts/web/static/style.css` - CSS 样式
  - `scripts/web/static/app.js` - JavaScript
  - `scripts/web/routes.py` - API 路由
  - `scripts/web/utils.py` - 工具函数
  - `scripts/web/config.py` - 配置常量
- **架构**: 符合 Flask 最佳实践，易于扩展
- **版本**: TEMPLATE_VERSION 递增到 008

### 代码结构分析 ( REFACTOR.md )
- **问题**: web_server.py 968 行过于臃肿（HTML 模板嵌入）
- **分析**: 其他脚本 285-562 行，结构合理
- **建议**: 短期优化结构，长期模块化分离
- **文档**: 创建 REFACTOR.md 记录重构方案


### Pantry UI 精简 ( web_server.py )
- **优化**: 删除食材卡片上的保质期显示（与过期提醒冗余）
- **版本**: web_server.py TEMPLATE_VERSION 递增到 007

### Pantry 保质期逻辑优化 ( pantry_manager.py, web_server.py )
- **改进**: 编辑界面只允许修改生产日期和保质期，过期日期自动计算
- **避免**: 三个日期都可修改导致的计算错误
- **版本**: web_server.py TEMPLATE_VERSION 递增到 006

### Pantry UI 精简优化 ( web_server.py )
- **优化**: 整合【编辑】和【使用】按钮为单个【编辑】按钮
- **设计**: 编辑模态框内嵌使用功能区域，UI 更精简
- **版本**: web_server.py TEMPLATE_VERSION 递增到 005

### Pantry 编辑功能修复 ( pantry_manager.py )
- **问题**: `check_remaining` 查询遗漏 `purchase_date` 字段，导致编辑按钮参数传递错误
- **解决**: 添加 `purchase_date` 到查询和返回数据
- **版本**: web_server.py TEMPLATE_VERSION 递增到 004

### Pantry 编辑功能 ( pantry_manager.py, web_server.py )
- **功能**: Web UI 食材管理页面支持编辑生产日期、过期日期、储藏位置、备注
- **后端**: 新增 `pantry_manager.py update` 命令
- **前端**: 新增编辑模态框和 `/api/pantry/update` 接口
- **版本**: web_server.py TEMPLATE_VERSION 递增到 003

### Pantry 分类字段修复 ( pantry_manager.py )
- **问题**: `check_remaining` 未返回 `category` 字段，导致 Web UI 显示为"其他"
- **解决**: 查询中添加 `c.food_group` 并映射到 `category` 字段
- **版本**: web_server.py TEMPLATE_VERSION 递增到 002

### Pantry 自动过期日期 ( pantry_manager.py, web_server.py )
- **问题**: 添加食材时需要手动输入过期日期
- **解决**: 优先从食物数据库获取保质期，其次按储藏位置使用默认值
- **默认值**: 冰箱7天/冷冻90天/干货区30天/台面5天
- **Web UI**: 添加版本号机制 (TEMPLATE_VERSION) 解决模板缓存问题

---

## 2026-03-28

### Web Dashboard v2 发布
- **重构**: 页签式界面 (概览/食材管理/体重记录)
- **新增**: Pantry 按分类筛选视图（蛋白质/蔬菜/碳水/水果/乳制品/脂肪）
- **优化**: 删除 v1 版本，统一维护 v2

---

## 2026-03-27

### v2.0 功能完成
- **新增**: Pantry 库存管理（位置追踪、过期提醒、使用扣减）
- **新增**: 智能菜谱推荐（基于库存和营养缺口）
- **新增**: OCR 食品识别（Kimi Vision + macOS Vision 双引擎）
- **数据**: 569 种中餐食物营养数据库

---

## 2026-03-16

### v1.0 基础功能
- 用户档案管理（BMR/TDEE 自动计算）
- 体重记录与趋势分析
- 饮食日志与营养追踪
- 饮食推荐系统

---

## 约定

- **版本号**: 日期格式 `YYYY-MM-DD-NNN`
- **模板缓存**: 修改 web_server.py HTML 时同步递增 TEMPLATE_VERSION
- **文档同步**: 功能变更 → 更新 FEATURE_GUIDE.md → 更新 CHANGELOG.md
