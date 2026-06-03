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

    **Vertical ($d$).** Spot positions are read by eye against millimeter graph
    paper. Because the reading is an *interpolated judgment* on an analog scale —
    not a hard quantization (where the $/\sqrt{12}$ rectangular model would
    apply) — we assign the judged confidence directly as a standard uncertainty,
    $\sigma_d = 0.25$ mm (half a square either side of the spot center). Note the
    ODR rescales the covariance by the residual variance, so a uniform
    $\sigma_d$ cancels from the final $\sigma_f$; this choice only sets
    $\chi^2/\nu$ and the plotted bars.

    **Horizontal ($1/\lambda_{\text{px}}$).** $\lambda_{\text{px}}$ is set
    digitally, so the first-order *angle* is fixed exactly by $2\pi/\lambda_{\text{px}}$
    (pixelation only adds higher harmonics, it does not shift the fundamental).
    The horizontal error is therefore negligible; we assign it $\sim$1 ppm and
    use orthogonal-distance regression for a both-axes-correct treatment.

    **Systematic (pixel pitch $p$).** $p$ is not on either axis — it is the
    scale converting the dimensionless slope to a length, so its relative error
    propagates directly: $\sigma_f/f \supseteq \sigma_p/p$. This systematic
    dominates the final budget and is added in quadrature with the statistical
    slope error.
    """)
    return


@app.cell
def _imports():
    from pathlib import Path
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import openpyxl
    from taulab import odr_fit

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
    return Path, mo, np, odr_fit, openpyxl, plt


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
    READ_SIGMA = 0.25e-3 # by-eye spot-reading uncertainty, half a graph square [m]
    PITCH = 9.0e-6       # SLM pixel pitch (datasheet 9 µm) [m]
    PITCH_SYS = 0.23e-6  # pixel-pitch systematic (measured 9.44 ± 0.23 µm) [m]
    return LAMBDA, PITCH, PITCH_SYS, READ_SIGMA


@app.cell
def _load(DATA, np, openpyxl):
    """Load hand measurements from the spreadsheet."""
    _wb = openpyxl.load_workbook(DATA, data_only=True)
    _ws = _wb.active
    _rows = [r for r in _ws.iter_rows(min_row=2, values_only=True) if r[0] is not None]
    lpx = np.array([r[0] for r in _rows], dtype=float)
    d = np.array([r[2] for r in _rows], dtype=float)   # meters
    x = 1.0 / lpx
    return d, x


@app.cell
def _uncertainties(READ_SIGMA, d, np, x):
    # vertical: by-eye reading judgment taken directly as a standard uncertainty
    sy = READ_SIGMA * np.ones_like(d)
    # horizontal: lambda_px is software-exact -> negligible (~1 ppm)
    sx = 1e-6 * x
    return sx, sy


@app.cell
def _fit(LAMBDA, PITCH, PITCH_SYS, d, np, odr_fit, sx, sy, x):
    """ODR through the origin: d = m * (1/lambda_px); f = m p / lambda."""
    _proportional = lambda B, t: B[0] * t

    def _fit_one(_x, _sx, _d, _sy):
        _res = odr_fit(_proportional, [_d.mean() / _x.mean()], _x, _sx, _d, _sy,
                       param_names=["m"])
        _m, _sm = float(_res.params[0]), float(_res.errors[0])
        _f = _m * PITCH / LAMBDA
        _sf_stat = _sm * PITCH / LAMBDA
        _sf_sys = _f * (PITCH_SYS / PITCH) if PITCH > 0 else 0.0
        _sf_tot = float(np.hypot(_sf_stat, _sf_sys))
        return _f, _m, _res, _sf_stat, _sf_sys, _sf_tot, _sm

    f, m, res, sf_stat, sf_sys, sf_tot, sm = _fit_one(x, sx, d, sy)
    return f, m, res, sf_stat, sf_sys, sf_tot, sm


@app.cell
def _md_results(f, m, mo, res, sf_stat, sf_sys, sf_tot, sm):
    mo.md(rf"""
    ## Result

    **Hand measurements** (`data/fit.xlsx`):

    $$
    m = {m*1e3:.2f} \pm {sm*1e3:.2f}\ \text{{mm}}, \qquad
    \chi^2/\nu = {res.redchi:.2f}
    $$

    $$
    \boxed{{\,f = {f*100:.1f} \pm {sf_tot*100:.1f}\ \text{{cm}}\,}}
    $$

    Statistical (slope) uncertainty is $\pm{sf_stat*100:.2f}$ cm and pixel-pitch
    systematic $\pm{sf_sys*100:.2f}$ cm combined in quadrature. The central value
    remains reading-limited, while the systematic dominates the honest budget.
    """)
    return


@app.cell
def _plot(OUT_DIR, d, f, m, np, plt, res, sf_tot, sx, sy, x):
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
    ax.plot(_xf, m * _xf * 1e3, '-', color='#1f1f1f', lw=1.6,
            label='ODR fit')
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

    fig.savefig(OUT_DIR / "focal_length_fit.png", dpi=200)
    fig.savefig(OUT_DIR / "focal_length_fit.pdf")
    fig
    return


if __name__ == "__main__":
    app.run()
