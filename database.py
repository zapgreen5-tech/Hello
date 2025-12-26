"""
Zolory Bot Database Models and Operations
Complete database schema for user management, economy, moderation, gambling, and server settings
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
from dataclasses import dataclass, asdict
from enum import Enum


class CurrencyType(Enum):
    """Currency types for the economy system"""
    COINS = "coins"
    GEMS = "gems"


class ModerationType(Enum):
    """Types of moderation actions"""
    WARN = "warn"
    MUTE = "mute"
    KICK = "kick"
    BAN = "ban"


@dataclass
class User:
    """User model for user management"""
    user_id: int
    username: str
    coins: int = 0
    gems: int = 0
    level: int = 1
    experience: int = 0
    total_messages: int = 0
    join_date: str = None
    last_activity: str = None
    reputation: int = 0
    
    def __post_init__(self):
        if self.join_date is None:
            self.join_date = datetime.utcnow().isoformat()
        if self.last_activity is None:
            self.last_activity = datetime.utcnow().isoformat()


@dataclass
class ServerSettings:
    """Server configuration model"""
    server_id: int
    server_name: str
    prefix: str = "!"
    welcome_channel_id: Optional[int] = None
    moderation_channel_id: Optional[int] = None
    log_channel_id: Optional[int] = None
    auto_role_id: Optional[int] = None
    currency_name: str = "coins"
    max_level: int = 100
    xp_per_message: int = 10
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


@dataclass
class UserBalance:
    """User economy balance model"""
    user_id: int
    server_id: int
    coins: int = 0
    gems: int = 0
    daily_streak: int = 0
    last_daily: Optional[str] = None
    total_earned: int = 0
    total_spent: int = 0
    bank_balance: int = 0
    
    def __post_init__(self):
        if self.last_daily is None:
            self.last_daily = (datetime.utcnow() - timedelta(days=1)).isoformat()


@dataclass
class GambleRecord:
    """Gambling record model"""
    gamble_id: int
    user_id: int
    server_id: int
    game_type: str  # "slots", "dice", "flip", "roulette", "blackjack"
    bet_amount: int
    winnings: int
    result: str  # "win", "lose"
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class ModerationRecord:
    """Moderation action record model"""
    mod_id: int
    server_id: int
    user_id: int
    moderator_id: int
    action_type: str  # from ModerationType
    reason: str
    duration: Optional[int] = None  # in minutes, for temp bans/mutes
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class DatabaseManager:
    """Main database manager for Zolory bot"""
    
    def __init__(self, db_path: str = "zolory_bot.db"):
        """Initialize database connection and create tables"""
        self.db_path = db_path
        self.connection = None
        self.init_database()
    
    def connect(self):
        """Create database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                coins INTEGER DEFAULT 0,
                gems INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0,
                join_date TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                reputation INTEGER DEFAULT 0
            )
        """)
        
        # Server Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS server_settings (
                server_id INTEGER PRIMARY KEY,
                server_name TEXT NOT NULL,
                prefix TEXT DEFAULT '!',
                welcome_channel_id INTEGER,
                moderation_channel_id INTEGER,
                log_channel_id INTEGER,
                auto_role_id INTEGER,
                currency_name TEXT DEFAULT 'coins',
                max_level INTEGER DEFAULT 100,
                xp_per_message INTEGER DEFAULT 10,
                created_at TEXT NOT NULL
            )
        """)
        
        # User Balance (per server) table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_balance (
                balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                server_id INTEGER NOT NULL,
                coins INTEGER DEFAULT 0,
                gems INTEGER DEFAULT 0,
                daily_streak INTEGER DEFAULT 0,
                last_daily TEXT,
                total_earned INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                bank_balance INTEGER DEFAULT 0,
                UNIQUE(user_id, server_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(server_id) REFERENCES server_settings(server_id)
            )
        """)
        
        # Gambling Records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gamble_records (
                gamble_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                server_id INTEGER NOT NULL,
                game_type TEXT NOT NULL,
                bet_amount INTEGER NOT NULL,
                winnings INTEGER NOT NULL,
                result TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(server_id) REFERENCES server_settings(server_id)
            )
        """)
        
        # Moderation Records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moderation_records (
                mod_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                duration INTEGER,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(server_id) REFERENCES server_settings(server_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(moderator_id) REFERENCES users(user_id)
            )
        """)
        
        # Warnings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                warning_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(server_id) REFERENCES server_settings(server_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(moderator_id) REFERENCES users(user_id)
            )
        """)
        
        # Mutes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mutes (
                mute_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                duration INTEGER,
                mute_time TEXT NOT NULL,
                expire_time TEXT NOT NULL,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY(server_id) REFERENCES server_settings(server_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(moderator_id) REFERENCES users(user_id)
            )
        """)
        
        # Bans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bans (
                ban_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                duration INTEGER,
                ban_time TEXT NOT NULL,
                expire_time TEXT NOT NULL,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY(server_id) REFERENCES server_settings(server_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(moderator_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, user_id: int, username: str) -> User:
        """Create a new user"""
        conn = self.connect()
        cursor = conn.cursor()
        user = User(user_id=user_id, username=username)
        
        cursor.execute("""
            INSERT OR IGNORE INTO users 
            (user_id, username, join_date, last_activity)
            VALUES (?, ?, ?, ?)
        """, (user.user_id, user.username, user.join_date, user.last_activity))
        
        conn.commit()
        conn.close()
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(**dict(row))
        return None
    
    def update_user_activity(self, user_id: int):
        """Update user's last activity timestamp"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET last_activity = ? WHERE user_id = ?
        """, (datetime.utcnow().isoformat(), user_id))
        
        conn.commit()
        conn.close()
    
    def add_experience(self, user_id: int, xp: int) -> Tuple[int, int]:
        """Add experience to user and return new level and experience"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT experience, level FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        new_xp = row["experience"] + xp
        # Assuming 1000 XP per level
        new_level = 1 + (new_xp // 1000)
        
        cursor.execute("""
            UPDATE users SET experience = ?, level = ? WHERE user_id = ?
        """, (new_xp, new_level, user_id))
        
        conn.commit()
        conn.close()
        return new_level, new_xp
    
    def increment_message_count(self, user_id: int):
        """Increment total messages count for user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET total_messages = total_messages + 1 WHERE user_id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
    
    def add_reputation(self, user_id: int, amount: int):
        """Add or remove reputation from user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET reputation = reputation + ? WHERE user_id = ?
        """, (amount, user_id))
        
        conn.commit()
        conn.close()
    
    def get_top_users(self, metric: str = "level", limit: int = 10) -> List[User]:
        """Get top users by specified metric (level, coins, gems, etc.)"""
        conn = self.connect()
        cursor = conn.cursor()
        
        valid_metrics = ["level", "coins", "gems", "experience", "reputation"]
        if metric not in valid_metrics:
            metric = "level"
        
        cursor.execute(f"SELECT * FROM users ORDER BY {metric} DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [User(**dict(row)) for row in rows]
    
    # ==================== SERVER SETTINGS OPERATIONS ====================
    
    def create_server_settings(self, server_id: int, server_name: str, 
                              prefix: str = "!") -> ServerSettings:
        """Create server settings"""
        conn = self.connect()
        cursor = conn.cursor()
        settings = ServerSettings(server_id=server_id, server_name=server_name, prefix=prefix)
        
        cursor.execute("""
            INSERT OR IGNORE INTO server_settings 
            (server_id, server_name, prefix, created_at)
            VALUES (?, ?, ?, ?)
        """, (settings.server_id, settings.server_name, settings.prefix, settings.created_at))
        
        conn.commit()
        conn.close()
        return settings
    
    def get_server_settings(self, server_id: int) -> Optional[ServerSettings]:
        """Get server settings by ID"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM server_settings WHERE server_id = ?", (server_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ServerSettings(**dict(row))
        return None
    
    def update_server_settings(self, server_id: int, **kwargs):
        """Update server settings"""
        conn = self.connect()
        cursor = conn.cursor()
        
        allowed_fields = [
            "prefix", "welcome_channel_id", "moderation_channel_id",
            "log_channel_id", "auto_role_id", "currency_name", "max_level", "xp_per_message"
        ]
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                cursor.execute(f"UPDATE server_settings SET {key} = ? WHERE server_id = ?",
                             (value, server_id))
        
        conn.commit()
        conn.close()
    
    # ==================== ECONOMY OPERATIONS ====================
    
    def create_user_balance(self, user_id: int, server_id: int) -> UserBalance:
        """Create user balance for a server"""
        conn = self.connect()
        cursor = conn.cursor()
        balance = UserBalance(user_id=user_id, server_id=server_id)
        
        cursor.execute("""
            INSERT OR IGNORE INTO user_balance 
            (user_id, server_id, last_daily)
            VALUES (?, ?, ?)
        """, (balance.user_id, balance.server_id, balance.last_daily))
        
        conn.commit()
        conn.close()
        return balance
    
    def get_user_balance(self, user_id: int, server_id: int) -> Optional[UserBalance]:
        """Get user balance in a server"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM user_balance WHERE user_id = ? AND server_id = ?
        """, (user_id, server_id))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserBalance(**dict(row))
        return None
    
    def add_coins(self, user_id: int, server_id: int, amount: int):
        """Add coins to user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Ensure balance entry exists
        cursor.execute("""
            INSERT OR IGNORE INTO user_balance (user_id, server_id, last_daily)
            VALUES (?, ?, ?)
        """, (user_id, server_id, (datetime.utcnow() - timedelta(days=1)).isoformat()))
        
        cursor.execute("""
            UPDATE user_balance 
            SET coins = coins + ?, total_earned = total_earned + ?
            WHERE user_id = ? AND server_id = ?
        """, (amount, amount, user_id, server_id))
        
        conn.commit()
        conn.close()
    
    def remove_coins(self, user_id: int, server_id: int, amount: int) -> bool:
        """Remove coins from user (returns False if insufficient funds)"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT coins FROM user_balance WHERE user_id = ? AND server_id = ?
        """, (user_id, server_id))
        row = cursor.fetchone()
        
        if not row or row["coins"] < amount:
            conn.close()
            return False
        
        cursor.execute("""
            UPDATE user_balance 
            SET coins = coins - ?, total_spent = total_spent + ?
            WHERE user_id = ? AND server_id = ?
        """, (amount, amount, user_id, server_id))
        
        conn.commit()
        conn.close()
        return True
    
    def add_gems(self, user_id: int, server_id: int, amount: int):
        """Add gems to user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO user_balance (user_id, server_id, last_daily)
            VALUES (?, ?, ?)
        """, (user_id, server_id, (datetime.utcnow() - timedelta(days=1)).isoformat()))
        
        cursor.execute("""
            UPDATE user_balance SET gems = gems + ? WHERE user_id = ? AND server_id = ?
        """, (amount, user_id, server_id))
        
        conn.commit()
        conn.close()
    
    def remove_gems(self, user_id: int, server_id: int, amount: int) -> bool:
        """Remove gems from user (returns False if insufficient gems)"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT gems FROM user_balance WHERE user_id = ? AND server_id = ?
        """, (user_id, server_id))
        row = cursor.fetchone()
        
        if not row or row["gems"] < amount:
            conn.close()
            return False
        
        cursor.execute("""
            UPDATE user_balance SET gems = gems - ? WHERE user_id = ? AND server_id = ?
        """, (amount, user_id, server_id))
        
        conn.commit()
        conn.close()
        return True
    
    def claim_daily_reward(self, user_id: int, server_id: int, 
                          reward_amount: int = 100) -> Tuple[bool, int]:
        """Claim daily reward (returns success and streak)"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT last_daily, daily_streak FROM user_balance 
            WHERE user_id = ? AND server_id = ?
        """, (user_id, server_id))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, 0
        
        last_daily = datetime.fromisoformat(row["last_daily"])
        now = datetime.utcnow()
        
        # Check if enough time has passed (24 hours)
        if (now - last_daily).total_seconds() < 86400:
            conn.close()
            return False, row["daily_streak"]
        
        # Calculate streak
        if (now - last_daily).total_seconds() < 172800:  # 48 hours
            new_streak = row["daily_streak"] + 1
        else:
            new_streak = 1
        
        cursor.execute("""
            UPDATE user_balance 
            SET coins = coins + ?, last_daily = ?, daily_streak = ?, total_earned = total_earned + ?
            WHERE user_id = ? AND server_id = ?
        """, (reward_amount, now.isoformat(), new_streak, reward_amount, user_id, server_id))
        
        conn.commit()
        conn.close()
        return True, new_streak
    
    def get_leaderboard(self, server_id: int, currency: str = "coins", 
                       limit: int = 10) -> List[Dict]:
        """Get server leaderboard"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if currency not in ["coins", "gems"]:
            currency = "coins"
        
        cursor.execute(f"""
            SELECT u.user_id, u.username, ub.{currency} 
            FROM user_balance ub
            JOIN users u ON ub.user_id = u.user_id
            WHERE ub.server_id = ?
            ORDER BY ub.{currency} DESC
            LIMIT ?
        """, (server_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== GAMBLING OPERATIONS ====================
    
    def record_gamble(self, user_id: int, server_id: int, game_type: str,
                     bet_amount: int, winnings: int, result: str) -> int:
        """Record gambling transaction"""
        conn = self.connect()
        cursor = conn.cursor()
        gamble = GambleRecord(
            gamble_id=0,  # Will be auto-generated
            user_id=user_id,
            server_id=server_id,
            game_type=game_type,
            bet_amount=bet_amount,
            winnings=winnings,
            result=result
        )
        
        cursor.execute("""
            INSERT INTO gamble_records 
            (user_id, server_id, game_type, bet_amount, winnings, result, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (gamble.user_id, gamble.server_id, gamble.game_type,
              gamble.bet_amount, gamble.winnings, gamble.result, gamble.timestamp))
        
        gamble_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return gamble_id
    
    def get_user_gambling_stats(self, user_id: int, server_id: int) -> Dict:
        """Get gambling statistics for user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_games,
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'lose' THEN 1 ELSE 0 END) as losses,
                SUM(bet_amount) as total_bet,
                SUM(winnings) as total_winnings,
                AVG(winnings - bet_amount) as avg_profit
            FROM gamble_records
            WHERE user_id = ? AND server_id = ?
        """, (user_id, server_id))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {}
    
    def get_gambling_history(self, user_id: int, server_id: int, 
                            limit: int = 20) -> List[GambleRecord]:
        """Get recent gambling history"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM gamble_records 
            WHERE user_id = ? AND server_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, server_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [GambleRecord(**dict(row)) for row in rows]
    
    # ==================== MODERATION OPERATIONS ====================
    
    def warn_user(self, server_id: int, user_id: int, moderator_id: int, 
                 reason: str) -> int:
        """Issue warning to user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO warnings (server_id, user_id, moderator_id, reason, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (server_id, user_id, moderator_id, reason, datetime.utcnow().isoformat()))
        
        warning_id = cursor.lastrowid
        
        # Record in moderation records
        cursor.execute("""
            INSERT INTO moderation_records 
            (server_id, user_id, moderator_id, action_type, reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (server_id, user_id, moderator_id, "warn", reason, datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
        return warning_id
    
    def get_user_warnings(self, server_id: int, user_id: int) -> List[Dict]:
        """Get all warnings for a user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT w.warning_id, u.username as moderator, w.reason, w.timestamp
            FROM warnings w
            JOIN users u ON w.moderator_id = u.user_id
            WHERE w.server_id = ? AND w.user_id = ?
            ORDER BY w.timestamp DESC
        """, (server_id, user_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def mute_user(self, server_id: int, user_id: int, moderator_id: int,
                 reason: str, duration: int) -> int:
        """Mute user for specified duration (in minutes)"""
        conn = self.connect()
        cursor = conn.cursor()
        
        now = datetime.utcnow()
        expire_time = now + timedelta(minutes=duration)
        
        cursor.execute("""
            INSERT INTO mutes 
            (server_id, user_id, moderator_id, reason, duration, mute_time, expire_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (server_id, user_id, moderator_id, reason, duration, 
              now.isoformat(), expire_time.isoformat()))
        
        mute_id = cursor.lastrowid
        
        # Record in moderation records
        cursor.execute("""
            INSERT INTO moderation_records 
            (server_id, user_id, moderator_id, action_type, reason, duration, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (server_id, user_id, moderator_id, "mute", reason, duration, 
              now.isoformat()))
        
        conn.commit()
        conn.close()
        return mute_id
    
    def unmute_user(self, server_id: int, user_id: int):
        """Unmute user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE mutes SET active = 0 WHERE server_id = ? AND user_id = ?
        """, (server_id, user_id))
        
        conn.commit()
        conn.close()
    
    def is_user_muted(self, server_id: int, user_id: int) -> bool:
        """Check if user is currently muted"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT expire_time FROM mutes 
            WHERE server_id = ? AND user_id = ? AND active = 1
        """, (server_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False
        
        expire_time = datetime.fromisoformat(row["expire_time"])
        if datetime.utcnow() > expire_time:
            return False
        
        return True
    
    def ban_user(self, server_id: int, user_id: int, moderator_id: int,
                reason: str, duration: Optional[int] = None) -> int:
        """Ban user from server"""
        conn = self.connect()
        cursor = conn.cursor()
        
        now = datetime.utcnow()
        if duration:
            expire_time = now + timedelta(minutes=duration)
        else:
            expire_time = now + timedelta(days=365*100)  # Permanent ban
        
        cursor.execute("""
            INSERT INTO bans 
            (server_id, user_id, moderator_id, reason, duration, ban_time, expire_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (server_id, user_id, moderator_id, reason, duration,
              now.isoformat(), expire_time.isoformat()))
        
        ban_id = cursor.lastrowid
        
        # Record in moderation records
        cursor.execute("""
            INSERT INTO moderation_records 
            (server_id, user_id, moderator_id, action_type, reason, duration, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (server_id, user_id, moderator_id, "ban", reason, duration, 
              now.isoformat()))
        
        conn.commit()
        conn.close()
        return ban_id
    
    def unban_user(self, server_id: int, user_id: int):
        """Unban user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE bans SET active = 0 WHERE server_id = ? AND user_id = ?
        """, (server_id, user_id))
        
        conn.commit()
        conn.close()
    
    def is_user_banned(self, server_id: int, user_id: int) -> bool:
        """Check if user is currently banned"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT expire_time FROM bans 
            WHERE server_id = ? AND user_id = ? AND active = 1
        """, (server_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False
        
        expire_time = datetime.fromisoformat(row["expire_time"])
        if datetime.utcnow() > expire_time:
            return False
        
        return True
    
    def get_moderation_history(self, server_id: int, user_id: int) -> List[Dict]:
        """Get complete moderation history for user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mr.mod_id, mr.action_type, u.username as moderator, 
                   mr.reason, mr.duration, mr.timestamp
            FROM moderation_records mr
            JOIN users u ON mr.moderator_id = u.user_id
            WHERE mr.server_id = ? AND mr.user_id = ?
            ORDER BY mr.timestamp DESC
        """, (server_id, user_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== UTILITY OPERATIONS ====================
    
    def cleanup_expired_mutes(self):
        """Remove expired mutes"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE mutes SET active = 0 
            WHERE expire_time < ? AND active = 1
        """, (datetime.utcnow().isoformat(),))
        
        conn.commit()
        conn.close()
    
    def cleanup_expired_bans(self):
        """Remove expired bans"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE bans SET active = 0 
            WHERE expire_time < ? AND active = 1
        """, (datetime.utcnow().isoformat(),))
        
        conn.commit()
        conn.close()
    
    def get_database_stats(self) -> Dict:
        """Get overall database statistics"""
        conn = self.connect()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM users")
        stats["total_users"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM server_settings")
        stats["total_servers"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gamble_records")
        stats["total_gambles"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM moderation_records")
        stats["total_moderations"] = cursor.fetchone()[0]
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager("zolory_bot.db")
    
    # Create a test user
    user = db.create_user(123456789, "test_user")
    print(f"Created user: {user.username}")
    
    # Create server settings
    settings = db.create_server_settings(987654321, "Test Server")
    print(f"Created server: {settings.server_name}")
    
    # Create user balance
    balance = db.create_user_balance(123456789, 987654321)
    print(f"Created balance for user in server")
    
    # Add coins
    db.add_coins(123456789, 987654321, 100)
    print("Added 100 coins")
    
    # Print database stats
    stats = db.get_database_stats()
    print(f"Database stats: {stats}")
