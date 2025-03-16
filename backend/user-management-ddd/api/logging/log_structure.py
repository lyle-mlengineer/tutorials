from typing import Optional

from pydantic import BaseModel


class BaseLogRecord(BaseModel):
    timestamp: Optional[str] = None
    level: Optional[str] = None
    message: Optional[str] = None
    environment: Optional[str] = None


class LogRecord(BaseLogRecord):
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    service: Optional[str] = None


class Error(BaseModel):
    code: Optional[str] = None
    details: Optional[str] = None


class ErrorLogRecord(LogRecord):
    error: Error
