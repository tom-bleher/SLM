# SLM — Fourier Optics Lab

Spatial Light Modulator (SLM) experiments demonstrating the Fourier-transforming
property of a lens. A grating written on the SLM is imaged in the back focal
plane of a lens, where its spatial Fourier transform appears as a set of spots.

## Week 1

A 2f system places the Fourier plane at the focal point of a lens. We verify the
**linearity** and **convolution** properties of the Fourier transform using cosine
gratings, and measure the **focal length** of the lens from the displacement of
the first-order spots versus spatial frequency.

A cosine grating $\cos(kx)$ on the SLM produces a symmetric pair of first-order
spots. A spatial frequency $k = 2\pi/\lambda_{px}$ leaves the SLM at angle
$\theta = \lambda_\text{laser}\,k/2\pi$, mapped by the lens to a focal-plane
position $d = f\theta$. Plotting $d$ against $1/\lambda_{px}$ gives a line through
the origin with slope $m = \lambda_\text{laser} f / p$, so $f = m p / \lambda_\text{laser}$.

### Contents

- `week1/FourierOptics.py` — generates SLM display patterns (cosine gratings,
  Gaussian, convolution/linearity demos) and their FFTs; drives the SLM screen.
- `week1/fit.py` — [marimo](https://marimo.io) notebook: ODR fit of focal-plane
  spot displacement vs. spatial frequency to extract the lens focal length, with
  a full statistical + systematic (pixel-pitch) uncertainty treatment.
- `week1/notebook.md` / `notebook.pdf` — lab notebook write-up.
- `week1/data/` — hand-measured spot positions (`fit.xlsx`) and raw photos.
- `week1/media/` — photos of the projected Fourier spots.
- `week1/results/` — generated focal-length fit plot.

> Reference textbook PDFs and the course lab guide are kept local only (excluded
> via `.gitignore`) for copyright reasons.

## Running

The fit notebook is a self-contained [uv](https://docs.astral.sh/uv/) script:

```sh
uv run week1/fit.py        # run as a script
marimo edit week1/fit.py   # or open interactively
```
