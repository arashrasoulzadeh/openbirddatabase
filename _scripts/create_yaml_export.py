#!/usr/bin/env python3
"""Create YAML export from compact CSV."""

import pandas as pd
import yaml
import subprocess
from pathlib import Path

EXPORT_DIR = Path("exports")

# Read compact CSV (has all essential fields)
df = pd.read_csv(EXPORT_DIR / 'all_birds_compact.csv')

# Convert to list of dicts
records = df.to_dict('records')

# Write YAML
yaml_path = EXPORT_DIR / 'all_birds.yaml'
with open(yaml_path, 'w', encoding='utf-8') as f:
    yaml.dump(records, f, allow_unicode=True, sort_keys=False, indent=2)

# Compress
subprocess.run(['gzip', '-k', str(yaml_path)], check=True)

print(f'YAML: {subprocess.run(["du", "-h", str(yaml_path)], capture_output=True, text=True).stdout.strip()}')
print(f'YAML.gz: {subprocess.run(["du", "-h", str(yaml_path) + ".gz"], capture_output=True, text=True).stdout.strip()}')