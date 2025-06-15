offering_load -> sb_offering

offering_fields:

CREATE OR REPLACE VIEW public.offering_fields
 AS
 SELECT offering_load.id,
    offering_load.pid,
    offering_load.name,
    offering_load.name_de,
    offering_load.description,
	  offering_load.original_name,
	  offering_load.source,
	  offering_load.alternative_name
   FROM offering_load;

get_offering_tree(root_node_id)
