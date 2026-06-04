import os
import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir()} if os.path.exists('.') else 'Directory not accessible'")

# Попробуем найти файлы вручную
print("\nChecking for project files:")
base_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Base directory: {base_dir}")

data_dir = os.path.join(base_dir, '..', 'data')
print(f"Data directory: {data_dir}, exists: {os.path.exists(data_dir)}")

conversations_file = os.path.join(data_dir, 'conversations.json')
print(f"Conversations file: {conversations_file}, exists: {os.path.exists(conversations_file)}")

models_dir = os.path.join(base_dir, '..', 'models')
print(f"Models directory: {models_dir}, exists: {os.path.exists(models_dir)}")

create_data_file = os.path.join(base_dir, '..', 'create_data.py')
print(f"Create data file: {create_data_file}, exists: {os.path.exists(create_data_file)}")