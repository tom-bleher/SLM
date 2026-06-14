# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "numpy",
#     "openpyxl",
#     "matplotlib",
#     "taulab",
# ]
# ///

import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium")


@app.cell
def _md_intro(mo):
    mo.md(r"""
    # SLM — Focal length of $L_1$ from the Fourier plane

    A lens performs a spatial Fourier transform in its back focal plane. A
    cosine grating $\cos(k x)$ written on the SLM transforms to a symmetric pair
    of first-order spots (the two $\delta$-functions). A pure spatial frequency
    $k$ leaves the SLM at angle $\theta = \lambda_{\text{laser}}k/2\pi$, and the
    lens maps that angle to a position in the focal plane:

    $$
    d = f\,\theta = \frac{\lambda_{\text{laser}}\,f}{2\pi}\,k
      = \frac{\lambda_{\text{laser}}\,f}{p}\cdot\frac{1}{\lambda_{\text{px}}},
    $$

    using $k = 2\pi/\lambda_{\text{px}}$ (period in pixels) and the SLM pixel
    pitch $p$. Plotting the measured spot displacement $d$ against
    $x = 1/\lambda_{\text{px}}$ gives a line through the origin with slope

    $$
    m = \frac{\lambda_{\text{laser}}\,f}{p}
    \qquad\Longrightarrow\qquad
    f = \frac{m\,p}{\lambda_{\text{laser}}}.
    $$

    ### Uncertainties

    **Vertical ($d$).** Spot positions are read against millimeter graph paper.
    Treating the 1 mm scale resolution as a rectangular distribution gives the
    standard uncertainty $\sigma_d = 1\text{ mm}/\sqrt{12}$. Note the
    ODR rescales the covariance by the residual variance, so a uniform
    $\sigma_d$ cancels from the final $\sigma_f$; this choice only sets
    $\chi^2/\nu$ and the plotted bars.

    **Horizontal ($1/\lambda_{\text{px}}$).** $\lambda_{\text{px}}$ is set
    digitally, so the first-order *angle* is fixed exactly by $2\pi/\lambda_{\text{px}}$
    (pixelation only adds higher harmonics, it does not shift the fundamental).
    The horizontal error is therefore negligible; we assign it $\sim$1 ppm and
    use orthogonal-distance regression for a both-axes-correct treatment.

    **Pixel pitch ($p$).** We use the course-guide specification
    $p=9.00\,\mu\text{m}$. Since the guide does not provide an uncertainty for
    this value, no pixel-pitch systematic is included in the uncertainty budget.
    """)
    return


@app.cell
def _imports():
    from pathlib import Path
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import openpyxl
    from taulab import fit_functions, odr_fit

    plt.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 12.5,
        "axes.titleweight": "regular",
        "axes.labelsize": 10,
        "legend.fontsize": 8.5,
        "mathtext.fontset": "cm",
        "axes.linewidth": 0.8,
        "axes.edgecolor": "#444444",
        "xtick.color": "#444444",
        "ytick.color": "#444444",
        "xtick.labelcolor": "black",
        "ytick.labelcolor": "black",
        "axes.labelcolor": "black",
        "text.color": "black",
        "savefig.dpi": 200,
        "figure.facecolor": "white",
    })
    return Path, fit_functions, mo, np, odr_fit, openpyxl, plt


@app.cell
def _paths(Path):
    ROOT = Path(__file__).resolve().parent
    DATA = ROOT / "data" / "fit.xlsx"
    OUT_DIR = ROOT / "results"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return DATA, OUT_DIR


@app.cell
def _constants():
    LAMBDA = 633e-9      # diode laser, 633 nm (per lab guide) [m]
    READ_SIGMA = 1e-3 / (12 ** 0.5)  # 1 mm scale resolution / sqrt(12) [m]
    PITCH = 9.0e-6       # SLM pixel pitch (datasheet 9 µm) [m]
    PITCH_SYS = 0.0      # no pitch uncertainty is specified in the course guide
    return LAMBDA, PITCH, PITCH_SYS, READ_SIGMA


