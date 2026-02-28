# Quick Setup Guide

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Run the Application

```bash
python main.py
```

That's it! The application will automatically:
- Create the SQLite database file (`vyapaarsetgo.db`) if it doesn't exist
- Create all required tables
- Create a default admin user (username: `admin`, password: `admin123`)

## Step 3: Login

- **Username:** `admin`
- **Password:** `admin123`

## No Database Server Required!

This application uses **SQLite**, which means:
- ✅ No MySQL, PostgreSQL, or any other database server needed
- ✅ Database is stored in a single file (`vyapaarsetgo.db`)
- ✅ Works immediately after installing Python dependencies
- ✅ Easy to backup (just copy the .db file)

## Troubleshooting

### Import Errors
- Make sure you're running from the project root directory
- Verify all dependencies are installed: `pip install -r requirements.txt`

### UI Not Displaying
- Check Python version (requires 3.8+)
- Ensure CustomTkinter is installed: `pip install customtkinter`

### Database File Issues
- Ensure you have write permissions in the application directory
- If the database file is corrupted, delete `vyapaarsetgo.db` and restart the application (it will recreate it)

## Next Steps

1. Change the default admin password in the database
2. Add your first products in the Inventory module
3. Add suppliers in the Supplier Management module
4. Add customers in the Customer Khata module
5. Start processing sales!

## Database Location

The database file (`vyapaarsetgo.db`) will be created in the same directory as `main.py`. You can change this by modifying `DB_PATH` in `config.py`.

## Backup

To backup your data:
1. Close the application
2. Copy `vyapaarsetgo.db` to a safe location

To restore:
1. Close the application
2. Replace `vyapaarsetgo.db` with your backup file
