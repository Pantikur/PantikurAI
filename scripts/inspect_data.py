import joblib

data = joblib.load('data/chat_data.pkl')

print(f"Vocab size: {data['vocab_size']}")
print(f"Max length: {data['max_length']}")
print(f"Word to idx keys: {len(data['word_to_idx'])}")
print(f"Idx to word keys: {len(data['idx_to_word'])}")
print(f"Sample words: {list(data['word_to_idx'].keys())[:10]}")