"""In-memory repository seeded with the same rows as db/migrations/0002_seed.sql.

Swap this for the database in db/ by implementing the same four methods; the
routes do not know which implementation they are talking to.
"""
from itertools import count
from typing import Dict, List, Optional

SEED = [
    {"title": "Replace condenser fan motor", "status": "in-progress", "priority": "high", "location": "Northside Chiller Plant"},
    {"title": "Quarterly filter service", "status": "new", "priority": "normal", "location": "Harbour Point Tower"},
    {"title": "Investigate compressor noise", "status": "new", "priority": "high", "location": "Airport Cargo Bay 4"},
    {"title": "Recalibrate thermostat array", "status": "complete", "priority": "low", "location": "Civic Centre"},
]


class WorkItemStore:
    def __init__(self) -> None:
        self._ids = count(1)
        self._items: Dict[int, dict] = {}
        for row in SEED:
            self.create(row)

    def list(self, status: Optional[str] = None) -> List[dict]:
        items = sorted(self._items.values(), key=lambda item: item['id'])
        return [item for item in items if status is None or item['status'] == status]

    def get(self, item_id: int) -> Optional[dict]:
        return self._items.get(item_id)

    def create(self, payload: dict) -> dict:
        item = {**payload, 'id': next(self._ids)}
        self._items[item['id']] = item
        return item

    def update(self, item_id: int, changes: dict) -> Optional[dict]:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.update({key: value for key, value in changes.items() if value is not None})
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None


store = WorkItemStore()
