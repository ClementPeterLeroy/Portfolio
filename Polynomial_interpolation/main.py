import pandas as pd
import random as rd
import numpy as np
from matplotlib import pyplot as plt

"""
Price Approximator — Polynomial Interpolation Tool
===================================================
Given 2-5 paris of (parameter, price) fits a polynomial and allows to solve for an unknown
parameter or price. Produces a detailed matplotlib figure.

Designed to showcase matplotlib knowledge.

v1.0.5
Improved by brentq method to find the exact solution

Potential notes for v2.0
T-kinter interface or Streamlit app ? 
"""

## Import and definitions

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.optimize import brentq


## Input Output


def get_pairs(n: int):
    """Interactively collect n (parameter, price) pairs from the user."""
    print(f"\n{'─'*50}")
    print(f"  Enter {n} (parameter, price) pairs")
    print(f"{'─'*50}")
    pairs: list[tuple[float, float]] = []
    for i in range(1, n + 1):
        while True:
            try:
                raw = input(f"  Pair {i}  →  parameter price : ").strip()
                x_str, y_str = raw.split()
                pairs.append((float(x_str), float(y_str)))
                break
            except (ValueError, TypeError):
                print("Please enter exactly two numbers separated by a space!")
    return pairs


def get_target_price():
    """Ask the user for the price whose parameter they want to find."""
    while True:
        try:
            val = float(input("\n  Target price to solve for: ").strip())
            return val
        except ValueError:
            print("Please enter a valid number!")



## Mathematics
def fit_polynomial(pairs: list[tuple[float, float]]):
    """Fit an (n-1)-degree polynomial through n exact points."""
    xs = np.array([p[0] for p in pairs])
    ys = np.array([p[1] for p in pairs])
    degree = len(pairs) - 1
    coeffs = np.polyfit(xs, ys, degree)
    return np.poly1d(coeffs)


def solve_for_parameter(poly: np.poly1d, target: float, x_min: float, x_max: float, margin: float = 0.5):
    """
    Find x such that poly(x) = target by root-finding on poly(x) - target.
    Searches in [x_min - margin*range, x_max + margin*range].
    Returns the first root found, or None.
    """
    span = x_max - x_min if x_max != x_min else 1.0
    lo = x_min - margin * span
    hi = x_max + margin * span

    shifted = poly - target          # poly1d supports scalar subtraction
    # Sample to find a sign change
    xs_scan = np.linspace(lo, hi, 10_000)
    ys_scan = shifted(xs_scan)
    roots = []
    for j in range(len(xs_scan) - 1):
        if ys_scan[j] * ys_scan[j + 1] < 0:
            try:
                root = brentq(shifted, xs_scan[j], xs_scan[j + 1])
                roots.append(root)
            except ValueError:
                pass
    return roots[0] if roots else None


def tangent_line(poly: np.poly1d, x0: float):
    """Return slope and intercept of the tangent to poly at x0."""
    deriv = poly.deriv()
    slope = deriv(x0)
    intercept = poly(x0) - slope * x0
    return slope, intercept


