#!/usr/bin/env python3

"""Train the Benzene behavioral-cloning / DAgger policy.

- Aggregates every episode folder under DATASET_ROOT that has
  labels.csv + images/ (so DAgger iterations just add more folders).
- Time-based validation split: the LAST VAL_SPLIT fraction of each
  episode is held out, so neighbouring frames never leak into validation.
- Training augmentation: horizontal flip (angular_z negated) + brightness.
- Crops the top of the image (same area the expert ignores).

Usage:
    python3 train_behavioral_cloning.py
    python3 train_behavioral_cloning.py --epochs 40
    python3 train_behavioral_cloning.py --episodes episode_20260926_163735 test1
"""

import argparse
import csv
import os
import random

import cv2
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


# ============================================================
# Configuration
# ============================================================

DATASET_ROOT = os.path.expanduser(
    "~/ros2_ws/src/benzene/benzene_dagger/dataset"
)

MODEL_DIR = os.path.expanduser(
    "~/ros2_ws/src/benzene/benzene_dagger/models"
)
MODEL_PATH = os.path.join(MODEL_DIR, "benzene_bc_model.pth")

IMAGE_SIZE = (200, 120)      # (width, height) fed to the CNN
CROP_TOP = 0.35              # fraction of the image height removed at the top
                             # (matches the line detector's ROI)

BATCH_SIZE = 32
EPOCHS = 30
LEARNING_RATE = 1e-3
VAL_SPLIT = 0.2
FLIP_PROB = 0.5


# ============================================================
# Data loading
# ============================================================

def preprocess(frame_bgr):
    """BGR frame -> cropped, resized RGB uint8 (H, W, 3). Must match
    the preprocessing in cnn_controller.py."""
    image = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    top = int(image.shape[0] * CROP_TOP)
    image = image[top:, :]
    return cv2.resize(image, IMAGE_SIZE)


def load_episode(episode_dir):
    """Return (images uint8 [N,H,W,3], labels float32 [N]) in time order."""
    csv_path = os.path.join(episode_dir, "labels.csv")
    image_dir = os.path.join(episode_dir, "images")

    if not (os.path.isfile(csv_path) and os.path.isdir(image_dir)):
        return None

    images, labels = [], []
    with open(csv_path, "r") as f:
        for row in csv.DictReader(f):
            path = os.path.join(image_dir, row["image_file"])
            frame = cv2.imread(path)
            if frame is None:
                continue
            images.append(preprocess(frame))
            labels.append(float(row["angular_z"]))

    if not images:
        return None

    return np.stack(images), np.asarray(labels, dtype=np.float32)


class ArrayDataset(Dataset):

    def __init__(self, images, labels, augment):
        self.images = images
        self.labels = labels
        self.augment = augment

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        image = self.images[idx]
        label = float(self.labels[idx])

        if self.augment:
            if random.random() < FLIP_PROB:
                image = image[:, ::-1]      # mirror left <-> right
                label = -label              # steering flips sign too
            gain = random.uniform(0.8, 1.2)
            image = np.clip(image.astype(np.float32) * gain, 0, 255)

        image = np.ascontiguousarray(image, dtype=np.float32) / 255.0
        image = torch.from_numpy(np.transpose(image, (2, 0, 1)))
        return image, torch.tensor(label, dtype=torch.float32)


def build_datasets(root, episode_names):
    if episode_names:
        names = episode_names
    else:
        names = sorted(
            d for d in os.listdir(root)
            if os.path.isdir(os.path.join(root, d))
        )

    tr_x, tr_y, va_x, va_y = [], [], [], []

    print("Episodes:")
    for name in names:
        data = load_episode(os.path.join(root, name))
        if data is None:
            print(f"  {name}: skipped (no labels.csv/images)")
            continue

        images, labels = data
        n = len(labels)
        split = int(n * (1.0 - VAL_SPLIT))   # last chunk = validation

        tr_x.append(images[:split]); tr_y.append(labels[:split])
        va_x.append(images[split:]); va_y.append(labels[split:])

        print(f"  {name}: {n} frames "
              f"(train {split}, val {n - split}), "
              f"mean angular_z {labels.mean():+.3f}")

    if not tr_x:
        raise RuntimeError(f"No usable episodes under {root}")

    return (np.concatenate(tr_x), np.concatenate(tr_y),
            np.concatenate(va_x), np.concatenate(va_y))


# ============================================================
# CNN  (must stay identical to cnn_controller.py)
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
            nn.Flatten(),
        )

        with torch.no_grad():
            dummy = torch.zeros(1, 3, IMAGE_SIZE[1], IMAGE_SIZE[0])
            feature_size = self.features(dummy).shape[1]

        self.regressor = nn.Sequential(
            nn.Linear(feature_size, 100),
            nn.ReLU(),
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.Linear(50, 10),
            nn.ReLU(),
            nn.Linear(10, 1),
        )

    def forward(self, x):
        return self.regressor(self.features(x)).squeeze(1)


# ============================================================
# Training
# ============================================================

def run_epoch(model, loader, criterion, device, optimizer=None):
    training = optimizer is not None
    model.train(training)

    total, count = 0.0, 0
    with torch.set_grad_enabled(training):
        for images, steering in loader:
            images = images.to(device)
            steering = steering.to(device)

            predictions = model(images)
            loss = criterion(predictions, steering)

            if training:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            total += loss.item() * images.size(0)
            count += images.size(0)

    return total / max(count, 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=DATASET_ROOT)
    parser.add_argument("--episodes", nargs="*", default=None,
                        help="Episode folder names (default: all)")
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    args = parser.parse_args()

    os.makedirs(MODEL_DIR, exist_ok=True)

    train_x, train_y, val_x, val_y = build_datasets(
        args.root, args.episodes)

    if len(train_y) < 100:
        raise RuntimeError("Dataset is too small for training.")

    print(f"\nTrain: {len(train_y)} | Val: {len(val_y)}")
    print(f"Train label stats: mean {train_y.mean():+.3f}, "
          f"std {train_y.std():.3f}, "
          f"left {np.mean(train_y > 0.05):.0%}, "
          f"right {np.mean(train_y < -0.05):.0%}")
    print("(flip augmentation makes the effective left/right balanced)")
    print(f"Baseline val MSE, predict 0: {np.mean(val_y ** 2):.6f}")
    print(f"Baseline val MSE, predict train mean: "
          f"{np.mean((val_y - train_y.mean()) ** 2):.6f}\n")

    train_loader = DataLoader(
        ArrayDataset(train_x, train_y, augment=True),
        batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(
        ArrayDataset(val_x, val_y, augment=False),
        batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    model = BenzeneCNN().to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_val = float("inf")

    for epoch in range(args.epochs):
        train_loss = run_epoch(
            model, train_loader, criterion, device, optimizer)
        val_loss = run_epoch(model, val_loader, criterion, device)

        print(f"Epoch {epoch + 1:02d}/{args.epochs} "
              f"| Train Loss: {train_loss:.6f} "
              f"| Val Loss: {val_loss:.6f}")

        if val_loss < best_val:
            best_val = val_loss
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "image_size": IMAGE_SIZE,
                    "crop_top": CROP_TOP,
                    "best_val_loss": best_val,
                },
                MODEL_PATH,
            )
            print(f"  ✓ Saved best model: {MODEL_PATH}")

    print("\nTraining complete.")
    print(f"Best validation loss: {best_val:.6f}")
    print(f"Model: {MODEL_PATH}")


if __name__ == "__main__":
    main()