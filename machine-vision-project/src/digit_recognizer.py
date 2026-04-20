import torch
import torch.nn as nn
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import os

from .utils import preprocess_digit

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.relu2(x)
        x = self.pool2(x)
        x = x.view(-1, 64 * 7 * 7)
        x = self.fc1(x)
        x = self.relu3(x)
        x = self.fc2(x)
        return x

class DigitRecognizer:
    def __init__(self, model_path='models/digit_model.pth'):
        self.model_path = model_path
        self.device = torch.device('cpu')
        self.model = SimpleCNN().to(self.device)
        
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        else:
            self.train_model()
        
        self.model.eval()
    
    def train_model(self):
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        
        train_dataset = datasets.MNIST(
            root='./data', train=True, download=True, transform=transform
        )
        train_loader = torch.utils.data.DataLoader(
            train_dataset, batch_size=64, shuffle=True
        )
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        print("Training digit recognition model...")
        for epoch in range(3):
            self.model.train()
            total_loss = 0
            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = data.to(self.device), target.to(self.device)
                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)
            print(f"Epoch {epoch+1}/3, Loss: {avg_loss:.4f}")
        
        os.makedirs('models', exist_ok=True)
        torch.save(self.model.state_dict(), self.model_path)
        print(f"Model saved to {self.model_path}")
    
    def predict(self, image):
        processed = preprocess_digit(image)
        tensor = torch.tensor(processed, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(tensor)
            pred = output.argmax(dim=1, keepdim=True).item()
        
        return pred