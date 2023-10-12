import os
import pathlib

import matplotlib.pyplot as plt

import numpy as np

import tensorflow as tf

from scipy.io import wavfile
def get_spectrogram(waveform):
  # Convert the waveform to a spectrogram via a STFT.
  spectrogram = tf.signal.stft(
      waveform, frame_length=255, frame_step=128)
  # Obtain the magnitude of the STFT.
  spectrogram = tf.abs(spectrogram)
  # Add a `channels` dimension, so that the spectrogram can be used
  # as image-like input data with convolution layers (which expect
  # shape (`batch_size`, `height`, `width`, `channels`).
  spectrogram = spectrogram[..., tf.newaxis]
  return spectrogram


def plot_spectrogram(spectrogram, ax):
  if len(spectrogram.shape) > 2:
    assert len(spectrogram.shape) == 3
    spectrogram = np.squeeze(spectrogram, axis=-1)
  # Convert the frequencies to log scale and transpose, so that the time is
  # represented on the x-axis (columns).
  # Add an epsilon to avoid taking a log of zero.
  log_spec = np.log(spectrogram.T + np.finfo(float).eps)
  height = log_spec.shape[0]
  width = log_spec.shape[1]
  X = np.linspace(0, np.size(spectrogram), num=width, dtype=int)
  Y = range(height)
  ax.pcolormesh(X, Y, log_spec)

def spectrogram_to_waveform(spectrogram):
    # Remove the channel dimension.
    spectrogram = tf.squeeze(spectrogram, axis=-1)
    
    # Inverse STFT. This will give complex values.
    waveform = tf.signal.inverse_stft(
        spectrogram, frame_length=255, frame_step=128, window_fn=tf.signal.inverse_stft_window_fn(128)
    )
    
    # Since we used the magnitude (tf.abs) to get the spectrogram,
    # the phase information was lost. Therefore, the reconstructed
    # waveform from the inverse STFT might not be exactly the same
    # as the original, but it should be a close approximation.

    return waveform


def save_waveform_to_wav(waveform, filename, sample_rate=44100):
    # Ensure waveform is a NumPy array and scale to int16.
    waveform = (waveform * 32767 / max(0.01, np.max(np.abs(waveform)))).astype(np.int16)

    # Save to WAV file.
    wavfile.write(filename, sample_rate, waveform)

audio_path = str(pathlib.Path().absolute()) + "/Basic_Audio_Processing/sample_wav_tunes/"

audio_files = os.listdir(audio_path)

sample_rate, data = wavfile.read(audio_path + str(audio_files[0]))
waveform = data[:, 0]


spectrogram = get_spectrogram(waveform)

fig, axes = plt.subplots(2, figsize=(12, 8))
timescale = np.arange(waveform.shape[0])
axes[0].plot(timescale, waveform)
axes[0].set_title('Waveform')
axes[0].set_xlim([0, 1000000])

plot_spectrogram(spectrogram, axes[1])
axes[1].set_title('Spectrogram')
plt.show()

waveform_from_spec = np.array(spectrogram_to_waveform(spectrogram).numpy())
save_waveform_to_wav(waveform_from_spec, "fullyTransformed.wav")