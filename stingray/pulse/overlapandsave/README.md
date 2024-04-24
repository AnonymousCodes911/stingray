# Fast-convolution via overlap-save: a partial drop-in replacement for scipy.signal.fftconvolve

Original repo: https://github.com/fasiha/overlap_save-py

**Changelog**

*1.1.2* support for numpy<1.15 (where numpy.flip had more limited behavior)—thanks again Matteo!

*1.1.1* full complex support (thanks Matteo Bachetti! [!1](https://github.com/fasiha/overlap_save-py/pull/1) & [!2](https://github.com/fasiha/overlap_save-py/pull/2))

*1.1.0* PyFFTW and `mirror` mode added