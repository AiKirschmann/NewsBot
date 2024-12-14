-- Добавляем недостающие колонки в таблицу news
ALTER TABLE news ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT FALSE;
ALTER TABLE news ADD COLUMN IF NOT EXISTS is_processed BOOLEAN DEFAULT FALSE;

-- Обновляем типы существующих колонок для единообразия
ALTER TABLE news 
    ALTER COLUMN published_at TYPE TIMESTAMP WITH TIME ZONE,
    ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

-- Обновляем индексы
CREATE INDEX IF NOT EXISTS idx_news_is_published ON news(is_published);
CREATE INDEX IF NOT EXISTS idx_news_is_processed ON news(is_processed);

-- Обновляем таблицу publications если она существует
CREATE TABLE IF NOT EXISTS publications (
    id SERIAL PRIMARY KEY,
    news_id INTEGER REFERENCES news(id),
    channel_id VARCHAR(100) NOT NULL,
    message_id INTEGER,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

-- Добавляем индексы для publications
CREATE INDEX IF NOT EXISTS idx_publications_status ON publications(status);
CREATE INDEX IF NOT EXISTS idx_publications_scheduled_time ON publications(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_publications_news_id ON publications(news_id);
