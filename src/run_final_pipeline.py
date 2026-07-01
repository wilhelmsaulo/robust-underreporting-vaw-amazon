#!/usr/bin/env python3
"""Run the final analytical stages used by the manuscript.

Restricted source data and preprocessing outputs must already be available in
`data/processed/` before this script is executed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = [
    'robust_underreporting_v17.py',
    'spatial_access_services_v18.py',
    'pareto_validation_v20.py',
    'sensitivity_scenario_factors_v22.py',
    'electre_tri_b_v25.py',
]


def main() -> None:
    for stage in STAGES:
        path = ROOT / 'src' / stage
        print(f'\n=== Running {stage} ===')
        subprocess.run([sys.executable, str(path)], check=True, cwd=ROOT)
    print('\nFinal analytical pipeline completed successfully.')


if __name__ == '__main__':
    main()
