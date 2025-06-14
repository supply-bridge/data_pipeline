
CREATE OR REPLACE VIEW offering_fields AS
SELECT id, pid, name, name_de
FROM offering_load;


INSERT INTO sb_offering
SELECT * FROM offering_fields
ON CONFLICT (id) DO UPDATE
SET pid = EXCLUDED.pid,
    name = EXCLUDED.name,
    name_de = EXCLUDED.name_de;
