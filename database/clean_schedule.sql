-- Очищаем все pending публикации
DELETE FROM publications WHERE status = 'pending';

-- Создаем временную таблицу для дубликатов по заголовкам
CREATE TEMP TABLE duplicate_titles AS
SELECT LOWER(title) as lower_title, COUNT(*) as count
FROM news
GROUP BY LOWER(title)
HAVING COUNT(*) > 1;

-- Выводим найденные дубликаты
SELECT n.title, n.category, n.created_at
FROM news n
JOIN duplicate_titles dt ON LOWER(n.title) = dt.lower_title
ORDER BY dt.lower_title, n.created_at DESC;

-- Удаляем дубликаты, оставляя только самые свежие записи
WITH duplicates_to_remove AS (
    SELECT id
    FROM (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY LOWER(title) ORDER BY created_at DESC) as rn
        FROM news
    ) t
    WHERE rn > 1
)
DELETE FROM news
WHERE id IN (SELECT id FROM duplicates_to_remove);

-- Проверяем оставшиеся новости
SELECT title, category, created_at 
FROM news 
ORDER BY created_at DESC;
