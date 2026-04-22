"""Tests for routine event operations."""

from alt_db.routines import (
    add_baseline,
    complete_routine,
    delete_event,
    get_all_last_events,
    get_history,
    get_last_event,
)


def test_complete_routine_and_retrieve(db):
    client, _, routine_ids, _ = db
    routine_id = _create_test_routine(client, "test_Clean the toilet", "household")
    routine_ids.add(routine_id)
    complete_routine(client, "test_Clean the toilet", "household")
    result = get_last_event(client, "test_Clean the toilet")
    assert result is not None
    assert result["routine_name"] == "test_Clean the toilet"
    assert result["category"] == "household"


def test_add_baseline(db):
    client, _, routine_ids, _ = db
    routine_id = _create_test_routine(client, "test_Take flea medicine", "dog")
    routine_ids.add(routine_id)
    add_baseline(client, "test_Take flea medicine", "dog", date="2026-05-01")
    result = get_last_event(client, "test_Take flea medicine")
    assert "2026-05-01" in result["completed_at"]


def test_get_last_event_returns_most_recent(db):
    client, _, routine_ids, _ = db
    routine_id = _create_test_routine(client, "test_Clean toilet recent", "household")
    routine_ids.add(routine_id)
    complete_routine(client, "test_Clean toilet recent", "household")
    complete_routine(client, "test_Clean toilet recent", "household")
    result = get_last_event(client, "test_Clean toilet recent")
    assert result is not None


def test_get_last_event_not_found(db):
    client, _, _, _ = db
    result = get_last_event(client, "test_Nonexistent routine")
    assert result is None


def test_get_all_last_events(db):
    client, _, routine_ids, _ = db
    rid1 = _create_test_routine(client, "test_All clean toilet", "household")
    rid2 = _create_test_routine(client, "test_All dental checkup", "health")
    routine_ids.update([rid1, rid2])
    complete_routine(client, "test_All clean toilet", "household")
    complete_routine(client, "test_All dental checkup", "health")
    results = get_all_last_events(client)
    names = [r["routine_name"] for r in results]
    assert "test_All clean toilet" in names
    assert "test_All dental checkup" in names


def test_get_all_last_events_returns_only_latest(db):
    client, _, routine_ids, _ = db
    rid = _create_test_routine(client, "test_Latest clean toilet", "household")
    routine_ids.add(rid)
    complete_routine(client, "test_Latest clean toilet", "household")
    complete_routine(client, "test_Latest clean toilet", "household")
    results = get_all_last_events(client)
    matched = [r for r in results if r["routine_name"] == "test_Latest clean toilet"]
    assert len(matched) == 1


def test_get_history(db):
    client, _, routine_ids, _ = db
    rid = _create_test_routine(client, "test_History routine", "household")
    routine_ids.add(rid)
    complete_routine(client, "test_History routine", "household")
    complete_routine(client, "test_History routine", "household")
    results = get_history(client, "test_History routine")
    assert len(results) == 2
    assert "id" in results[0]


def test_get_history_empty(db):
    client, _, _, _ = db
    results = get_history(client, "test_Nonexistent history")
    assert results == []


def test_delete_event(db):
    client, _, routine_ids, _ = db
    rid = _create_test_routine(client, "test_Delete routine", "household")
    routine_ids.add(rid)
    complete_routine(client, "test_Delete routine", "household")
    history = get_history(client, "test_Delete routine")
    event_id = history[0]["id"]
    assert delete_event(client, event_id) is True
    assert get_history(client, "test_Delete routine") == []


def test_delete_event_not_found(db):
    client, _, _, _ = db
    assert delete_event(client, "00000000-0000-0000-0000-000000000000") is False


def _create_test_routine(client, name: str, category: str) -> str:
    """Create a test routine in the routines table and return its ID."""
    result = client.execute(
        "INSERT INTO routines (name, category, interval_days) VALUES ($1, $2, 7) RETURNING id",
        [name, category],
    )
    return str(result.rows[0][0])
