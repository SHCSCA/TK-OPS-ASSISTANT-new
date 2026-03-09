from __future__ import annotations

# pyright: basic, reportMissingImports=false

"""自动化领域服务导出。"""

from .service import (
    AutoReplyLogDTO,
    AutoReplyRuleDTO,
    AutomationConfigDTO,
    AutomationService,
    AutomationStatusDTO,
    AutomationTaskDTO,
    CollectionTaskDTO,
    DateRangeDTO,
    ScheduledPostDTO,
)

__all__ = [
    "AutoReplyLogDTO",
    "AutoReplyRuleDTO",
    "AutomationConfigDTO",
    "AutomationService",
    "AutomationStatusDTO",
    "AutomationTaskDTO",
    "CollectionTaskDTO",
    "DateRangeDTO",
    "ScheduledPostDTO",
]