@app.cell
def _load(DATA, np, openpyxl):
    """Load hand measurements from the spreadsheet."""
    _wb = openpyxl.load_workbook(DATA, data_only=True)
    _ws = _wb.active
    _all_rows = list(_ws.iter_rows(values_only=True))
    _headers = {str(value).strip(): index for index, value in enumerate(_all_rows[0])}
    _lpx_col = _headers["λ_px"]
    _squares_col = _headers["squares_new"]
    _d_col = _headers["d_new (m)"]
    _rows = [
        row for row in _all_rows[1:]
        if row[_lpx_col] is not None
        and row[_squares_col] is not None
        and row[_d_col] is not None
    ]
    lpx = np.array([row[_lpx_col] for row in _rows], dtype=float)
    # squares_new is the directly edited graph-paper measurement in millimeters.
    # Derive d from it so stale values in the duplicate d_new column cannot mask edits.
    d = np.array([row[_squares_col] for row in _rows], dtype=float) * 1e-3
    x = 1.0 / lpx
    return d, x


@app.cell
def _uncertainties(READ_SIGMA, d, np, x):
    # vertical: 1 mm scale resolution with a rectangular distribution
    sy = READ_SIGMA * np.ones_like(d)
    # horizontal: lambda_px is software-exact -> negligible (~1 ppm)
    sx = 1e-6 * x
    return sx, sy


@app.cell
def _fit(LAMBDA, PITCH, PITCH_SYS, d, fit_functions, np, odr_fit, sx, sy, x):
    """TauLab linear ODR: d = b + m / lambda_px; f = m p / lambda."""
    def _fit_one(_x, _sx, _d, _sy):
        _res = odr_fit(fit_functions.linear, None, _x, _sx, _d, _sy,
                       param_names=["intercept", "slope"])
        _b, _m = map(float, _res.params)
        _sb, _sm = map(float, _res.errors)
        _f = _m * PITCH / LAMBDA
        _sf_stat = _sm * PITCH / LAMBDA
        _sf_sys = _f * (PITCH_SYS / PITCH) if PITCH > 0 else 0.0
        _sf_tot = float(np.hypot(_sf_stat, _sf_sys))
        return _b, _f, _m, _res, _sb, _sf_stat, _sf_sys, _sf_tot, _sm

    b, f, m, res, sb, sf_stat, sf_sys, sf_tot, sm = _fit_one(x, sx, d, sy)
    return b, f, m, res, sb, sf_stat, sf_sys, sf_tot, sm


@app.cell
def _md_results(b, f, m, mo, res, sb, sf_tot, sm):
    mo.md(rf"""
    ## Result

    **New hand measurements** (`squares_new` and `d_new (m)` in `data/fit.xlsx`):

    | Result | Fit |
    |---|---:|
    | $b$ [mm] | ${b*1e3:.2f} \pm {sb*1e3:.2f}$ |
    | $m$ [mm] | ${m*1e3:.2f} \pm {sm*1e3:.2f}$ ({sm/m*100:.2f}%) |
    | $f$ [cm] | ${f*100:.1f} \pm {sf_tot*100:.1f}$ ({sf_tot/f*100:.1f}%) |
    | $\chi^2_{{\mathrm{{red}}}}$ | {res.redchi:.3f} |
    | $p_{{\mathrm{{val}}}}$ | {res.p_value:.3f} |

    The focal-length uncertainty is statistical and comes from the fitted slope.
    """)
    return


@app.cell
def _plot(OUT_DIR, b, d, f, m, np, plt, res, sf_tot, sx, sy, x):
    fig, ax = plt.subplots(figsize=(6.4, 4.2), constrained_layout=True)
    ax.errorbar(
        x,
        d * 1e3,
        xerr=sx,
        yerr=sy * 1e3,
        fmt='o',
        ms=6,
        capsize=3,
        color='#c1272d',
        label=fr'hand table: $f={f*100:.1f}$ cm',
        zorder=3,
    )
    _xf = np.linspace(0, x.max() * 1.05, 100)
    ax.plot(_xf, (b + m * _xf) * 1e3, '-', color='#1f1f1f', lw=1.6,
            label='TauLab linear ODR fit')
    ax.set_xlabel(r'$1/\lambda_{px}$  [pixel$^{-1}$]')
    ax.set_ylabel(r"$d$  [mm]")
    ax.set_title(
        fr'SLM focal-length fit: new $f = {f*100:.1f} \pm {sf_tot*100:.1f}\,$cm'
        fr'  ($\chi^2/\nu = {res.redchi:.2f}$)',
        fontsize=11,
    )
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    fig.savefig(OUT_DIR / "focal_length_fit.png", dpi=400)
    fig
    return


if __name__ == "__main__":
    app.run()
