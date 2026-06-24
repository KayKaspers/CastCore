"""ORM models. Importing this package registers every model on ``Base.metadata``.

As new modules land (stream jobs, sources, platforms, channels, …) import them here so
Alembic sees them.
"""

from app.db.base import Base
from app.models.audit import AuditEvent
from app.models.backup import Backup
from app.models.media import MediaItem, MediaProbe
from app.models.notification import Notification
from app.models.recording import Recording
from app.models.scheduler import SchedulerEntry
from app.models.settings import Setting, SetupState
from app.models.storage import SmbSource, StorageSource
from app.models.streaming import (
    Destination,
    FFmpegProfile,
    Input,
    Output,
    ProcessStatus,
    StreamJob,
)
from app.models.user import ApiToken, Role, Session, User, user_roles

__all__ = [
    "Base",
    "User",
    "Role",
    "Session",
    "ApiToken",
    "user_roles",
    "Setting",
    "SetupState",
    "AuditEvent",
    "FFmpegProfile",
    "Destination",
    "StreamJob",
    "Input",
    "Output",
    "ProcessStatus",
    "StorageSource",
    "SmbSource",
    "Backup",
    "MediaItem",
    "MediaProbe",
    "Notification",
    "Recording",
    "SchedulerEntry",
]
