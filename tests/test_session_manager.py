"""
Tests for Session Manager
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta

from src.core.session_manager import Session, SessionManager, get_session_manager


def test_session_creation():
    """Test basic session creation and attributes"""
    session = Session(operation_type="test_operation", metadata={"key": "value"})
    
    assert session.session_id is not None
    assert len(session.session_id) > 0
    assert session.user is not None
    assert session.operation_type == "test_operation"
    assert session.metadata["key"] == "value"
    assert session.status == "active"
    assert session.start_time is not None
    assert session.end_time is None


def test_session_events():
    """Test adding events to a session"""
    session = Session(operation_type="test")
    
    session.add_event("start", "Starting test")
    session.add_event("progress", "50% complete", {"percentage": 50})
    session.add_event("complete", "Test finished")
    
    assert len(session.events) == 3
    assert session.events[0]["type"] == "start"
    assert session.events[1]["data"]["percentage"] == 50
    assert session.events[2]["description"] == "Test finished"


def test_session_completion():
    """Test completing a session"""
    session = Session(operation_type="test")
    
    assert session.status == "active"
    assert session.end_time is None
    
    session.complete(status="success")
    
    assert session.status == "success"
    assert session.end_time is not None
    assert session.get_duration() is not None
    assert len(session.events) > 0  # Complete event should be added


def test_session_serialization():
    """Test session to_dict and from_dict"""
    original = Session(
        operation_type="test",
        user="testuser",
        metadata={"key": "value"}
    )
    original.add_event("test", "Test event")
    original.complete("success")
    
    # Serialize
    data = original.to_dict()
    
    assert data["session_id"] == original.session_id
    assert data["user"] == "testuser"
    assert data["operation_type"] == "test"
    assert data["metadata"]["key"] == "value"
    assert data["status"] == "success"
    assert len(data["events"]) > 0
    
    # Deserialize
    restored = Session.from_dict(data)
    
    assert restored.session_id == original.session_id
    assert restored.user == original.user
    assert restored.operation_type == original.operation_type
    assert restored.status == original.status
    assert len(restored.events) == len(original.events)


def test_session_manager_creation():
    """Test session manager creates sessions"""
    with TemporaryDirectory() as td:
        storage_path = Path(td) / "sessions.json"
        manager = SessionManager(storage_path=str(storage_path))
        
        session = manager.create_session(
            operation_type="audit",
            metadata={"tenant": "test.onmicrosoft.com"}
        )
        
        assert session.session_id in manager.active_sessions
        assert session.operation_type == "audit"
        assert storage_path.exists()


def test_session_manager_persistence():
    """Test sessions are persisted and loaded"""
    with TemporaryDirectory() as td:
        storage_path = Path(td) / "sessions.json"
        
        # Create manager and session
        manager1 = SessionManager(storage_path=str(storage_path))
        session1 = manager1.create_session(operation_type="test1")
        session1.add_event("test", "Test event")
        manager1.complete_session(session1.session_id, status="success")
        
        # Create new manager - should load previous session
        manager2 = SessionManager(storage_path=str(storage_path))
        history = manager2.get_session_history(days=1)
        
        assert len(history) >= 1
        assert any(s["session_id"] == session1.session_id for s in history)


def test_session_manager_get_session():
    """Test retrieving active sessions"""
    with TemporaryDirectory() as td:
        storage_path = Path(td) / "sessions.json"
        manager = SessionManager(storage_path=str(storage_path))
        
        session = manager.create_session(operation_type="test")
        
        retrieved = manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
        
        # Non-existent session
        none_session = manager.get_session("nonexistent-id")
        assert none_session is None


def test_session_manager_complete_session():
    """Test completing sessions removes them from active list"""
    with TemporaryDirectory() as td:
        storage_path = Path(td) / "sessions.json"
        manager = SessionManager(storage_path=str(storage_path))
        
        session = manager.create_session(operation_type="test")
        assert session.session_id in manager.active_sessions
        
        manager.complete_session(session.session_id, status="success")
        assert session.session_id not in manager.active_sessions
        assert session.status == "success"
        
        # Should be in history
        history = manager.get_session_history(days=1)
        assert any(s["session_id"] == session.session_id for s in history)


def test_session_manager_query_by_operation():
    """Test querying sessions by operation type"""
    with TemporaryDirectory() as td:
        storage_path = Path(td) / "sessions.json"
        manager = SessionManager(storage_path=str(storage_path))
        
        # Create sessions of different types
        audit_session = manager.create_session(operation_type="audit")
        analysis_session = manager.create_session(operation_type="analysis")
        manager.complete_session(audit_session.session_id)
        manager.complete_session(analysis_session.session_id)
        
        # Query by type
        audit_history = manager.get_session_history(operation_type="audit", days=1)
        assert len(audit_history) == 1
        assert audit_history[0]["operation_type"] == "audit"
        
        analysis_history = manager.get_session_history(operation_type="analysis", days=1)
        assert len(analysis_history) == 1
        assert analysis_history[0]["operation_type"] == "analysis"


def test_session_manager_query_by_user():
    """Test querying sessions by user"""
    with TemporaryDirectory() as td:
        storage_path = Path(td) / "sessions.json"
        manager = SessionManager(storage_path=str(storage_path))
        
        # Create sessions for different users
        user1_session = manager.create_session(operation_type="test", user="user1")
        user2_session = manager.create_session(operation_type="test", user="user2")
        manager.complete_session(user1_session.session_id)
        manager.complete_session(user2_session.session_id)
        
        # Query by user
        user1_history = manager.get_session_history(user="user1", days=1)
        assert len(user1_history) == 1
        assert user1_history[0]["user"] == "user1"
        
        user2_history = manager.get_session_history(user="user2", days=1)
        assert len(user2_history) == 1
        assert user2_history[0]["user"] == "user2"


def test_session_manager_statistics():
    """Test session statistics calculation"""
    with TemporaryDirectory() as td:
        storage_path = Path(td) / "sessions.json"
        manager = SessionManager(storage_path=str(storage_path))
        
        # Create several sessions
        session1 = manager.create_session(operation_type="audit")
        session2 = manager.create_session(operation_type="audit")
        session3 = manager.create_session(operation_type="analysis")
        
        manager.complete_session(session1.session_id, status="success")
        manager.complete_session(session2.session_id, status="success")
        manager.complete_session(session3.session_id, status="error")
        
        stats = manager.get_statistics(days=1)
        
        assert stats["total_sessions"] == 3
        assert stats["by_operation_type"]["audit"] == 2
        assert stats["by_operation_type"]["analysis"] == 1
        assert stats["by_status"]["success"] == 2
        assert stats["by_status"]["error"] == 1
        assert "avg_duration_seconds" in stats


def test_global_session_manager():
    """Test global session manager singleton"""
    with TemporaryDirectory() as td:
        storage_path = Path(td) / "sessions.json"
        
        # Get global instance
        manager1 = get_session_manager(storage_path=str(storage_path))
        manager2 = get_session_manager()
        
        # Should be same instance
        assert manager1 is manager2


def test_session_duration():
    """Test session duration calculation"""
    session = Session(operation_type="test")
    
    # Active session should have duration
    duration1 = session.get_duration()
    assert duration1 is not None
    assert duration1.total_seconds() >= 0
    
    # Complete session
    session.complete("success")
    duration2 = session.get_duration()
    assert duration2 is not None
    assert duration2.total_seconds() >= 0


def test_empty_history():
    """Test manager with no session history"""
    with TemporaryDirectory() as td:
        storage_path = Path(td) / "sessions.json"
        manager = SessionManager(storage_path=str(storage_path))
        
        history = manager.get_session_history(days=30)
        assert history == []
        
        stats = manager.get_statistics(days=30)
        assert stats["total_sessions"] == 0
        assert stats["by_operation_type"] == {}
        assert stats["avg_duration_seconds"] == 0
