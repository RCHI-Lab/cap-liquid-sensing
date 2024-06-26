# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 18:57:06 2023

@author: yexin
"""

import os
import numpy as np
import torch
from torch.utils.data import Dataset
import pickle
from tqdm import tqdm
import torch.nn.functional as F
import random







class data_train_10(Dataset):
    def __init__(self, cap):
        self.cap = cap
        # Assuming each item in cap can give at least 20 readings
        self.total_sequences = sum([len(item) - 9 for item in cap])

    def __len__(self):
        return self.total_sequences

    def __getitem__(self, idx):
        cumulative_lengths = np.cumsum([len(item) - 9 for item in self.cap])
        num = np.searchsorted(cumulative_lengths, idx + 1)

        # If it's the first sequence, start from 0, else determine the starting point based on idx
        if num == 0:
            start_idx = idx
        else:
            start_idx = idx - cumulative_lengths[num - 1]

        capacitance = self.cap[num][start_idx: start_idx + 10]

        return torch.tensor(capacitance), torch.tensor(num), torch.tensor(start_idx)
    
class data_test_10(Dataset):
    def __init__(self, cap):
        self.cap = cap
        # Assuming each item in cap can give at least 20 readings
        self.total_sequences = sum([len(item) - 9 for item in cap])

    def __len__(self):
        return self.total_sequences

    def __getitem__(self, idx):
        cumulative_lengths = np.cumsum([len(item) - 9 for item in self.cap])
        num = np.searchsorted(cumulative_lengths, idx + 1)

        # If it's the first sequence, start from 0, else determine the starting point based on idx
        if num == 0:
            start_idx = idx
        else:
            start_idx = idx - cumulative_lengths[num - 1]

        capacitance = self.cap[num][start_idx: start_idx + 10]

        return torch.tensor(capacitance), torch.tensor(num), torch.tensor(start_idx)

    





class data_train_bc(Dataset):
    def __init__(self, cap, b):
        self.cap = cap
        self.b = b
        # Assuming each item in cap can give at least 20 readings
        self.total_sequences = sum([len(item) - 9 for item in cap])

    def __len__(self):
        return self.total_sequences

    def __getitem__(self, idx):
        cumulative_lengths = np.cumsum([len(item) - 9 for item in self.cap])
        num = np.searchsorted(cumulative_lengths, idx + 1)

        # If it's the first sequence, start from 0, else determine the starting point based on idx
        if num == 0:
            start_idx = idx
        else:
            start_idx = idx - cumulative_lengths[num - 1]

        capacitance = self.cap[num][start_idx: start_idx + 10]
        bh = self.b[num][start_idx: start_idx + 10]
        if np.mean(bh) > 0.01:
            a = 1
        else:
            a = 0

        return torch.tensor(capacitance), torch.tensor(num), torch.tensor(a)
    
    
    
class data_test_bc(Dataset):
    def __init__(self, cap, b):
        self.cap = cap
        self.b = b
        # Assuming each item in cap can give at least 20 readings
        self.total_sequences = sum([len(item) - 9 for item in cap])

    def __len__(self):
        return self.total_sequences

    def __getitem__(self, idx):
        cumulative_lengths = np.cumsum([len(item) - 9 for item in self.cap])
        num = np.searchsorted(cumulative_lengths, idx + 1)

        # If it's the first sequence, start from 0, else determine the starting point based on idx
        if num == 0:
            start_idx = idx
        else:
            start_idx = idx - cumulative_lengths[num - 1]

        capacitance = self.cap[num][start_idx: start_idx + 10]
        bh = self.b[num][start_idx: start_idx + 10]
        if np.mean(bh) > 0.01:
            a = 1
        else:
            a = 0

        return torch.tensor(capacitance), torch.tensor(num), torch.tensor(a)






