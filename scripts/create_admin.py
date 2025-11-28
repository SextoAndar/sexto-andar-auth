#!/usr/bin/env python3
"""
Script to create admin users via command line arguments
Usage: python scripts/create_admin.py <username> <full_name> <email> <password> [phone_number]
Example: python scripts/create_admin.py admin123 "Admin User" admin@example.com adminpass123 1111111111
"""

import sys
import os
import asyncio

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from sqlalchemy.orm import Session
from app.database.connection import connect_db, disconnect_db, SessionLocal
from app.models.account import Account, RoleEnum
from app.auth.password_handler import hash_password
from app.repositories.account_repository import AccountRepository

async def create_admin(username, full_name, email, password, phone_number=None):
    """Create admin with provided arguments"""
    print("=" * 60)
    print("          ADMIN USER CREATION SCRIPT")
    print("=" * 60)
    print()
    
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        await connect_db()
        print("✅ Connected to database successfully")
        print()
        
        # Get database session
        db: Session = SessionLocal()
        account_repo = AccountRepository(db)
        
        # Validate inputs
        print("Validating input data...")
        
        # Username validation
        if len(username) < 3 or len(username) > 50:
            print("❌ Username must be between 3 and 50 characters!")
            return False
        
        if not username.replace('_', '').replace('-', '').isalnum():
            print("❌ Username must contain only letters, numbers and underscore!")
            return False
        
        if account_repo.username_exists(username):
            print("❌ Username already exists!")
            return False
        
        # Full name validation
        if len(full_name) < 2 or len(full_name) > 100:
            print("❌ Full name must be between 2 and 100 characters!")
            return False
        
        # Email validation
        if '@' not in email or '.' not in email.split('@')[1]:
            print("❌ Please provide a valid email address!")
            return False
        
        if account_repo.email_exists(email):
            print("❌ Email already exists!")
            return False
        
        # Password validation
        if len(password) < 8:
            print("❌ Password must have at least 8 characters!")
            return False
        
        print("✅ All validations passed")
        print()
        
        print("📋 Admin user information:")
        print(f"   Username: {username}")
        print(f"   Full Name: {full_name}")
        print(f"   Email: {email}")
        print(f"   Phone: {phone_number or 'Not provided'}")
        print("   Role: Administrator")
        print()
        
        # Create admin user
        print("🔐 Creating admin user...")
        
        hashed_password = hash_password(password)
        
        admin_user = Account(
            username=username.lower(),
            fullName=full_name,
            email=email.lower(),
            phoneNumber=phone_number,
            password=hashed_password,
            role=RoleEnum.ADMIN
        )
        
        created_admin = account_repo.create(admin_user)
        
        print("✅ Admin user created successfully!")
        print()
        print("👤 Admin Details:")
        print(f"   ID: {created_admin.id}")
        print(f"   Username: {created_admin.username}")
        print(f"   Full Name: {created_admin.fullName}")
        print(f"   Email: {created_admin.email}")
        print(f"   Role: {created_admin.get_role_display()}")
        print(f"   Created: {created_admin.created_at}")
        print()
        print("🎉 You can now login with these credentials!")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()
        await disconnect_db()
    
    return True

def print_usage():
    """Print usage instructions"""
    print("Usage: python scripts/create_admin.py <username> <full_name> <email> <password> [phone_number]")
    print()
    print("Arguments:")
    print("  username     - Admin username (3-50 chars, letters/numbers/underscore only)")
    print("  full_name    - Admin full name (2-100 chars, use quotes if contains spaces)")
    print("  email        - Admin email address")
    print("  password     - Admin password (minimum 8 characters)")
    print("  phone_number - Admin phone number (optional)")
    print()
    print("Examples:")
    print('  python scripts/create_admin.py admin123 "Admin User" admin@example.com adminpass123')
    print('  python scripts/create_admin.py admin123 "Admin User" admin@example.com adminpass123 1111111111')

def main():
    """Main function"""
    # Check arguments
    if len(sys.argv) < 5:
        print("❌ Error: Missing required arguments")
        print()
        print_usage()
        sys.exit(1)
    
    if len(sys.argv) > 6:
        print("❌ Error: Too many arguments")
        print()
        print_usage()
        sys.exit(1)
    
    # Parse arguments
    username = sys.argv[1]
    full_name = sys.argv[2]
    email = sys.argv[3]
    password = sys.argv[4]
    phone_number = sys.argv[5] if len(sys.argv) == 6 else None
    
    # Run async function
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        success = asyncio.run(create_admin(username, full_name, email, password, phone_number))
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
