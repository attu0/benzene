#!/usr/bin/env python3

import os
import csv
import random

import cv2
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split


# ============================================================
# Configuration
# ============================================================

DATASET_DIR = os.path.expanduser(
    "~/ros2_ws/src/benzene/benzene_dagger/dataset/episode_20260926_163735"
)

IMAGE_SIZE = (200, 120)

BATCH_SIZE = 32
EPOCHS = 30
LEARNING_RATE = 1e-3

VAL_SPLIT = 0.2

MODEL_DIR = os.path.expanduser(
    "~/ros2_ws/src/benzene/benzene_dagger/models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "benzene_bc_model.pth"
)


# ============================================================
# Dataset
# ============================================================

class BenzeneDataset(Dataset):

    def __init__(self, dataset_dir):

        self.dataset_dir = dataset_dir
        self.image_dir = os.path.join(dataset_dir, "images")
        self.csv_path = os.path.join(dataset_dir, "labels.csv")

        self.samples = []

        with open(self.csv_path, "r") as f:

            reader = csv.DictReader(f)

            for row in reader:

                image_path = os.path.join(
                    self.image_dir,
                    row["image_file"]
                )

                if os.path.exists(image_path):

                    angular_z = float(row["angular_z"])

                    self.samples.append(
                        (image_path, angular_z)
                    )

        print(f"Loaded {len(self.samples)} samples")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):

        image_path, steering = self.samples[idx]

        image = cv2.imread(image_path)

        if image is None:
            raise RuntimeError(
                f"Could not read image: {image_path}"
            )

        # BGR -> RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Resize
        image = cv2.resize(
            image,
            IMAGE_SIZE
        )

        # Normalize
        image = image.astype(np.float32) / 255.0

        # HWC -> CHW
        image = np.transpose(
            image,
            (2, 0, 1)
        )

        image = torch.tensor(
            image,
            dtype=torch.float32
        )

        steering = torch.tensor(
            steering,
            dtype=torch.float32
        )

        return image, steering


# ============================================================
# CNN
# ============================================================

class BenzeneCNN(nn.Module):

    def __init__(self):

        super().__init__()

        self.features = nn.Sequential(

            nn.Conv2d(3, 24, kernel_size=5, stride=2),
            nn.ReLU(),

            nn.Conv2d(24, 36, kernel_size=5, stride=2),
            nn.ReLU(),

            nn.Conv2d(36, 48, kernel_size=5, stride=2),
            nn.ReLU(),

            nn.Conv2d(48, 64, kernel_size=3),
            nn.ReLU(),

            nn.Conv2d(64, 64, kernel_size=3),
            nn.ReLU(),

            nn.Flatten()
        )

        # Determine flattened size automatically
        with torch.no_grad():

            dummy = torch.zeros(
                1,
                3,
                IMAGE_SIZE[1],
                IMAGE_SIZE[0]
            )

            feature_size = self.features(dummy).shape[1]

        self.regressor = nn.Sequential(

            nn.Linear(feature_size, 100),
            nn.ReLU(),

            nn.Linear(100, 50),
            nn.ReLU(),

            nn.Linear(50, 10),
            nn.ReLU(),

            nn.Linear(10, 1)
        )

    def forward(self, x):

        x = self.features(x)

        return self.regressor(x).squeeze(1)


# ============================================================
# Training
# ============================================================

def main():

    os.makedirs(MODEL_DIR, exist_ok=True)

    dataset = BenzeneDataset(DATASET_DIR)

    if len(dataset) < 100:

        raise RuntimeError(
            "Dataset is too small for training."
        )

    val_size = int(
        len(dataset) * VAL_SPLIT
    )

    train_size = len(dataset) - val_size

    train_dataset, val_dataset = random_split(
        dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=2
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=2
    )

    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "cpu"
    )

    print(f"Device: {device}")
    print(f"Training samples: {train_size}")
    print(f"Validation samples: {val_size}")

    model = BenzeneCNN().to(device)

    criterion = nn.MSELoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    best_val_loss = float("inf")

    for epoch in range(EPOCHS):

        # ----------------------------------------------------
        # Training
        # ----------------------------------------------------

        model.train()

        train_loss = 0.0

        for images, steering in train_loader:

            images = images.to(device)
            steering = steering.to(device)

            optimizer.zero_grad()

            predictions = model(images)

            loss = criterion(
                predictions,
                steering
            )

            loss.backward()

            optimizer.step()

            train_loss += loss.item() * images.size(0)

        train_loss /= train_size

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        model.eval()

        val_loss = 0.0

        with torch.no_grad():

            for images, steering in val_loader:

                images = images.to(device)
                steering = steering.to(device)

                predictions = model(images)

                loss = criterion(
                    predictions,
                    steering
                )

                val_loss += loss.item() * images.size(0)

        val_loss /= val_size

        print(
            f"Epoch {epoch + 1:02d}/{EPOCHS} "
            f"| Train Loss: {train_loss:.6f} "
            f"| Val Loss: {val_loss:.6f}"
        )

        # Save best model

        if val_loss < best_val_loss:

            best_val_loss = val_loss

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "image_size": IMAGE_SIZE,
                    "best_val_loss": best_val_loss
                },
                MODEL_PATH
            )

            print(
                f"  ✓ Saved best model: {MODEL_PATH}"
            )

    print()
    print("Training complete.")
    print(f"Best validation loss: {best_val_loss:.6f}")
    print(f"Model: {MODEL_PATH}")


if __name__ == "__main__":
    main()