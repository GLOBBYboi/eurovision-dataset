import os
import json
import librosa
import numpy as np
import scipy.stats
from glob import glob

def detailed_stats(feature_array):
    feature_array = np.array(feature_array).flatten()
    return {
        'mean': float(np.mean(feature_array)),
        'variance': float(np.var(feature_array)),
        'median': float(np.median(feature_array)),
        'skewness': float(scipy.stats.skew(feature_array)),
        'kurtosis': float(scipy.stats.kurtosis(feature_array)),
        'min': float(np.min(feature_array)),
        'max': float(np.max(feature_array))
    }

def extract_audio_features(audio_path):
    y, sr = librosa.load(audio_path)
    
    # Basic features
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
    rms = librosa.feature.rms(y=y)

    # Key estimation (basic approximation)
    chroma_cens = librosa.feature.chroma_cens(y=y, sr=sr)
    chroma_mean = chroma_cens.mean(axis=1)
    key_index = chroma_mean.argmax()
    key_labels = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key = key_labels[key_index]

    # Danceability approximation (fix scalar conversion)
    beat_strength = float(np.mean(rms[0, beat_frames]))
    danceability_raw = (tempo / 200) * beat_strength * 10
    danceability = float(np.clip(danceability_raw, 0, 1))

    features = {
        'tempo': float(tempo),
        'danceability': danceability,
        'key': key,
        'duration': float(librosa.get_duration(y=y, sr=sr)),
        'chroma_stft_stats': detailed_stats(chroma),
        'spectral_centroid_stats': detailed_stats(spectral_centroid),
        'zero_crossing_rate_stats': detailed_stats(zero_crossing_rate),
        'rms_stats': detailed_stats(rms),
        'mfcc_stats': [detailed_stats(mfcc_band) for mfcc_band in mfcc],
        'spectral_contrast_stats': [detailed_stats(contrast_band) for contrast_band in spectral_contrast],
        'tonnetz_stats': [detailed_stats(tonnetz_band) for tonnetz_band in tonnetz]
    }

    return features

# Process audio files
#files = []
#for year in range(2013, 2024):
#    files.extend(glob(f'audio/{year}/*.mp3', recursive=True))

files = glob('audio/**/*.mp3', recursive=True)

for f in files:
    output_path = os.path.splitext(f)[0] + '.json'
    print(output_path)

    if not os.path.exists(output_path):
        print('Extracting audio features from {}'.format(f))
        features = extract_audio_features(f)
        
        with open(output_path, 'w') as fp:
            json.dump(features, fp, indent=4)
