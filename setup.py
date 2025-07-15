import sys
import subprocess
import os
import shutil

# --- 1. Check Python version ---
MIN_PYTHON = (3, 7)
if sys.version_info < MIN_PYTHON:
    sys.exit(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or higher is required. Current: {sys.version_info.major}.{sys.version_info.minor}")

# --- 2. Install requirements if requirements.txt exists ---
if os.path.exists('requirements.txt'):
    print('Installing dependencies from requirements.txt...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
else:
    print('No requirements.txt found. Skipping dependency installation.')

# --- 3. Run database_setup.py ---
if os.path.exists('database_setup.py'):
    print('Setting up the database (database_setup.py)...')
    subprocess.check_call([sys.executable, 'database_setup.py'])
else:
    print('database_setup.py not found. Skipping database setup.')

# --- 4. Apply Carrental_schema.sql automatically ---
if os.path.exists('Carrental_schema.sql'):
    print('Applying Carrental_schema.sql to the database...')
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        import mysql.connector
        with open('Carrental_schema.sql', 'r', encoding='utf-8') as f:
            sql_commands = f.read()
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        cursor = conn.cursor()
        for result in cursor.execute(sql_commands, multi=True):
            pass  # Just execute all
        conn.commit()
        cursor.close()
        conn.close()
        print('Carrental_schema.sql applied successfully!')
    except Exception as e:
        print(f'Error applying Carrental_schema.sql: {e}')
else:
    print('Carrental_schema.sql not found. Skipping schema application.')

# --- 5. Ensure static and template folders exist ---
folders = [
    'static/css',
    'static/js',
    'templates/admin',
    'templates/customer',
]
for folder in folders:
    if not os.path.exists(folder):
        print(f'Creating missing folder: {folder}')
        os.makedirs(folder, exist_ok=True)
    else:
        print(f'Folder exists: {folder}')

print('\nSetup complete!')
print('You can now run your app with: python app.py') 