---
authors:
  - ptuemmler
categories:
  - Mathematics
  - Numerics
tags:
  - Code
  - Fourier Transform
date: 2025-07-04
hide:
  - toc
draft: true
---
# Fast Fourier Transforms 

The [Fast Fourier Transform (FFT)](https://en.wikipedia.org/wiki/Fast_Fourier_transform) is an efficient algorithm to compute the Discrete Fourier Transform (DFT) and its inverse. It is widely used in signal processing, image analysis, and solving partial differential equations. A typical issue is the physically correct scaling and calculation of respective axes.
A common problem is the scaling of the axes, which can lead to confusion when interpreting the results. This app provides a simple interface to visualize the FFT and its inverse, allowing you to explore the effects of different parameters on the resulting spectra.
<!-- more -->
The simplest case of the FFT is the transformation of a 1D signal, which can be extended to 2D signals (e.g. images) and higher dimensions. The app allows you to visualize the FFT of a 1D signal and its inverse, as well as the scaling of the axes.
For the 1D case, we can use the following python and matlab code snippets to compute the FFT and its inverse with the correct scaling and also return the respective axes if desired:

=== "python"

    ``` python title="fft.py" linenums="1"
    from numpy import fft

    def fft_1d(axis, signal, return_axes=False):
        """
        Compute the 1D FFT of a signal and return the transformed signal and axes.
        
        Parameters
        ----------
        axis : 1D array-like
            The axis of the signal.
        signal : 1D array-like
            The signal to be transformed.
        return_axes : bool, optional
            If True, return the transformed axes and signal. Default is False.
        
        Returns
        -------
        tuple
            If return_axes is True, return a tuple of the transformed axes and signal.
            Otherwise, return only the transformed signal.
        """
        transformed_signal = fft.fft(signal)
        if return_axes:
            transformed_axis = fft.fftfreq(len(axis), axis[1] - axis[0])
            return transformed_axis, transformed_signal
        else:
            return transformed_signal

    def ifft_1d(axis, transformed_signal, return_axes=False):
        """
        Compute the inverse 1D FFT of a transformed signal and return the original signal and axes.
        
        Parameters
        ----------
        axis : 1D array-like
            The axis of the transformed signal.
        transformed_signal : 1D array-like
            The transformed signal to be inverted.
        return_axes : bool, optional
            If True, return the original axes and signal. Default is False.
        
        Returns
        -------
        tuple
            If return_axes is True, return a tuple of the original axes and signal.
            Otherwise, return only the original signal.
        """
        original_signal = fft.ifft(transformed_signal)
        if return_axes:
            original_axis = fft.fftfreq(len(axis), axis[1] - axis[0])
            return original_axis, original_signal
        else:
            return original_signal
    ```

=== "matlab"

    ``` matlab
    
    ```

{{embed_app("100%", "500px", "1d")}}
{{embed_app("100%", "500px", "2d")}}