## Plotting
def build_plot(pairs: list[tuple[float, float]],
               poly: np.poly1d,
               target_price: float,
               result_x: float | None) -> plt.Figure:

    xs_data = np.array([p[0] for p in pairs])
    ys_data = np.array([p[1] for p in pairs])
    x_min, x_max = xs_data.min(), xs_data.max()
    span = x_max - x_min if x_max != x_min else 1.0

    # Extended range for the curve ----------------------------------
    x_lo = x_min - 0.4 * span
    x_hi = x_max + 0.4 * span
    xs_curve = np.linspace(x_lo, x_hi, 600)
    ys_curve = poly(xs_curve)

    # Figure setup ----------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")
    for spine in ax.spines.values():
        spine.set_color("#3a3f55")
    ax.tick_params(colors="#9aa0bb", labelsize=9)
    ax.xaxis.label.set_color("#9aa0bb")
    ax.yaxis.label.set_color("#9aa0bb")
    ax.grid(color="#1e2235", linewidth=0.8, linestyle="--", alpha=0.7)

    # Polynomial curve ----------------------------------
    ax.plot(xs_curve, ys_curve,
            color="#4f9cf9", linewidth=2.2, label="Polynomial fit", zorder=3)

    # Scatter: input pairs ----------------------------------
    ax.scatter(xs_data, ys_data,
               marker="s", s=80, color="#4f9cf9", edgecolors="white",
               linewidths=0.8, zorder=5, label="Input pairs")

    if result_x is not None:
        # Result point ----------------------------------
        ax.scatter([result_x], [target_price],
                   marker="x", s=160, color="#ff4d6d", linewidths=2.5,
                   zorder=6, label=f"Result  x ≈ {result_x:.4f}")

        # Dashed guide lines to axes
        ax.axhline(target_price, color="#ff4d6d", linewidth=0.7,
                   linestyle=":", alpha=0.6)
        ax.axvline(result_x, color="#ff4d6d", linewidth=0.7,
                   linestyle=":", alpha=0.6)

        # Tangent line ----------------------------------
        slope, intercept = tangent_line(poly, result_x)
        t_half = 0.25 * (x_hi - x_lo)          # tangent visible width
        xs_tan = np.array([result_x - t_half, result_x + t_half])
        ys_tan = slope * xs_tan + intercept
        ax.plot(xs_tan, ys_tan, color="#ff9f43", linewidth=1.8, linestyle="--", label="Tangent", zorder=4)

    # Target price horizontal label ----------------------------------
    ax.axhline(target_price, color="#ff4d6d", linewidth=1.0,
               linestyle="-.", alpha=0.4)

    # Degree annotation ----------------------------------
    degree = len(pairs) - 1
    deg_label = ["", "linear", "quadratic", "cubic", "quartic"][degree] \
                if degree <= 4 else f"degree-{degree}"
    ax.text(0.02, 0.97, f"{deg_label.capitalize()} polynomial  (degree {degree})",
            transform=ax.transAxes, color="#9aa0bb", fontsize=8.5,
            va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#1e2235",
                      edgecolor="#3a3f55", alpha=0.8))

    # Labels & legend ----------------------------------
    ax.set_xlabel("Parameter", labelpad=8)
    ax.set_ylabel("Price", labelpad=8)
    ax.set_title("Price Approximator — Polynomial Interpolation",
                 color="white", fontsize=13, pad=14, fontweight="semibold")

    legend = ax.legend(facecolor="#1a1e2e", edgecolor="#3a3f55",
                       labelcolor="white", fontsize=9,
                       loc="upper left" if result_x is None or result_x < np.mean(xs_data)
                       else "upper right")

    plt.tight_layout()
    return fig


## Main

def main():
    print("\n╔══════════════════════════════════════╗")
    print("║       PRICE APPROXIMATOR v1.0.5      ║")
    print("╚══════════════════════════════════════╝")

    # Step 1 : collect data & fit polynomial ----------------------------------
    n = int(input("How many pairs to consider : "))
    pairs = get_pairs(n)
    poly = fit_polynomial(pairs)

    degree = len(pairs) - 1

    target_price = get_target_price()

    xs_data = [p[0] for p in pairs]
    result_x = solve_for_parameter(poly, target_price, x_min=min(xs_data), x_max=max(xs_data))

    if result_x is not None:
        print(f"\n For price = {target_price}")
        print(f"parameter ≈ {result_x:.6f}")
    else:
        print(f"\n No real solution found for price = {target_price} in the searched range.")

    # Step 2 : plot ----------------------------------
    fig = build_plot(pairs, poly, target_price, result_x)

    output_path = "price_approximation.png"
    fig.savefig(output_path, dpi=150, bbox_inches="tight",facecolor=fig.get_facecolor())
    print(f"\n  Plot saved → {output_path}")
    plt.show()


if __name__ == "__main__":
    main()
