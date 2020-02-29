import pyaudio
import wave
import os


class AudioListener(object):

    def __init__(self):
        self.CHUNK_SIZE = 1024
        # recorded_frames = []
        device_info = {}
        useloopback = False
        recordtime = 5
        export_directory = "outputs"
        self.p = pyaudio.PyAudio()

    def getListOfDevices(self):
        availableDevices = []

        for device_id in range(0, self.p.get_device_count()):
            device = {}

            info = p.get_device_info_by_index(device_id)
            device_info = p.get_device_info_by_index(device_id)

            device["index"] = info["index"]
            device["deviceName"] = info["name"]
            device["hostApi"] = p.get_host_api_info_by_index(info["hostApi"])["name"]
            device["loopback"] = False

            is_input = device_info["maxInputChannels"] > 0
            is_wasapi = (p.get_host_api_info_by_index(device_info["hostApi"])["name"]).find("WASAPI") != -1

            if is_input:
                print ("Selection is input using standard mode.\n")
                availableDevices.append(device)
            elif is_wasapi:
                device["loopback"] = True
                print ("Selection is output. Using loopback mode.\n")
                availableDevices.append(device)

        return availableDevices

    def startStream(self):
        stream = p.open(format = self.FORMAT,
                channels = self.CHANNEL_COUNT,
                rate = int(device_info["defaultSampleRate"]),
                input = True,
                frames_per_buffer = self.CHUNK_SIZE,
                input_device_index = device_info["index"],
                as_loopback = self.loopback_enabled)