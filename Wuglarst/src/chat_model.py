import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pickle

class ChatDataset(Dataset):
    def __init__(self, data_file):
        with open(data_file, 'rb') as f:
            data = pickle.load(f)
        
        self.input_sequences = data['input_sequences']
        self.target_sequences = data['target_sequences']
    
    def __len__(self):
        return len(self.input_sequences)
    
    def __getitem__(self, idx):
        return torch.tensor(self.input_sequences[idx]), torch.tensor(self.target_sequences[idx])

class ChatNN(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers=2):
        super(ChatNN, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, x, hidden=None):
        x = self.embedding(x)
        lstm_out, hidden = self.lstm(x, hidden)
        output = self.fc(lstm_out)
        return output, hidden

def train_model(data_file, vocab_size, embedding_dim=128, hidden_dim=256, num_layers=2, epochs=100, batch_size=32, lr=0.001):
    
        dataset = ChatDataset(data_file)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        model = ChatNN(vocab_size, embedding_dim, hidden_dim, num_layers)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=lr)
        
        model.train()
        for epoch in range(epochs):
            total_loss = 0
            for inputs, targets in dataloader:
                optimizer.zero_grad()
                
                outputs, _ = model(inputs)
                loss = criterion(outputs.view(-1, vocab_size), targets.view(-1))
                
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Loss: {total_loss/len(dataloader):.4f}')
        
        torch.save(model.state_dict(), 'Wuglarst/models/chat_model.pth')
        print('Model trained and saved successfully!')
        return model