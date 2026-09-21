from backend.database import create_database

print("Setting up HireIQ database...")

success = create_database()

if success:
    print("Database setup completed successfully.")
else:
    print("Database setup failed.")