import numpy as np
import pylab
import matplotlib.pyplot as plt
from scipy.io import wavfile
import time
import sys
import seaborn as sns

import pyaudio
import wave
import os

CHUNK_SIZE = 1024
recorded_frames = []
device_info = {}
useloopback = False
recordtime = 5
export_directory = "outputs"
#Use module
p = pyaudio.PyAudio()

#Set default to first in list or ask Windows
try:
    default_device_index = p.get_default_input_device_info()
except IOError:
    default_device_index = -1

#Select Device
print("Available devices:")
for i in range(0, p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print (str(info["index"]) + ": \t %s \n \t %s \n" % (info["name"], p.get_host_api_info_by_index(info["hostApi"])["name"]))

    if default_device_index == -1:
        default_device_index = info["index"]

#Handle no devices available
if default_device_index == -1:
    print ("No device available. Quitting.")
    exit()


#Get input or default
device_id = int(input("Choose device [" + str(default_device_index) + "]: ") or default_device_index)
print ("")

#Get device info
try:
    device_info = p.get_device_info_by_index(device_id)
except IOError:
    device_info = p.get_device_info_by_index(default_device_index)
    print ("Selection not available, using default.")

#Choose between loopback or standard mode
is_input = device_info["maxInputChannels"] > 0
is_wasapi = (p.get_host_api_info_by_index(device_info["hostApi"])["name"]).find("WASAPI") != -1
if is_input:
    print ("Selection is input using standard mode.\n")
else:
    if is_wasapi:
        useloopback = True;
        print ("Selection is output. Using loopback mode.\n")
    else:
        print ("Selection is input and does not support loopback mode. Quitting.\n")
        exit()

# recordtime = int(input("Record time in seconds [" + str(recordtime) + "]: ") or recordtime)

#Open stream
channelcount = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
stream = p.open(format = pyaudio.paInt16,
                channels = channelcount,
                rate = int(device_info["defaultSampleRate"]),
                input = True,
                frames_per_buffer = CHUNK_SIZE,
                input_device_index = device_info["index"],
                as_loopback = useloopback)

#Start Recording
print ("Starting...")

#--------------------------------------------------------------------------------------------------------------

i=0
f,ax = plt.subplots(2)

# Prepare the Plotting Environment with random starting values
x = np.arange(10000)
y = np.random.randn(10000)

# Plot 0 is for raw audio data
li, = ax[0].plot(x, y)
ax[0].set_xlim(0,1000)
ax[0].set_ylim(-5000,5000)
ax[0].set_title("Raw Audio Signal")
# Plot 1 is for the FFT of the audio
li2, = ax[1].plot(x, y)
ax[1].set_xlim(0,5000)
ax[1].set_ylim(-100,100)
ax[1].set_title("Fast Fourier Transform")
# Show the plot, but without blocking updates
plt.pause(0.01)
plt.tight_layout()

global keep_going
keep_going = True

def plot_data(in_data):
    # get and convert the data to float
    audio_data = np.fromstring(in_data, np.int16)
    # Fast Fourier Transform, 10*log10(abs) is to scale it to dB
    # and make sure it's not imaginary
    dfft = 10.*np.log10(abs(np.fft.rfft(audio_data)))

    # Force the new data into the plot, but without redrawing axes.
    # If uses plt.draw(), axes are re-drawn every time
    #print audio_data[0:10]
    #print dfft[0:10]
    #print
    li.set_xdata(np.arange(len(audio_data)))
    li.set_ydata(audio_data)
    li2.set_xdata(np.arange(len(dfft))*10.)
    li2.set_ydata(dfft)

    # Show the updated plot, but without blocking
    plt.pause(0.01)
    if keep_going:
        return True
    else:
        return False

# Open the connection and start streaming the data
stream.start_stream()

# Loop so program doesn't end while the stream callback's
# itself for new data
while keep_going:
    try:
        plot_data(stream.read(CHUNK_SIZE))
    except KeyboardInterrupt:
        keep_going=False
    except:
        pass

# Close up shop (currently not used because KeyboardInterrupt
# is the only way to close)
stream.stop_stream()
stream.close()

p.terminate()

#--------------------------------------------------------------------------------------------------------------

# for i in range(0, int(int(device_info["defaultSampleRate"]) / CHUNK_SIZE * recordtime)):
#     recorded_frames.append(stream.read(CHUNK_SIZE))
#     print (".")

# print ("End.")
# #Stop Recording

# stream.stop_stream()
# stream.close()

# #Close module
# p.terminate()

# filename = "out.wav"

# file = os.path.join(export_directory, filename)

# waveFile = wave.open(file, 'wb')
# waveFile.setnchannels(channelcount)
# waveFile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
# waveFile.setframerate(int(device_info["defaultSampleRate"]))
# waveFile.writeframes(b''.join(recorded_frames))
# waveFile.close()