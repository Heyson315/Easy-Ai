"""
Session Management for M365 Security Toolkit
============================================

This module provides centralized session management for tracking user operations,
audit sessions, and maintaining comprehensive audit trails across the toolkit.

Features:
- Unique session ID generation
- Session metadata tracking (user, operation, timestamp)
- Session persistence to JSON
- Query capabilities for session history
- Integration with cost tracking and audit logging

Author: Rahman Finance and Accounting P.L.LLC
Created: November 2025
"""

import json
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import os
import getpass


class Session:
    """Represents a single user session with metadata and tracking"""

    def __init__(
        self,
        session_id: Optional[str] = None,
        user: Optional[str] = None,
        operation_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new session.

        Args:
            session_id: Unique session identifier (auto-generated if not provided)
            user: Username or identifier (auto-detected if not provided)
            operation_type: Type of operation (audit, analysis, remediation, etc.)
            metadata: Additional session metadata
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.user = user or self._detect_user()
        self.operation_type = operation_type or "general"
        self.metadata = metadata or {}
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.status = "active"
        self.events: List[Dict[str, Any]] = []

    def _detect_user(self) -> str:
        """Detect current user from environment"""
        try:
            return getpass.getuser()
        except Exception:
            return os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

    def add_event(self, event_type: str, description: str, data: Optional[Dict[str, Any]] = None):
        """
        Add an event to the session timeline.

        Args:
            event_type: Type of event (start, progress, error, complete)
            description: Human-readable event description
            data: Additional event data
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "data": data or {},
        }
        self.events.append(event)

    def complete(self, status: str = "success"):
        """
        Mark session as complete.

        Args:
            status: Final session status (success, error, cancelled)
        """
        self.end_time = datetime.now()
        self.status = status
        self.add_event("complete", f"Session completed with status: {status}")

    def get_duration(self) -> Optional[timedelta]:
        """Get session duration"""
        if self.end_time:
            return self.end_time - self.start_time
        return datetime.now() - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "user": self.user,
            "operation_type": self.operation_type,
            "metadata": self.metadata,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "duration_seconds": self.get_duration().total_seconds() if self.end_time else None,
            "events": self.events,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary"""
        session = cls(
            session_id=data["session_id"],
            user=data["user"],
            operation_type=data["operation_type"],
            metadata=data.get("metadata", {}),
        )
        session.start_time = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            session.end_time = datetime.fromisoformat(data["end_time"])
        session.status = data["status"]
        session.events = data.get("events", [])
        return session


class SessionManager:
    """
    Centralized session management for the M365 Security Toolkit.

    Manages session lifecycle, persistence, and querying capabilities.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize session manager.

        Args:
            storage_path: Path to session storage file (default: output/sessions/session_log.json)
        """
        self.storage_path = Path(storage_path or "output/sessions/session_log.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.active_sessions: Dict[str, Session] = {}
        self.load_sessions()

    def load_sessions(self):
        """Load session history from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Load any active sessions back into memory
                    for session_data in data:
                        if session_data.get("status") == "active":
                            session = Session.from_dict(session_data)
                            self.active_sessions[session.session_id] = session
            except (json.JSONDecodeError, FileNotFoundError):
                pass

    def save_sessions(self):
        """Persist all sessions to storage"""
        # Load existing sessions to preserve history
        all_sessions = []
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    all_sessions = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Update or add active sessions
        session_map = {s["session_id"]: s for s in all_sessions}
        for session in self.active_sessions.values():
            session_map[session.session_id] = session.to_dict()

        # Save back to file
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(list(session_map.values()), f, indent=2)

    def create_session(
        self, operation_type: str, user: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Create a new session.

        Args:
            operation_type: Type of operation (audit, analysis, remediation, etc.)
            user: Username (auto-detected if not provided)
            metadata: Additional session metadata

        Returns:
            New Session object
        """
        session = Session(user=user, operation_type=operation_type, metadata=metadata)
        self.active_sessions[session.session_id] = session
        session.add_event("start", f"Session started for {operation_type}")
        self.save_sessions()
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get an active session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session object if found, None otherwise
        """
        return self.active_sessions.get(session_id)

    def complete_session(self, session_id: str, status: str = "success"):
        """
        Complete a session and remove from active sessions.

        Args:
            session_id: Session identifier
            status: Final status (success, error, cancelled)
        """
        session = self.active_sessions.get(session_id)
        if session:
            session.complete(status)
            self.save_sessions()
            # Remove from active sessions
            del self.active_sessions[session_id]

    def get_session_history(
        self, operation_type: Optional[str] = None, user: Optional[str] = None, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Query session history with filters.

        Args:
            operation_type: Filter by operation type
            user: Filter by user
            days: Number of days to look back

        Returns:
            List of session dictionaries matching filters
        """
        if not self.storage_path.exists():
            return []

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                all_sessions = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

        cutoff = datetime.now() - timedelta(days=days)
        filtered = []

        for session_data in all_sessions:
            start_time = datetime.fromisoformat(session_data["start_time"])
            if start_time < cutoff:
                continue

            if operation_type and session_data.get("operation_type") != operation_type:
                continue

            if user and session_data.get("user") != user:
                continue

            filtered.append(session_data)

        return filtered

    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get session usage statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        sessions = self.get_session_history(days=days)

        if not sessions:
            return {
                "total_sessions": 0,
                "by_operation_type": {},
                "by_user": {},
                "by_status": {},
                "avg_duration_seconds": 0,
            }

        # Calculate statistics
        by_operation = defaultdict(int)
        by_user = defaultdict(int)
        by_status = defaultdict(int)
        total_duration = 0
        completed_count = 0

        for session in sessions:
            by_operation[session.get("operation_type", "unknown")] += 1
            by_user[session.get("user", "unknown")] += 1
            by_status[session.get("status", "unknown")] += 1

            if session.get("duration_seconds"):
                total_duration += session["duration_seconds"]
                completed_count += 1

        avg_duration = total_duration / completed_count if completed_count > 0 else 0

        return {
            "total_sessions": len(sessions),
            "active_sessions": len(self.active_sessions),
            "by_operation_type": dict(by_operation),
            "by_user": dict(by_user),
            "by_status": dict(by_status),
            "avg_duration_seconds": round(avg_duration, 2),
        }

    def print_statistics(self, days: int = 30):
        """Print formatted session statistics"""
        stats = self.get_statistics(days)

        print("\n" + "=" * 80)
        print(f"  Session Statistics - Last {days} Days")
        print("=" * 80)

        print(f"\n📊 Overview:")
        print(f"   Total Sessions: {stats['total_sessions']}")
        print(f"   Active Sessions: {stats['active_sessions']}")
        print(f"   Average Duration: {stats['avg_duration_seconds']:.1f} seconds")

        print(f"\n🔧 By Operation Type:")
        for op_type, count in sorted(stats["by_operation_type"].items(), key=lambda x: x[1], reverse=True):
            print(f"   {op_type}: {count}")

        print(f"\n👤 By User:")
        for user, count in sorted(stats["by_user"].items(), key=lambda x: x[1], reverse=True):
            print(f"   {user}: {count}")

        print(f"\n✅ By Status:")
        for status, count in sorted(stats["by_status"].items(), key=lambda x: x[1], reverse=True):
            print(f"   {status}: {count}")

        print("=" * 80 + "\n")


# Global session manager instance
_global_manager: Optional[SessionManager] = None


def get_session_manager(storage_path: Optional[str] = None) -> SessionManager:
    """Get or create global session manager instance"""
    global _global_manager
    if _global_manager is None:
        _global_manager = SessionManager(storage_path=storage_path)
    return _global_manager


def create_session(operation_type: str, metadata: Optional[Dict[str, Any]] = None) -> Session:
    """
    Convenient function to create a new session.

    Args:
        operation_type: Type of operation
        metadata: Additional metadata

    Returns:
        New Session object
    """
    manager = get_session_manager()
    return manager.create_session(operation_type=operation_type, metadata=metadata)


def complete_session(session_id: str, status: str = "success"):
    """
    Convenient function to complete a session.

    Args:
        session_id: Session identifier
        status: Final status
    """
    manager = get_session_manager()
    manager.complete_session(session_id, status)


# Example usage
if __name__ == "__main__":
    # Create session manager
    manager = SessionManager()

    # Create a session
    print("Creating security audit session...")
    session = manager.create_session(
        operation_type="security_audit", metadata={"tenant": "contoso.onmicrosoft.com", "compliance": "CIS"}
    )

    print(f"Session ID: {session.session_id}")
    print(f"User: {session.user}")
    print(f"Started: {session.start_time}")

    # Add some events
    session.add_event("progress", "Connecting to Exchange Online")
    session.add_event("progress", "Running CIS controls checks")
    session.add_event("progress", "Analyzing results")

    # Complete session
    manager.complete_session(session.session_id, status="success")
    print(f"Session completed!")

    # Create another session
    session2 = manager.create_session(
        operation_type="sharepoint_analysis", metadata={"site": "https://contoso.sharepoint.com"}
    )
    session2.add_event("progress", "Analyzing permissions")
    manager.complete_session(session2.session_id, status="success")

    # Print statistics
    manager.print_statistics(days=7)

    print("\n📌 Usage Tips:")
    print("=" * 80)
    print("1. Always create sessions for operations:")
    print("   from src.core.session_manager import create_session")
    print("   session = create_session('audit')")
    print()
    print("2. Track important events:")
    print("   session.add_event('progress', 'Completed 50% of checks')")
    print()
    print("3. Complete sessions when done:")
    print("   complete_session(session.session_id, status='success')")
    print()
    print("4. Query session history:")
    print("   manager.get_session_history(operation_type='audit', days=30)")
    print("=" * 80 + "\n")
