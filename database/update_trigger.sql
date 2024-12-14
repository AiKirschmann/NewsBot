-- Функция для обновления времени публикации
CREATE OR REPLACE FUNCTION update_news_published_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'published' AND OLD.status != 'published' THEN
        UPDATE news 
        SET published_at = CURRENT_TIMESTAMP
        WHERE id = NEW.news_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для обновления времени публикации
DROP TRIGGER IF EXISTS update_news_published_at_trigger ON publications;
CREATE TRIGGER update_news_published_at_trigger
AFTER UPDATE ON publications
FOR EACH ROW
EXECUTE FUNCTION update_news_published_at();
