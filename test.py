import librosa
import numpy
import matplotlib.pyplot as plt
import pdb
import webrtcvad
import time
# imprt vlc
import mir_eval
import IPython.display as ipd
import sounddevice as sd
import urllib
from pylab import *

def extract_max(pitches,magnitudes, shape):
    new_pitches = []
    new_magnitudes = []
    for i in range(0, shape[1]):
        new_pitches.append(numpy.max(pitches[:,i]))
        new_magnitudes.append(numpy.max(magnitudes[:,i]))
    return (new_pitches,new_magnitudes)

def smooth(x,window_len=11,window='hanning'):
        if window_len<3:
                return x
        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
                raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
        s=numpy.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
        if window == 'flat': #moving average
                w=numpy.ones(window_len,'d')
        else:
                w=eval('numpy.'+window+'(window_len)')
        y=numpy.convolve(w/w.sum(),s,mode='same')
        return y[window_len:-window_len+1]


file = './iron.mp3'
urllib.urlretrieve('http://audio.musicinformationretrieval.com/1_bar_funk_groove.mp3', 
                    filename='test.mp3')
duration = 350
y, sr = librosa.load(file)
#y1, sr1 = librosa.load('./1', sr=sample_f, duration=duration)

tempo, beat_frames = librosa.beat.beat_track(y, sr, start_bpm=60)
beat_times = librosa.frames_to_time(beat_frames)
clicks = mir_eval.sonify.clicks(beat_times, sr, length=len(y))

# while True:
# 	time.sleep(100)

pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)#, S=None, n_fft= n_fft, hop_length=hop_length, fmin=fmin, fmax=fmax, threshold=0.75)
shape = numpy.shape(pitches)
#nb_samples = total_samples / hop_length
nb_samples = shape[0]
#nb_windows = n_fft / 2
nb_windows = shape[1]
pitches, magnitudes = extract_max(pitches, magnitudes, shape)

pitches1 = smooth(pitches,window_len=10)
sd.play(clicks+y, sr) 
time.sleep(1)
i = 0
start = time.time()
while (abs(time.time() - start) < duration):
    x = time.time() - start
    if (i < len(beat_times) and abs(x - beat_times[i]) < 0.00001):
        # print x 
        # print beat_times[i] 
        print "bam"
        i += 1

# plt.plot(magnitudes)
# plt.show()
# pdb.set_trace()