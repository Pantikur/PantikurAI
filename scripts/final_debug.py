import os
import sys
import joblib

def debug_files():
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Проверка существования важных файлов
    files_to_check = [
        'data/chat_data.pkl',
        'create_data.py',
        'models/chat_model.pth',
        'main.py'
    ]
    
    for file in files_to_check:
        exists = os.path.exists(file)
        abs_path = os.path.abspath(file)
        print(f"{file}: exists={exists}, path={abs_path}")
        
        # Если файл существует, попробуем его прочитать
        if exists and file == 'data/chat_data.pkl':
            try:
                data = joblib.load(file)
                print(f"  vocab_size: {data['vocab_size']}")
                print(f"  max_length: {data['max_length']}")
                print(f"  word_to_idx size: {len(data['word_to_idx'])}")
                print(f"  idx_to_word size: {len(data['idx_to_word'])}")
            except Exception as e:
                print(f"  error reading: {e}")

if __name__ == "__main__":
    debug_files()