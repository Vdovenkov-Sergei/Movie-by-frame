import pytorch_lightning as pl
import torch
import torch.nn as nn
from timm import create_model

from src.utils import CLASSES, MODEL_NAME, MODEL_PT_PATH


class ViTClassifier(pl.LightningModule):
    def __init__(self, *, model_name, num_classes):
        super().__init__()
        self.save_hyperparameters()
        self.model = create_model(model_name, pretrained=True, num_classes=num_classes)
        self.model.head = nn.Linear(self.model.head.in_features, num_classes)

    def forward(self, x):
        return self.model(x)


model = ViTClassifier(model_name=MODEL_NAME, num_classes=len(CLASSES))
state_dict = torch.load(MODEL_PT_PATH)
model.load_state_dict(state_dict)
model.eval()
