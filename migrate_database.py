#!/usr/bin/env python3
"""
Database Migration Script for Flask-Security-Too Integration
Adds new columns to existing database schema
"""
import os
import sys
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_database():
    """Migrate existing database to support Flask-Security-Too"""
    db_path = os.path.join('instance', 'mystic_echo.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    # Create backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to {backup_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting database migration...")
        
        # Check current schema
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📊 Current user table columns: {columns}")
        
        # Add new columns if they don't exist
        new_columns = [
            ("password", "VARCHAR(255)"),
            ("active", "BOOLEAN DEFAULT 1"),
            ("confirmed_at", "DATETIME"),
            ("fs_uniquifier", "VARCHAR(64) UNIQUE")
        ]
        
        # Handle password column rename if needed
        if "password_hash" in columns and "password" not in columns:
            try:
                cursor.execute("ALTER TABLE users RENAME COLUMN password_hash TO password")
                print("✅ Renamed password_hash to password")
            except sqlite3.Error as e:
                print(f"⚠️  Could not rename password_hash: {e}")
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    if "UNIQUE" in column_type:
                        # For UNIQUE columns, add without constraint first, then add constraint
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} VARCHAR(64)")
                        print(f"✅ Added column: {column_name}")
                    else:
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                        print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"⚠️  Column {column_name} might already exist: {e}")
            else:
                print(f"ℹ️  Column {column_name} already exists")
        
        # Create roles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(80) UNIQUE NOT NULL,
                description VARCHAR(255)
            )
        """)
        print("✅ Created roles table")
        
        # Create user_roles association table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INTEGER,
                role_id INTEGER,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (role_id) REFERENCES roles (id)
            )
        """)
        print("✅ Created user_roles table")
        
        # Insert default roles
        cursor.execute("INSERT OR IGNORE INTO roles (name, description) VALUES ('admin', 'Administrator')")
        cursor.execute("INSERT OR IGNORE INTO roles (name, description) VALUES ('user', 'Regular User')")
        print("✅ Inserted default roles")
        
        # Update existing users to have confirmed_at set to created_at
        cursor.execute("""
            UPDATE users 
            SET confirmed_at = created_at 
            WHERE confirmed_at IS NULL AND created_at IS NOT NULL
        """)
        print("✅ Updated existing users with confirmed_at")
        
        # Set active to True for existing users
        cursor.execute("""
            UPDATE users 
            SET active = 1 
            WHERE active IS NULL
        """)
        print("✅ Set active flag for existing users")
        
        # Generate fs_uniquifier for existing users
        import uuid
        cursor.execute("SELECT id FROM users WHERE fs_uniquifier IS NULL")
        users_without_uniquifier = cursor.fetchall()
        
        for user_id in users_without_uniquifier:
            uniquifier = str(uuid.uuid4())
            cursor.execute("UPDATE users SET fs_uniquifier = ? WHERE id = ?", (uniquifier, user_id[0]))
        
        print(f"✅ Generated fs_uniquifier for {len(users_without_uniquifier)} existing users")
        
        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Verify migration
        cursor.execute("PRAGMA table_info(users)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"📊 Updated user table columns: {new_columns}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database migration failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Main migration function"""
    print("🚀 MysticEcho Database Migration Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the MysticEcho directory.")
        return
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Database migration completed successfully!")
        print("📋 Next steps:")
        print("1. Run the user migration script to migrate existing users")
        print("2. Test the application")
        print("3. Remove old OAuth system when ready")
    else:
        print("\n❌ Database migration failed. Please check the errors above.")

if __name__ == "__main__":
    main()
