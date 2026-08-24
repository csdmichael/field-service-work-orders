-- Forward-only migration 0002: reference data so a new environment is not empty.
-- Re-runnable: each row is inserted only when its title is absent.
INSERT INTO work_item (title, status, priority, location)
SELECT 'Replace condenser fan motor', 'in-progress', 'high', 'Northside Chiller Plant'
WHERE NOT EXISTS (SELECT 1 FROM work_item WHERE title = 'Replace condenser fan motor');
INSERT INTO work_item (title, status, priority, location)
SELECT 'Quarterly filter service', 'new', 'normal', 'Harbour Point Tower'
WHERE NOT EXISTS (SELECT 1 FROM work_item WHERE title = 'Quarterly filter service');
INSERT INTO work_item (title, status, priority, location)
SELECT 'Investigate compressor noise', 'new', 'high', 'Airport Cargo Bay 4'
WHERE NOT EXISTS (SELECT 1 FROM work_item WHERE title = 'Investigate compressor noise');
INSERT INTO work_item (title, status, priority, location)
SELECT 'Recalibrate thermostat array', 'complete', 'low', 'Civic Centre'
WHERE NOT EXISTS (SELECT 1 FROM work_item WHERE title = 'Recalibrate thermostat array');
