WITH RECURSIVE offering_tree AS (
    SELECT id, pid,
           jsonb_build_object(
               'Name', name,
               'name_de', name_de
           ) AS data
    FROM sb_offering
    WHERE id = 1
    UNION ALL
    SELECT o.id, o.pid,
           jsonb_build_object(
               'Name', o.name,
               'name_de', o.name_de
           ) AS data
    FROM sb_offering o
    JOIN offering_tree ot ON o.pid = ot.id
)
SELECT jsonb_build_object(
    'formats', jsonb_build_array(
        jsonb_build_object(
            'fields', jsonb_build_array(
                jsonb_build_object('fieldname', 'Name', 'fieldtype', 'Text'),
                jsonb_build_object('fieldname', 'name_de', 'fieldtype', 'Text')
            ),
            'formatname', 'DEFAULT',
            'outputlines', jsonb_build_array('{*Name*}'),
            'titleline', '{*Name*}'
        )
    ),
    'nodes', jsonb_agg(
        jsonb_build_object(
            'uid', id::text,
            'format', 'DEFAULT',
            'data', data,
            'children', COALESCE(
                (SELECT jsonb_agg(child.id::text) FROM offering_tree child WHERE child.pid = ot.id),
                '[]'::jsonb
            )
        )
    )
) AS result
FROM offering_tree ot;
