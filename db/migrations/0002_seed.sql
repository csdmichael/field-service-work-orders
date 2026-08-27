-- Forward-only migration 0002: reference data so a new environment is not empty.
-- Re-runnable: each row is inserted only when its title is absent.
INSERT INTO work_order (title, reference, status, priority)
SELECT 'Sample Work Order 1', 'WO-0001', 'new', 'low'
WHERE NOT EXISTS (SELECT 1 FROM work_order WHERE title = 'Sample Work Order 1');
INSERT INTO work_order (title, reference, status, priority)
SELECT 'Sample Work Order 2', 'WO-0002', 'in-progress', 'normal'
WHERE NOT EXISTS (SELECT 1 FROM work_order WHERE title = 'Sample Work Order 2');
INSERT INTO work_order (title, reference, status, priority)
SELECT 'Sample Work Order 3', 'WO-0003', 'complete', 'high'
WHERE NOT EXISTS (SELECT 1 FROM work_order WHERE title = 'Sample Work Order 3');
INSERT INTO work_order (title, reference, status, priority)
SELECT 'Sample Work Order 4', 'WO-0004', 'new', 'low'
WHERE NOT EXISTS (SELECT 1 FROM work_order WHERE title = 'Sample Work Order 4');
