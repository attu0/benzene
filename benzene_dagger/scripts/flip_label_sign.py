#!/usr/bin/env python3

"""Negate angular_z in labels.csv for episodes recorded with the OLD expert.

The old expert steered AWAY from the line (sign inverted). The magnitude
was correct, so the right label is simply the negative of the stored one.

For each episode folder this script
  * copies labels.csv -> labels_original_sign.csv   (backup)
  * rewrites labels.csv with angular_z negated
  * writes a .sign_flipped marker, so running it twice cannot flip back

Usage:
    python3 flip_label_sign.py                       # all episodes
    python3 flip_label_sign.py --episodes test1 episode_20260926_163735
    python3 flip_label_sign.py --undo                # restore the backups
    python3 flip_label_sign.py --dry-run
"""

import argparse
import csv
import os
import shutil

DEFAULT_ROOT = os.path.expanduser(
    "~/ros2_ws/src/benzene/benzene_dagger/dataset"
)


def flip(ep_dir, dry_run=False):
    csv_path = os.path.join(ep_dir, "labels.csv")
    backup = os.path.join(ep_dir, "labels_original_sign.csv")
    marker = os.path.join(ep_dir, ".sign_flipped")
    name = os.path.basename(ep_dir)

    if not os.path.isfile(csv_path):
        print(f"{name}: no labels.csv, skipped")
        return
    if os.path.exists(marker):
        print(f"{name}: already flipped, skipped")
        return

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    if dry_run:
        print(f"{name}: would flip {len(rows)} rows")
        return

    shutil.copy2(csv_path, backup)
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            row["angular_z"] = f"{-float(row['angular_z']):.6f}"
            writer.writerow(row)
    with open(marker, "w") as f:
        f.write("angular_z negated\n")
    print(f"{name}: flipped {len(rows)} rows (backup: labels_original_sign.csv)")


def undo(ep_dir):
    backup = os.path.join(ep_dir, "labels_original_sign.csv")
    marker = os.path.join(ep_dir, ".sign_flipped")
    name = os.path.basename(ep_dir)
    if os.path.isfile(backup) and os.path.exists(marker):
        shutil.copy2(backup, os.path.join(ep_dir, "labels.csv"))
        os.remove(marker)
        print(f"{name}: restored original labels")
    else:
        print(f"{name}: nothing to undo")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--episodes", nargs="*", default=None)
    parser.add_argument("--undo", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    names = args.episodes or sorted(
        d for d in os.listdir(args.root)
        if os.path.isdir(os.path.join(args.root, d)))

    for name in names:
        ep_dir = os.path.join(args.root, name)
        if args.undo:
            undo(ep_dir)
        else:
            flip(ep_dir, args.dry_run)


if __name__ == "__main__":
    main()