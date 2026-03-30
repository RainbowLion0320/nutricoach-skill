# Archive Directory

此目录存放已废弃/历史版本的脚本，仅作备份保留，不再维护。

## 文件说明

| 文件 | 废弃原因 | 替代方案 |
|------|---------|---------|
| `web_server_v3.py` | 与 `web_server.py` 重复，且未被使用 | 使用 `web_server.py` |
| `migrate_db.py` | 一次性迁移脚本，已完成历史使命 | 数据库结构已稳定 |
| `migrate_body_metrics.py` | 一次性迁移脚本，已完成 | 表结构已更新 |
| `update_food_database.py` | 功能被 `fill_food_defaults.py` 替代 | 使用 `fill_food_defaults.py` |

**注意：** 这些脚本可能包含过时的代码逻辑，不建议直接使用。
