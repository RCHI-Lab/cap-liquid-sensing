# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 18:12:13 2023

@author: yexin
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import torch.nn.init as init
from torchvision.models import resnet18


def prepare_sequence(data, max_length=100):
    # If data is shorter than max_length, pad it
    if len(data) < max_length:
        padding_length = max_length - len(data)
        # Assuming you pad with zeros
        padded_data = torch.cat([data, torch.zeros(padding_length)], dim=0)
        # Create a mask: 1 for real tokens, 0 for padding tokens
        mask = torch.cat([torch.ones(len(data)), torch.zeros(padding_length)], dim=0)
    # If data is longer than max_length, truncate it
    elif len(data) > max_length:
        padded_data = data[:max_length]
        mask = torch.ones(max_length)
    # If data is exactly max_length
    else:
        padded_data = data
        mask = torch.ones(max_length)
    
    return padded_data, mask





    
class MLP_2_10_resnet_class(nn.Module):
    def __init__(self, d_model=256, output_dim=3, class_size = 5, embedding_dim = 50):
        super(MLP_2_10_resnet_class, self).__init__()
        
        self.projection = nn.Linear(10 * 10 + embedding_dim, d_model)
        self.linears = nn.ModuleList([nn.Linear(d_model, d_model) for _ in range(7)])
        self.out = nn.Linear(d_model, output_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.05)
        self.embedding = nn.Embedding(num_embeddings = class_size, embedding_dim=embedding_dim)
        
        # for linear in self.linears:
        #     init.kaiming_normal_(linear.weight)  # He Initialization
        #     init.zeros_(linear.bias)             # Zero Initialization for Bias
            
        # init.xavier_uniform_(self.out.weight)  # Xavier Initialization
        
    def forward(self, x, label):
        batch_size, seq_len, shape = x.shape
        label = self.embedding(label)
        # label = torch.nn.functional.one_hot(label, num_classes=3)
        x = x.reshape(batch_size, -1)
        x = torch.concatenate((x, label), dim = 1)
        x = self.projection(x)
        x = self.relu(x)
        
        for linear in self.linears:
            a = x
            x = linear(x)
            x = self.relu(x)
            x = self.dropout(x) 
            x += a
            
            
        x = self.out(x)
        x = self.relu(x)
        weight = x[:, 0]
        offset_1 = x[:, 1]
        offset_2 = x[:, 2]
        
        return weight, offset_1, offset_2   
    
    








class MLP_bc(nn.Module):
    def __init__(self, d_model=256, output_dim=1, class_size = 5, weight_size = 4, embedding_dim = 50):
        super(MLP_bc, self).__init__()
        
        self.projection = nn.Linear(10 * 10 + embedding_dim * 2, d_model)
        self.linears = nn.ModuleList([nn.Linear(d_model, d_model) for _ in range(7)])
        self.out = nn.Linear(d_model, output_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.05)
        self.embedding1 = nn.Embedding(num_embeddings = class_size, embedding_dim=embedding_dim)
        self.embedding2 = nn.Embedding(num_embeddings = weight_size, embedding_dim=embedding_dim)
        
        self.sig = nn.Sigmoid()

        
    def forward(self, x, label, weight):
        batch_size, seq_len, shape = x.shape
        label = self.embedding1(label)
        weight = self.embedding2(weight)
        
        x = x.reshape(batch_size, -1)
        x = torch.concatenate((x, label, weight), dim = 1)

        x = self.projection(x)
        x = self.relu(x)
        
        for linear in self.linears:
            a = x
            x = linear(x)
            x = self.relu(x)
            x = self.dropout(x) 
            x += a
            
            
        x = self.out(x)
        x = self.sig(x)
        x = x[:, 0]

        
        return x




    
    
    
    
