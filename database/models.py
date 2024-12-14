from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class News(Base):
    """Модель для новостей"""
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    link = Column(String(500), unique=True, nullable=False)  # URL новости
    content = Column(Text, nullable=True)  # Полный текст новости
    category = Column(String(50), nullable=False)  # Категория новости
    
    # Метрики анализа
    sentiment_score = Column(Float, default=0.0)  # Оценка тональности
    relevance_score = Column(Float, default=0.0)  # Оценка релевантности
    
    # Флаги состояния
    is_processed = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связанные публикации
    publications = relationship("Publication", back_populates="news")

    def __repr__(self):
        return f"<News {self.id}: {self.title[:50]}...>"

class Publication(Base):
    """Модель для публикаций в Telegram"""
    __tablename__ = 'publications'

    id = Column(Integer, primary_key=True)
    news_id = Column(Integer, ForeignKey('news.id'), nullable=False)
    channel_id = Column(String(100), nullable=False)
    message_id = Column(Integer, nullable=True)
    
    # Статус публикации
    status = Column(String(20), default='pending')  # pending, published, failed
    error_message = Column(Text, nullable=True)  # Сообщение об ошибке, если есть
    
    # Временные метки
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связь с новостью
    news = relationship("News", back_populates="publications")

    def __repr__(self):
        return f"<Publication {self.id}: {self.status}>"

class Stats(Base):
    """Модель для статистики"""
    __tablename__ = 'stats'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), nullable=False)
    category = Column(String(50), nullable=False)
    news_count = Column(Integer, default=0)
    published_count = Column(Integer, default=0)
    avg_sentiment_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Stats {self.date}: {self.category}>"

# SQL для создания таблиц
CREATE_TABLES_SQL = """
-- Таблица новостей
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    link VARCHAR(500) UNIQUE NOT NULL,
    content TEXT,
    category VARCHAR(50) NOT NULL,
    sentiment_score FLOAT DEFAULT 0.0,
    relevance_score FLOAT DEFAULT 0.0,
    is_processed BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE
);

-- Таблица публикаций
CREATE TABLE IF NOT EXISTS publications (
    id SERIAL PRIMARY KEY,
    news_id INTEGER REFERENCES news(id) NOT NULL,
    channel_id VARCHAR(100) NOT NULL,
    message_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица статистики
CREATE TABLE IF NOT EXISTS stats (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    category VARCHAR(50) NOT NULL,
    news_count INTEGER DEFAULT 0,
    published_count INTEGER DEFAULT 0,
    avg_sentiment_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_news_link ON news(link);
CREATE INDEX IF NOT EXISTS idx_news_category ON news(category);
CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at);
CREATE INDEX IF NOT EXISTS idx_publications_status ON publications(status);
CREATE INDEX IF NOT EXISTS idx_publications_scheduled_time ON publications(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_stats_date ON stats(date);
"""
