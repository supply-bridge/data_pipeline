WITH RECURSIVE hierarchy AS (
  -- 从特定节点开始
  SELECT 
    id, 
    name, 
    regexp_replace(name, '\s*\(\d+\)', '', 'g') AS clear_name,
    name AS path_name, -- 初始路径就是自身的 name
    1 AS level 
  FROM sb_offering 
  WHERE id = 1 -- 替换为你的起始节点 ID
  UNION ALL
  -- 递归查找子节点，并拼接路径
  SELECT 
    t.id, 
    t.name,
    regexp_replace(t.name, '\s*\(\d+\)', '', 'g') AS clear_name,
    CONCAT(h.path_name, '/', t.name) AS path_name, -- 拼接路径
    h.level + 1 AS level 
  FROM sb_offering t
  JOIN hierarchy h ON t.pid = h.id
  WHERE h.level <= 4   -- 控制层级深度
)

SELECT * FROM hierarchy WHERE level = 4;
