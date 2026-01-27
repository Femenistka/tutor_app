PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                comment TEXT
            );
INSERT INTO lessons VALUES(1,'Паша',25.0,'2025-01-15','артем');
INSERT INTO lessons VALUES(2,'Паша',25.0,'2025-01-19','мега');
INSERT INTO lessons VALUES(3,'Паша',25.0,'2025-01-23','балбес');
INSERT INTO lessons VALUES(4,'Паша',25.0,'2025-01-26','но');
INSERT INTO lessons VALUES(5,'Никита',30.0,'2025-01-19','я');
INSERT INTO lessons VALUES(6,'Никита',30.0,'2025-01-26','его');
INSERT INTO lessons VALUES(7,'Катя',25.0,'2025-01-15','все равно');
INSERT INTO lessons VALUES(8,'Катя',25.0,'2025-01-23','очень');
INSERT INTO lessons VALUES(9,'Глеб',30.0,'2025-01-24','люблю');
INSERT INTO lessons VALUES(10,'Глеб',30.0,'2026-01-27',NULL);
CREATE TABLE payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                comment TEXT,
                pay_method TEXT NOT NULL DEFAULT 'card'  -- 'cash' | 'card'
            );
INSERT INTO payments VALUES(1,'Паша',25.0,'2025-01-15','артем','card');
INSERT INTO payments VALUES(2,'Паша',25.0,'2025-01-19','мега','card');
INSERT INTO payments VALUES(3,'Паша',25.0,'2025-01-23','балбес','card');
INSERT INTO payments VALUES(4,'Паша',25.0,'2025-01-26','но','card');
INSERT INTO payments VALUES(5,'Никита',30.0,'2025-01-19','я','card');
INSERT INTO payments VALUES(6,'Никита',30.0,'2025-01-26','его','card');
INSERT INTO payments VALUES(7,'Катя',25.0,'2025-01-15','все равно','cash');
INSERT INTO payments VALUES(8,'Катя',25.0,'2025-01-23','очень','cash');
INSERT INTO payments VALUES(9,'Глеб',30.0,'2025-01-24','люблю','cash');
INSERT INTO sqlite_sequence VALUES('payments',9);
INSERT INTO sqlite_sequence VALUES('lessons',10);
COMMIT;
