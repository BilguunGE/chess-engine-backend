from collections import OrderedDict
from torch import nn
from torch.nn import functional as F
import torch
from torch.utils.data import DataLoader, IterableDataset
from peewee import *
import base64
import numpy as np
from random import randrange
import pytorch_lightning as pl

db = SqliteDatabase('koth_training.db')

class Training_data(Model):
  id = IntegerField()
  binary = BlobField()
  evals = FloatField()

  class Meta:
    database = db

  def binary_base64(self):
    return base64.b64encode(self.binary)
db.connect()

class EvaluationDataset(IterableDataset):
  def __init__(self, count):
    self.count = count
  def __iter__(self):
    return self
  def __next__(self):
    idx = randrange(self.count)
    return self[idx]
  def __len__(self):
    return self.count
  def __getitem__(self, idx):
    eval = Training_data.get(Training_data.id == idx+1)
    bin = np.frombuffer(eval.binary, dtype=np.uint8)
    bin = np.unpackbits(bin, axis=0).astype(np.single) 
    eval.evals = max(eval.evals, -15)
    eval.evals = min(eval.evals, 15)
    ev = np.array([eval.evals]).astype(np.single) 
    return {'binary':bin, 'eval':ev}

class EvaluationModel(pl.LightningModule):
  def __init__(self,learning_rate=1e-3,batch_size=1024,layer_count=10):
    super().__init__()
    self.batch_size = batch_size
    self.learning_rate = learning_rate
    layers = []
    for i in range(layer_count-1):
      layers.append((f"linear-{i}", nn.Linear(808, 808)))
      layers.append((f"relu-{i}", nn.ReLU()))
    layers.append((f"linear-{layer_count-1}", nn.Linear(808, 1)))
    self.seq = nn.Sequential(OrderedDict(layers))

  def forward(self, x):
    return self.seq(x)

  def training_step(self, batch, batch_idx):
    x, y = batch['binary'], batch['eval']
    y_hat = self(x)
    loss = F.l1_loss(y_hat, y)
    self.log("train_loss", loss)
    return loss

  def configure_optimizers(self):
    return torch.optim.Adam(self.parameters(), lr=self.learning_rate)

  def train_dataloader(self):
    dataset = EvaluationDataset(count=1000000)
    return DataLoader(dataset, batch_size=self.batch_size, num_workers=0)