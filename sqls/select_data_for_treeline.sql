-- 不要布尔值字段, 增加properties
WITH RECURSIVE offering_tree AS (
    SELECT id, pid, to_jsonb(sb_offering) - 'id' - 'pid' - 'embedding' - 'path_embedding' - 'description_embedding' - 'search_embedding' - 'path_text' - 'is_searchable' - 'is_priority' AS data
    FROM sb_offering
    WHERE id = 1
    UNION ALL
    SELECT o.id, o.pid, to_jsonb(o) - 'id' - 'pid' - 'embedding' - 'path_embedding' - 'description_embedding' - 'search_embedding' - 'path_text' - 'is_searchable' - 'is_priority' AS data
    FROM sb_offering o
    JOIN offering_tree ot ON o.pid = ot.id
)
SELECT jsonb_build_object(
    'properties', jsonb_build_object(
        'tlversion', '3.1.4',
        'topnodes', (SELECT jsonb_agg(id::text) FROM offering_tree WHERE pid IS NULL)
    ),
    'formats', jsonb_build_array(
        jsonb_build_object(
            'fields', (
                SELECT jsonb_agg(
                    jsonb_build_object(
                        'fieldname', column_name,
                        'fieldtype', CASE 
                            WHEN data_type IN ('character varying', 'text') THEN 'Text'
                            WHEN data_type IN ('integer', 'bigint', 'smallint') THEN 'Number'
                            WHEN data_type IN ('boolean') THEN 'Boolean'
                            WHEN data_type IN ('timestamp without time zone', 'date') THEN 'Text' -- 确保日期以字符串存储
                            ELSE 'Other'
                        END
                    )
                )
                FROM information_schema.columns
                WHERE table_name = 'sb_offering'
                  AND column_name NOT IN ('id', 'pid', 'embedding', 'path_embedding', 'description_embedding', 'search_embedding', 'path_text', 'is_searchable', 'is_priority')
            ),
            'formatname', 'DEFAULT',
            'outputlines', jsonb_build_array('{*name*}'),
            'titleline', '{*name*}'
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
