#!/usr/bin/env python3
"""
Deterministic placeholder predictor for diamond price integration testing.

Expected CLI argument order:
carat cut color clarity depth table x y z

This script intentionally uses a simple formula so the Java/Python integration
can be tested end-to-end until a real model is introduced.
"""

import sys


CUT_WEIGHTS = {
    "Fair": 0.90,
    "Good": 0.98,
    "Very Good": 1.03,
    "Premium": 1.07,
    "Ideal": 1.10,
}

COLOR_WEIGHTS = {
    "D": 1.08,
    "E": 1.06,
    "F": 1.04,
    "G": 1.02,
    "H": 1.00,
    "I": 0.97,
    "J": 0.94,
}

CLARITY_WEIGHTS = {
    "I1": 0.84,
    "SI2": 0.90,
    "SI1": 0.96,
    "VS2": 1.02,
    "VS1": 1.07,
    "VVS2": 1.12,
    "VVS1": 1.16,
    "IF": 1.20,
}


def main() -> int:
    if len(sys.argv) != 10:
        print("Expected 9 arguments: carat cut color clarity depth table x y z", file=sys.stderr)
        return 1

    _, carat_raw, cut, color, clarity, depth_raw, table_raw, x_raw, y_raw, z_raw = sys.argv

    try:
        carat = float(carat_raw)
        depth = float(depth_raw)
        table = float(table_raw)
        x_val = float(x_raw)
        y_val = float(y_raw)
        z_val = float(z_raw)
    except ValueError as exc:
        print(f"Numeric parsing failed: {exc}", file=sys.stderr)
        return 1

    cut_factor = CUT_WEIGHTS.get(cut, 1.0)
    color_factor = COLOR_WEIGHTS.get(color, 1.0)
    clarity_factor = CLARITY_WEIGHTS.get(clarity, 1.0)

    dimensions_score = (x_val + y_val + z_val) * 45.0
    depth_table_adjustment = (depth - 55.0) * 12.0 + (table - 55.0) * 8.0

    base_price = 4500.0 * carat + dimensions_score + depth_table_adjustment
    predicted_price = base_price * cut_factor * color_factor * clarity_factor
    predicted_price = max(predicted_price, 0.0)

    print(f"{predicted_price:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
