"""

File: duckDB.py
Author: ZackDaQuack
Last Edited: 11/27/2024


Info:

This module provides a simple interface for interacting with an SQLite database
(specifically, `duck.db`) using the `sqlite3` library. It's designed to manage
user data, including credits, quest status, and other information relevant to a
Discord bot.


Database Structure:

The module uses a single table, `users`, with the following columns:
    - user_id (INTEGER PRIMARY KEY): The Discord user ID.
    - credits (INTEGER): The user's social credits.
    - quest_status (TEXT): The user's current quest status (serialized data).


Methods:

User Data Management:
    - ensure_user(user_id): Creates a new user entry if one doesn't exist, initializing credits to 0 and quest status to an empty string.
    - user_exists(user_id): Checks if a user exists in the database.
    - delete_user(user_id): Deletes a user from the database.

Credit Management:
    - add_credits(user_id, num_to_add): Adds credits to a user.
    - deduct_credits(user_id, num_to_deduct): Deducts credits from a user.
    - set_credits(user_id, num_to_set): Sets a user's credits to a specific value.
    - get_credits(user_id): Retrieves a user's credit balance.

Quest Management:
    - set_quest_data(user_id, status): Updates a user's quest status.  `status` is expected to be a string representation of quest data (e.g., from `ast.literal_eval`).
    - get_quest_data(user_id): Retrieves a user's quest status.

Leaderboard:
    - leaderboard(user_id): Returns the top 10 users on the leaderboard (sorted by credits), the specified user's rank, and their credit balance.

Database Latency:
    - get_latency():  Measures and returns the database latency in milliseconds.

"""

import sqlite3
from time import monotonic


class DuckDB:
    def __init__(self):
        self.conn = sqlite3.connect("./storage/duck.db")
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    credits INTEGER NOT NULL,
                    quest_status TEXT
                )
            ''')

    async def add_credits(self, user_id, num_to_add):
        with self.conn:
            self.conn.execute('''
                UPDATE users
                SET credits = credits + ?
                WHERE user_id = ?
            ''', (num_to_add, user_id))

    async def deduct_credits(self, user_id, num_to_deduct):
        with self.conn:
            self.conn.execute('''
                UPDATE users
                SET credits = credits - ?
                WHERE user_id = ?
            ''', (num_to_deduct, user_id))

    async def set_credits(self, user_id, num_to_set):
        with self.conn:
            self.conn.execute('''
                UPDATE users
                SET credits = ?
                WHERE user_id = ?
            ''', (num_to_set, user_id))

    async def get_credits(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT credits
            FROM users
            WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    async def leaderboard(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            WITH ranked_users AS (
                SELECT user_id, credits,
                       ROW_NUMBER() OVER (ORDER BY credits DESC) AS rank
                FROM users
            ),
            top_10 AS (
                SELECT user_id, credits, rank
                FROM ranked_users
                WHERE rank <= 10
            ),
            user_rank AS (
                SELECT credits, rank
                FROM ranked_users
                WHERE user_id = ?
            )
            SELECT t.user_id, t.credits, t.rank, u.credits AS user_credits, u.rank AS user_rank
            FROM top_10 t
            LEFT JOIN user_rank u ON u.rank IS NOT NULL
        ''', (user_id,))

        results = cursor.fetchall()

        top_ten = [(row[0], row[1], row[2]) for row in results if row[2] <= 10]
        user_credits = results[0][3] if results and results[0][3] is not None else None
        user_rank = results[0][4] if results and results[0][4] is not None else None

        return top_ten, user_rank, user_credits

    async def set_quest_data(self, user_id, status):
        with self.conn:
            self.conn.execute('''
                UPDATE users
                SET quest_status = ?
                WHERE user_id = ?
            ''', (status, user_id))

    async def get_quest_data(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT quest_status
            FROM users
            WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    async def ensure_user(self, user_id):
        with self.conn:
            self.conn.execute('''
                INSERT OR IGNORE INTO users (user_id, credits, quest_status)
                VALUES (?, ?, ?)
            ''', (user_id, 0, ""))

    async def user_exists(self, user_id):
        with self.conn:
            result = self.conn.execute('''
                SELECT EXISTS(
                    SELECT 1 
                    FROM users 
                    WHERE user_id = ?
                )
            ''', (user_id,))
            return result.fetchone()[0] == 1

    async def delete_user(self, user_id):
        with self.conn:
            result = self.conn.execute('''
                DELETE FROM users
                WHERE user_id = ?
            ''', (user_id,))
            return result.rowcount > 0

    async def get_latency(self):
        start_time = monotonic()
        with self.conn:
            self.conn.execute('SELECT 1')
        end_time = monotonic()
        return (end_time - start_time) * 1000
