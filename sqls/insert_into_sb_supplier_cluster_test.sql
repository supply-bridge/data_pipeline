insert into sb_supplier_cluster_test 
   (id, old_id, pid, "order", name, long_name, description, long_description, website)
SELECT id, old_id, pid, "order", name, long_name, description, long_description, website
FROM public.sb_supplier;



