"""Routine event operations.

Schema:
  routines: id, name, category, interval_days, active_months, available_days, notes
  routine_events: id, completed_at, routine_id (FK → routines.id)
"""

from .connection import NeonHTTP


def _resolve_routine_id(db: NeonHTTP, name: str) -> str:
    """Look up routine ID by name. Raises if not found."""
    result = db.execute("SELECT id FROM routines WHERE name = $1", [name])
    if not result.rows:
        raise ValueError(f"Routine not found: {name}")
    return str(result.rows[0][0])


def complete_routine(db: NeonHTTP, name: str, category: str, note: str | None = None):
    """Record a routine completion."""
    routine_id = _resolve_routine_id(db, name)
    db.execute(
        "INSERT INTO routine_events (routine_id, completed_at) VALUES ($1, clock_timestamp())",
        [routine_id],
    )


def add_baseline(db: NeonHTTP, name: str, category: str, date: str, note: str | None = None):
    """Record a baseline event (tracking start point)."""
    routine_id = _resolve_routine_id(db, name)
    db.execute(
        "INSERT INTO routine_events (routine_id, completed_at) VALUES ($1, $2)",
        [routine_id, f"{date}T00:00:00+00:00"],
    )


def get_last_event(db: NeonHTTP, name: str) -> dict | None:
    """Get the most recent event for a routine."""
    result = db.execute(
        """
        SELECT r.name, r.category, re.completed_at
        FROM routine_events re
        JOIN routines r ON r.id = re.routine_id
        WHERE r.name = $1
        ORDER BY re.completed_at DESC LIMIT 1
        """,
        [name],
    )
    if not result.rows:
        return None
    row = result.rows[0]
    return {
        "routine_name": row[0],
        "category": row[1],
        "completed_at": str(row[2]),
    }


def get_all_last_events(db: NeonHTTP) -> list[dict]:
    """Get the most recent event for each routine."""
    result = db.execute(
        """
        SELECT DISTINCT ON (r.name)
            r.name, r.category, re.completed_at
        FROM routine_events re
        JOIN routines r ON r.id = re.routine_id
        ORDER BY r.name, re.completed_at DESC
        """
    )
    return [
        {
            "routine_name": row[0],
            "category": row[1],
            "completed_at": str(row[2]),
        }
        for row in result.rows
    ]


def get_history(db: NeonHTTP, name: str) -> list[dict]:
    """Get all events for a routine, newest first."""
    result = db.execute(
        """
        SELECT re.id, r.name, r.category, re.completed_at
        FROM routine_events re
        JOIN routines r ON r.id = re.routine_id
        WHERE r.name = $1
        ORDER BY re.completed_at DESC
        """,
        [name],
    )
    return [
        {
            "id": str(row[0]),
            "routine_name": row[1],
            "category": row[2],
            "completed_at": str(row[3]),
        }
        for row in result.rows
    ]


def delete_event(db: NeonHTTP, event_id: str) -> bool:
    """Delete a routine event by ID. Returns True if deleted."""
    result = db.execute("DELETE FROM routine_events WHERE id = $1", [event_id])
    return result.row_count > 0
