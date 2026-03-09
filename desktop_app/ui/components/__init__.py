from __future__ import annotations

"""Reusable themed UI components for the TK-OPS desktop shell."""

# Buttons
from .buttons import (
    DangerButton,
    FloatingActionButton,
    IconButton,
    PrimaryButton,
    SecondaryButton,
)

# Cards
from .cards import ActionCard, InfoCard, KPICard, ProfileCard

# Charts
from .charts import ChartWidget, MiniSparkline

# Data tables
from .tables import DataTable

# Tags & badges
from .tags import CountBadge, StatsBadge, StatusBadge, TagChip

# Inputs
from .inputs import (
    FilterDropdown,
    SearchBar,
    TagInput,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedTextEdit,
    ToggleSwitch,
)

# Layouts
from .layouts import (
    ContentSection,
    FormGroup,
    PageContainer,
    SplitPanel,
    TabBar,
    ThemedScrollArea,
)

# Dialogs
from .dialogs import PlaceholderDialog

# Media
from .media import (
    DragDropZone,
    FileUploaderWidget,
    ImageGrid,
    MediaPreview,
    ThumbnailCard,
    VideoPlayerWidget,
)

# Analytics
from .analytics import (
    DistributionChart,
    FunnelChart,
    HeatmapWidget,
    SentimentGauge,
    TrendComparison,
    WordCloudWidget,
)

# Operations
from .operations import (
    CalendarWidget,
    DeviceCard,
    LogViewer,
    RuleEditorWidget,
    TaskProgressBar,
    TimelineWidget,
)

# AI
from .ai_widgets import (
    AgentRoleSelector,
    AIConfigPanel,
    AIStatusIndicator,
    ModelPicker,
    PromptEditor,
    StreamingOutputWidget,
    TokenUsageDisplay,
)

__all__ = [
    # Buttons
    "PrimaryButton",
    "SecondaryButton",
    "IconButton",
    "DangerButton",
    "FloatingActionButton",
    # Cards
    "KPICard",
    "InfoCard",
    "ProfileCard",
    "ActionCard",
    # Charts
    "ChartWidget",
    "MiniSparkline",
    # Tables
    "DataTable",
    # Tags
    "StatusBadge",
    "TagChip",
    "StatsBadge",
    "CountBadge",
    # Inputs
    "SearchBar",
    "FilterDropdown",
    "TagInput",
    "ThemedLineEdit",
    "ThemedComboBox",
    "ThemedTextEdit",
    "ToggleSwitch",
    # Layouts
    "PageContainer",
    "SplitPanel",
    "TabBar",
    "ThemedScrollArea",
    "ContentSection",
    "FormGroup",
    # Dialogs
    "PlaceholderDialog",
    # Media
    "ImageGrid",
    "VideoPlayerWidget",
    "FileUploaderWidget",
    "DragDropZone",
    "ThumbnailCard",
    "MediaPreview",
    # Analytics
    "HeatmapWidget",
    "WordCloudWidget",
    "SentimentGauge",
    "FunnelChart",
    "TrendComparison",
    "DistributionChart",
    # Operations
    "TaskProgressBar",
    "RuleEditorWidget",
    "CalendarWidget",
    "TimelineWidget",
    "LogViewer",
    "DeviceCard",
    # AI
    "AIConfigPanel",
    "StreamingOutputWidget",
    "AgentRoleSelector",
    "ModelPicker",
    "PromptEditor",
    "TokenUsageDisplay",
    "AIStatusIndicator",
]
