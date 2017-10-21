#!/usr/bin/env ipython

# Authors: martijn.millecamp@student.kuleuven.be [Martijn Millecamp] & miro.masat@gmail.com [Miroslav Masat]

import librosa
import numpy
import matplotlib.pyplot as plt
import pdb
import webrtcvad
import time
import vlc
import mir_eval
import IPython.display as ipd
import sounddevice as sd
import urllib

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

def plot(vector, name, xlabel=None, ylabel=None):
    plt.figure()
    plt.plot(vector)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.plot()
    # plt.savefig(name)

def set_variables(sample_f,duration,window_time,fmin,fmax,overlap):
    total_samples = sample_f * duration
    #There are sample_f/1000 samples / ms
    #windowsize = number of samples in one window
    window_size = sample_f/1000 * window_time
    hop_length = total_samples / window_size
    #Calculate number of windows needed
    needed_nb_windows = total_samples / (window_size - overlap)
    n_fft = needed_nb_windows * 2.0
    return total_samples, window_size, needed_nb_windows, n_fft, hop_length

def analyse(y,sr,n_fft,hop_length,fmin,fmax):
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr, S=None, n_fft= n_fft, hop_length=hop_length, fmin=fmin, fmax=fmax, threshold=0.75)

    tempo, beat_frames = librosa.beat.beat_track(y, sr, start_bpm=40)
    beat_samples = librosa.frames_to_samples(beat_frames)

    shape = numpy.shape(pitches)
    #nb_samples = total_samples / hop_length
    nb_samples = shape[0]
    #nb_windows = n_fft / 2
    nb_windows = shape[1]
    pitches,magnitudes = extract_max(pitches, magnitudes, shape)

    pitches1 = smooth(pitches,window_len=10)
    pitches2 = smooth(pitches,window_len=20)
    pitches3 = smooth(pitches,window_len=30)
    pitches4 = smooth(pitches,window_len=40)

    # vad = webrtcvad.Vad()
    # frame_duration = 20  # ms
    # frame = b'\x00\x00' * (sr * frame_duration / 1000)
    # print 'Contains speech: %s' % (vad.is_speech(frame, sr))

    # pdb.set_trace()
    # plt.ion()
    # start = time.time()
    # x = numpy.arange(0, duration, duration/len(pitches1))
    # plt.plot(pitches1)
    # pdb.set_trace()
    # for i in range(len(pitches1)):
    #     plt.scatter(i, pitches1[i])
    #     # plt.pause(0.000001)
    # print "elapsed", time.time() - start

    # pdb.set_trace()
    # plot(pitches1, 'pitches1')
    # plot(pitches2, 'pitches2')
    # plot(pitches3, 'pitches3')
    # plot(pitches4, 'pitches4')
    # plot(magnitudes, 'magnitudes')
    # plot( y, 'audio')
    # plt.vlines(beat_samples, -1, 1, color='r')
    # plt.show()

    return pitches4, beat_frames, tempo

def main():

    file = './iron.mp3'
    urllib.urlretrieve('http://audio.musicinformationretrieval.com/1_bar_funk_groove.mp3', 
                    filename='test.mp3')
    #Set all wanted variables

    #we want a sample frequency of 16 000
    sample_f = 16000
    #The duration of the voice sample
    global duration
    duration = 10
    #We want a windowsize of 30 ms
    window_time = 60
    fmin = 80
    fmax = 250
    #We want an overlap of 10 ms
    overlap = 20
    total_samples, window_size, needed_nb_windows, n_fft, hop_length = set_variables(sample_f, duration, window_time, fmin, fmax, overlap)


    # y = audio time series
    # sr = sampling rate of y
    y, sr = librosa.load(file)
    #y1, sr1 = librosa.load('./1', sr=sample_f, duration=duration)

    tempo, beat_frames = librosa.beat.beat_track(y, sr, start_bpm=60)
    beat_times = librosa.frames_to_time(beat_frames)
    clicks = mir_eval.sonify.clicks(beat_times, sr, length=len(y))
    sd.play(clicks+y, sr)


    pitch, beat, tempo = analyse(y, sr, n_fft, hop_length, fmin, fmax)

    tempo, beat_frames = librosa.beat.beat_track(y, sr)
    beat_times = librosa.frames_to_time(beat_frames)
    clicks = mir_eval.sonify.clicks(beat_times, sr, length=len(y))
    sd.play(clicks+y, sr)

    beats = ipd.Audio(y+clicks, rate=sr)
    pdb.set_trace()

    # song = vlc.MediaPlayer(file)
    # # ipdb.set_trace()
    # beat = vlc.MediaPlayer(beats)
    # song.play()
    # beat.play()

    # i = 0
    # time.sleep(1.2)
    # start = time.time()
    # # pdb.set_trace()
    
    # while (abs(time.time() - start) < duration):
    #     x = time.time() - start
    #     if (i < len(beat_times) and abs(x - beat_times[i]) < 0.00001):
    #         # print x 
    #         # print beat_times[i] 
    #         print "bam"
    #         i += 1





if __name__ == "__main__":
    main()
