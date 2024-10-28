import torch
import torch.nn as nn
from classifiers.abstractClassifier import AbstractClassifier
import torchvision
from torchvision import transforms

class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride):
        super(ConvBlock, self).__init__()
        

        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=kernel_size, stride=stride, padding=1)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=2)

        self.block = nn.Sequential(
            self.conv,
            self.bn,
            self.relu,
            self.pool,
                )
        
    def forward(self, x):
        return self.block(x)

class CNN(AbstractClassifier, nn.Module):
    
    def __init__(self, config):
        super(CNN, self).__init__()
        self.config = config
        self.model = self.init_model(config)
        
    def init_model(self, config):
        self.n_channels = config.dataset.input_size[0]
        
        first_conv = ConvBlock(self.n_channels, config.model.hyper.n_neurons, config.model.hyper.kernel_size, config.model.hyper.stride)
        
        conv_layers = [ConvBlock(config.model.hyper.n_neurons * 2**i, config.model.hyper.n_neurons * 2**(i+1), 
                                config.model.hyper.kernel_size, config.model.hyper.stride) for i in range(config.model.hyper.n_depth)]
        
        model = nn.Sequential(
            first_conv,
            *conv_layers,
            nn.Flatten(),
            nn.Linear(config.model.hyper.n_neurons * 2**config.model.hyper.n_depth * 2 * 2, config.model.hyper.linear_output_size), 
            nn.ReLU(),
            nn.Dropout(config.model.hyper.dropout),
            nn.Linear(512, config.dataset.n_classes)
            )

        return model
    
