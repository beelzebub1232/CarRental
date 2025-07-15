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

# --- 4. Apply Carrental_schema.sql if possible ---
if os.path.exists('Carrental_schema.sql'):
    print('Carrental_schema.sql found. Please ensure your MySQL server is running and credentials are correct in config.py.')
    print('You may need to apply the schema manually if not handled by database_setup.py.')
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