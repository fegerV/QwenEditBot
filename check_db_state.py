#!/usr/bin/env python3
"""Check database state"""

import sqlite3

def check_database():
    """Check the state of the database"""
    print("Checking database state...")
    
    with sqlite3.connect('backend/qwen.db') as conn:
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in database: {[table[0] for table in tables]}")
        
        # Check presets
        cursor.execute('SELECT COUNT(*) FROM presets;')
        preset_count = cursor.fetchone()[0]
        print(f"Number of presets: {preset_count}")
        
        if preset_count > 0:
            cursor.execute('SELECT name, category, price FROM presets LIMIT 10;')
            records = cursor.fetchall()
            print('Sample presets:')
            for record in records:
                print(f'  {record[0]} ({record[1]}) - {record[2]} points')
        
        # Check users
        cursor.execute('SELECT COUNT(*) FROM users;')
        user_count = cursor.fetchone()[0]
        print(f"Number of users: {user_count}")
        
        # Check other tables
        cursor.execute('SELECT COUNT(*) FROM jobs;')
        job_count = cursor.fetchone()[0]
        print(f"Number of jobs: {job_count}")
        
        cursor.execute('SELECT COUNT(*) FROM payments;')
        payment_count = cursor.fetchone()[0]
        print(f"Number of payments: {payment_count}")

if __name__ == "__main__":
    check_database()