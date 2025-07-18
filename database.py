import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional

class GameDatabase:
    """Класс для работы с базой данных игр"""
    
    def __init__(self, db_path: str = "games.db"):
        """Инициализация базы данных"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация таблиц базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица результатов игр
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    game_type TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    moves INTEGER NOT NULL,
                    game_time INTEGER,
                    max_combo INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица рекордов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    game_type TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица достижений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    game_type TEXT NOT NULL,
                    achievement_type TEXT NOT NULL,
                    achievement_name TEXT NOT NULL,
                    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
    
    def save_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Сохранение или обновление пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Проверяем, существует ли пользователь
            cursor.execute('SELECT username, first_name, last_name FROM users WHERE user_id = ?', (user_id,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Обновляем только если новые данные не пустые
                current_username, current_first_name, current_last_name = existing_user
                new_username = username if username else current_username
                new_first_name = first_name if first_name else current_first_name
                new_last_name = last_name if last_name else current_last_name
                
                cursor.execute('''
                    UPDATE users SET username = ?, first_name = ?, last_name = ?
                    WHERE user_id = ?
                ''', (new_username, new_first_name, new_last_name, user_id))
            else:
                # Создаем нового пользователя
                cursor.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
            
            conn.commit()
    
    def save_game_result(self, user_id: int, game_type: str, score: int, moves: int, 
                        game_time: int = None, max_combo: int = 0) -> Tuple[bool, bool, List[str]]:
        """Сохранение результата игры и проверка рекорда"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Проверяем лучший результат пользователя
            cursor.execute('''
                SELECT MAX(score) FROM game_results 
                WHERE game_type = ? AND user_id = ?
            ''', (game_type, user_id))
            
            user_best = cursor.fetchone()[0]
            
            # Сохраняем только если результат лучше или это первая игра
            if user_best is None or score > user_best:
                cursor.execute('''
                    INSERT INTO game_results (user_id, game_type, score, moves, game_time, max_combo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, game_type, score, moves, game_time, max_combo))
                
                is_personal_record = True
                
                # Проверяем глобальный рекорд
                cursor.execute('''
                    SELECT MAX(score) FROM game_results WHERE game_type = ?
                ''', (game_type,))
                
                global_best = cursor.fetchone()[0]
                is_global_record = score >= global_best
                
                # Сохраняем рекорд
                cursor.execute('''
                    INSERT OR REPLACE INTO records (user_id, game_type, score)
                    VALUES (?, ?, ?)
                ''', (user_id, game_type, score))
                
                # Проверяем достижения
                achievements = self._check_achievements(cursor, user_id, game_type, score)
                
                conn.commit()
                return (is_personal_record, is_global_record, achievements)
            else:
                # Результат не лучше - не сохраняем
                return (False, False, [])
    
    def _check_achievements(self, cursor, user_id: int, game_type: str, score: int) -> List[str]:
        """Проверка и выдача достижений"""
        achievements = []
        
        # Подсчитываем количество игр
        cursor.execute('''
            SELECT COUNT(*) FROM game_results 
            WHERE game_type = ? AND user_id = ?
        ''', (game_type, user_id))
        
        games_count = cursor.fetchone()[0]
        
        # Проверяем достижения
        if games_count == 1:
            if not self._has_achievement(cursor, user_id, game_type, "first_win"):
                self._grant_achievement(cursor, user_id, game_type, "first_win", "🎉 Первая победа")
                achievements.append("🎉 Первая победа")
        
        if games_count >= 10:
            if not self._has_achievement(cursor, user_id, game_type, "10_games"):
                self._grant_achievement(cursor, user_id, game_type, "10_games", "🎮 10 игр сыграно")
                achievements.append("🎮 10 игр сыграно")
        
        # Проверяем топовый результат
        cursor.execute('''
            SELECT COUNT(*) FROM game_results 
            WHERE game_type = ? AND score >= ?
        ''', (game_type, score))
        
        position = cursor.fetchone()[0]
        
        if position == 1:
            if not self._has_achievement(cursor, user_id, game_type, "top_score"):
                self._grant_achievement(cursor, user_id, game_type, "top_score", "🏆 Лучший результат")
                achievements.append("🏆 Лучший результат")
        
        return achievements
    
    def _has_achievement(self, cursor, user_id: int, game_type: str, achievement_type: str) -> bool:
        """Проверка наличия достижения"""
        cursor.execute('''
            SELECT COUNT(*) FROM achievements 
            WHERE user_id = ? AND game_type = ? AND achievement_type = ?
        ''', (user_id, game_type, achievement_type))
        
        return cursor.fetchone()[0] > 0
    
    def _grant_achievement(self, cursor, user_id: int, game_type: str, achievement_type: str, achievement_name: str):
        """Выдача достижения"""
        cursor.execute('''
            INSERT INTO achievements (user_id, game_type, achievement_type, achievement_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, game_type, achievement_type, achievement_name))
    
    def get_leaderboard(self, game_type: str, limit: int = 10) -> List[Tuple]:
        """Получение таблицы лидеров для конкретной игры"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.username, u.first_name, gr.score, gr.moves, gr.game_time, gr.max_combo, gr.created_at
                FROM game_results gr
                JOIN users u ON gr.user_id = u.user_id
                WHERE gr.game_type = ?
                ORDER BY gr.score DESC, gr.created_at ASC
                LIMIT ?
            ''', (game_type, limit))
            
            return cursor.fetchall()
    
    def get_user_stats(self, user_id: int, game_type: str = None) -> dict:
        """Получение статистики пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if game_type:
                # Статистика для конкретной игры
                cursor.execute('''
                    SELECT COUNT(*), MAX(score), AVG(score), SUM(moves), SUM(game_time)
                    FROM game_results 
                    WHERE user_id = ? AND game_type = ?
                ''', (user_id, game_type))
            else:
                # Общая статистика
                cursor.execute('''
                    SELECT COUNT(*), MAX(score), AVG(score), SUM(moves), SUM(game_time)
                    FROM game_results 
                    WHERE user_id = ?
                ''', (user_id,))
            
            result = cursor.fetchone()
            if result and result[0]:
                return {
                    'games_played': result[0],
                    'best_score': result[1],
                    'avg_score': round(result[2], 1),
                    'total_moves': result[3],
                    'total_time': result[4]
                }
            return {}
    
    def get_user_position(self, user_id: int, game_type: str) -> Optional[int]:
        """Получение позиции пользователя в таблице лидеров"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) + 1
                FROM game_results gr1
                WHERE gr1.game_type = ? AND gr1.score > (
                    SELECT MAX(gr2.score) 
                    FROM game_results gr2 
                    WHERE gr2.user_id = ? AND gr2.game_type = ?
                )
            ''', (game_type, user_id, game_type))
            
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_user_achievements(self, user_id: int, game_type: str) -> List[str]:
        """Получение достижений пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT achievement_name FROM achievements 
                WHERE user_id = ? AND game_type = ?
                ORDER BY achieved_at ASC
            ''', (user_id, game_type))
            
            return [row[0] for row in cursor.fetchall()]
    
    def update_user_info(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Обновление информации о пользователе во всех записях"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Обновляем основную информацию пользователя
            if username or first_name or last_name:
                self.save_user(user_id, username, first_name, last_name)
            
            conn.commit()

# Глобальный экземпляр базы данных
db = GameDatabase() 