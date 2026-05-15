import pickle
import numpy as np
import re
from collections import Counter

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Zа-яА-Я\s]', '', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def build_vocabulary(sentences, vocab_size=10000):
    # Preprocess all sentences
    processed_sentences = [preprocess_text(sent) for sent in sentences]
    
    # Tokenize
    words = []
    for sent in processed_sentences:
        words.extend(sent.split())
    
    # Count word frequencies
    word_counts = Counter(words)
    
    # Get most common words
    vocab_words = [word for word, count in word_counts.most_common(vocab_size - 2)]
    
    # Create vocabulary dictionaries
    word_to_idx = {'<PAD>': 0, '<UNK>': 1}
    idx_to_word = {0: '<PAD>', 1: '<UNK>'}
    
    for i, word in enumerate(vocab_words, 2):
        word_to_idx[word] = i
        idx_to_word[i] = word
    
    return word_to_idx, idx_to_word

def sentences_to_sequences(sentences, word_to_idx, max_length=50):
    sequences = []
    
    for sent in sentences:
        processed_sent = preprocess_text(sent)
        words = processed_sent.split()
        
        # Convert words to indices
        seq = [word_to_idx.get(word, word_to_idx['<UNK>']) for word in words]
        
        # Pad or truncate
        if len(seq) < max_length:
            seq += [word_to_idx['<PAD>']] * (max_length - len(seq))
        else:
            seq = seq[:max_length]
            
        sequences.append(seq)
    
    return np.array(sequences)

def prepare_chat_dataset(conversations, vocab_size=10000, max_length=50):
    # Extract all messages (assuming conversations is a list of [input, response] pairs)
    all_input_texts = [conv[0] for conv in conversations]
    all_response_texts = [conv[1] for conv in conversations]
    
    # Build vocabulary from all texts
    all_texts = all_input_texts + all_response_texts
    word_to_idx, idx_to_word = build_vocabulary(all_texts, vocab_size)
    
    # Convert to sequences
    input_sequences = sentences_to_sequences(all_input_texts, word_to_idx, max_length)
    target_sequences = sentences_to_sequences(all_response_texts, word_to_idx, max_length)
    
    # Save data and vocabulary
    data = {
        'input_sequences': input_sequences,
        'target_sequences': target_sequences,
        'word_to_idx': word_to_idx,
        'idx_to_word': idx_to_word,
        'vocab_size': len(word_to_idx),
        'max_length': max_length
    }
    
    with open('Wuglarst/data/chat_data.pkl', 'wb') as f:
        pickle.dump(data, f)
    
    print(f'Dataset prepared with {len(word_to_idx)} vocabulary size')
    print(f'Saved {len(input_sequences)} conversation pairs')
    
    return data