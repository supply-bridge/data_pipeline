UPDATE sb_offering 
SET name = s.name, 
      name_de = s.name_de, 
	  description = s.description, 
	  "order"=s.order, 
	  is_searchable=s.is_searchable, 
	  is_priority=s.is_priority,
	  original_name = s.original_name,
	  "source"=s.source
FROM sb_staging_offering s
WHERE sb_offering.id = s.id 



