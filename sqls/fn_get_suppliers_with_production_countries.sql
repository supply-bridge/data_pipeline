-- FUNCTION: public.get_suppliers_with_production_countries(integer[])

-- DROP FUNCTION IF EXISTS public.get_suppliers_with_production_countries(integer[]);

CREATE OR REPLACE FUNCTION public.get_suppliers_with_production_countries(
	supplier_ids integer[])
    RETURNS jsonb
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    result JSONB;
BEGIN
    WITH supplier_countries AS (
        SELECT
            s.id AS supplier_id,
            s.name AS supplier_name,
            c.name AS headquarter,
            s.rating,
            COALESCE(
                ARRAY_AGG(DISTINCT c1.name) FILTER (WHERE c1.name IS NOT NULL),
                '{}'
            ) AS production_countries
        FROM sb_supplier s
        JOIN sb_country c ON s.headquarter_id = c.id
        LEFT JOIN sb_supplier sub ON sub.pid = s.id
        LEFT JOIN sb_country c1 ON sub.country_id = c1.id
        WHERE s.pid IS NULL  -- 只选 parent 供应商
        AND s.id = ANY(supplier_ids)  -- 通过传递的 supplier_ids 查询
        GROUP BY s.id, s.name, c.name, s.rating
    )
    SELECT jsonb_agg(
        jsonb_build_object(
            'supplier_id', supplier_id,
            'supplier_name', supplier_name,
            'headquarter', headquarter,
            'production_countries', production_countries,
            'rating', rating
        )
    )
    INTO result
    FROM supplier_countries;

    RETURN result;
END;
$BODY$;

ALTER FUNCTION public.get_suppliers_with_production_countries(integer[])
    OWNER TO sbadmintest;
