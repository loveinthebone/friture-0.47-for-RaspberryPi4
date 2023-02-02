=======
Friture
=======

.. image:: https://github.com/tlecomte/friture/workflows/build/badge.svg
    :target: https://github.com/tlecomte/friture/actions

**Friture** is an application to visualize and analyze live audio data in real-time.

Friture displays audio data in several widgets, such as a scope, a spectrum analyzer, or a rolling 2D spectrogram.

This program can be useful to analyze and equalize the audio response of a hall, or for educational purposes, etc.

The name *Friture* is a french word for *frying*, also used for *noise* in a sound.

See the `project homepage`_ for screenshots and more information.

.. _`project homepage`: http://friture.org

With this branch of Friture, customized by International Audio Holding, we added following features to friture:

1. Compatibility with Raspberry PI 4. This branch can be installed in Raspberry PI 4, which has ARMv6 CPU architecture.

2. Added a new panel called "Scope_IAH". It is used to plot the FFT amplitudes at two user specified frewquencies. Such a feature is useful for crosstalk analysis.

3. The "Sine" wave generator is modified so that the user can adjust the frequencies of the two sine waves at the left and right output channels seperately. So the left and right channels can play two different tones. Such a feature is also used in crosstalk analysis.
