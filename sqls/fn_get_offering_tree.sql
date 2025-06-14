-- FUNCTION: public.get_offering_tree(integer)

-- DROP FUNCTION IF EXISTS public.get_offering_tree(integer);

CREATE OR REPLACE FUNCTION public.get_offering_tree(
	root_node_id integer DEFAULT NULL::integer)
    RETURNS jsonb
    LANGUAGE 'sql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
WITH RECURSIVE offering_tree AS (
    SELECT id, pid, 
           jsonb_build_object(
               'name', name,
               'name_de', name_de,
               'description', description,
               'original_name', original_name,
               'source', source,
               'alternative_name', alternative_name
           ) AS data
    FROM sb_offering
    WHERE root_node_id IS NULL OR id = root_node_id
    
    UNION ALL
    
    SELECT o.id, o.pid,
           jsonb_build_object(
               'name', o.name,
               'name_de', o.name_de,
               'description', o.description,
               'original_name', o.original_name,
               'source', o.source,
               'alternative_name', o.alternative_name
           ) AS data
    FROM sb_offering o
    JOIN offering_tree ot ON o.pid = ot.id
),
unique_nodes AS (
    SELECT DISTINCT id, pid, data FROM offering_tree
),
node_children AS (
    SELECT 
        n.id,
        jsonb_agg(DISTINCT c.id::text) AS children
    FROM unique_nodes n
    LEFT JOIN unique_nodes c ON n.id = c.pid
    GROUP BY n.id
)
SELECT jsonb_build_object(
    'properties', jsonb_build_object(
        'tlversion', '3.1.4',
        'topnodes', COALESCE(
            (SELECT jsonb_agg(id::text) FROM unique_nodes WHERE pid IS NULL),
            '[]'::jsonb
        )
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
                            WHEN data_type IN ('timestamp without time zone', 'date') THEN 'Text'
                            ELSE 'Other'
                        END
                    )
                )
                FROM information_schema.columns
                WHERE table_name = 'sb_offering'
                AND column_name IN ('name', 'name_de', 'description', 'original_name', 'source', 'alternative_name')
            ),
            'formatname', 'DEFAULT',
            'outputlines', jsonb_build_array('{*name*}'),
            'titleline', '{*name*}'
        )
    ),
    'nodes', (
        SELECT jsonb_agg(
            jsonb_build_object(
                'uid', n.id::text,
                'format', 'DEFAULT',
                'data', n.data,
                'children', COALESCE(c.children, '[]'::jsonb)
            )
        )
        FROM unique_nodes n
        LEFT JOIN node_children c ON n.id = c.id
    )
) AS result;
$BODY$;

ALTER FUNCTION public.get_offering_tree(integer)
    OWNER TO sbadmintest;
