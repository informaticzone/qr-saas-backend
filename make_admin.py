"""
Script to promote a user to admin role
"""
import sys
from app.database import SessionLocal
from app.models.user import User, UserRole


def make_admin(email: str):
    """Promote user to admin by email"""
    db = SessionLocal()
    try:
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            return False
        
        # Update role to admin
        user.role = UserRole.ADMIN
        user.is_verified = True  # Make sure admin is verified
        db.commit()
        
        print(f"✅ User '{email}' promoted to ADMIN")
        print(f"   Name: {user.full_name}")
        print(f"   ID: {user.id}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def list_users():
    """List all users"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            print("❌ No users found in database")
            return
        
        print("\n📋 Users in database:")
        print("-" * 80)
        for user in users:
            print(f"Email: {user.email}")
            print(f"Name: {user.full_name}")
            print(f"Role: {user.role}")
            print(f"Verified: {user.is_verified}")
            print(f"Subscription: {user.subscription_plan}")
            print("-" * 80)
        
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python make_admin.py <email>          - Make user admin")
        print("  python make_admin.py --list           - List all users")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_users()
    else:
        email = sys.argv[1]
        make_admin(email)
