from database.database import engine, Base
from models import models # Import models to ensure they are registered

print("🗑️ Wiping old database tables...")
# This drops all existing tables (deleting the old "10.7K" text data)
Base.metadata.drop_all(bind=engine)

print("✨ Recreating fresh tables with correct Integer columns...")
# This creates brand new, clean tables
Base.metadata.create_all(bind=engine)

print("✅ Database is now clean and ready for fresh integer seed data!")