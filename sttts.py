import keyboard
import pyaudio
import wave
import os
import tempfile
import speech_recognition
import pyttsx3
from time import sleep
from threading import Thread, Event
from getpass import getpass

os.system("title "+"ST3S by Field")

filename = "recorded.wav"
chunk = 1024
FORMAT = pyaudio.paInt16
channels = 1
sample_rate = 44100
p = pyaudio.PyAudio()
frames = []
recording_key_pressed = False
recognizer = speech_recognition.Recognizer()
indeviceid = 0
outdeviceid = 0
recordkey = ""
engine = pyttsx3.init()
voices = engine.getProperty('voices')

class ReusableThread(Thread):
    """
    This class provides code for a restartale / reusable thread

    join() will only wait for one (target)functioncall to finish
    finish() will finish the whole thread (after that, it's not restartable anymore)
        
    """

    def __init__(self, target):
        self._startSignal = Event()
        self._oneRunFinished = Event()
        self._finishIndicator = False
        self._callable = target

        Thread.__init__(self)

    def restart(self):
        """make sure to always call join() before restarting"""
        self._startSignal.set()

    def run(self):
        """ This class will reprocess the object "processObject" forever.
        Through the change of data inside processObject and start signals
        we can reuse the thread's resources"""

        self.restart()
        while(True):    
            # wait until we should process
            self._startSignal.wait()

            self._startSignal.clear()

            if(self._finishIndicator):# check, if we want to stop
                self._oneRunFinished.set()
                return
            
            # call the threaded function
            self._callable()

            # notify about the run's end
            self._oneRunFinished.set()

    def join(self):
        """ This join will only wait for one single run (target functioncall) to be finished"""
        self._oneRunFinished.wait()
        self._oneRunFinished.clear()

    def finish(self):
        self._finishIndicator = True
        self.restart()
        self.join()

def recordloop():
#Main recording function
    global frames
    stream = p.open(format=FORMAT,
        channels=channels,
        rate=sample_rate,
        input=True,
        output=True,
        input_device_index=indeviceid,
        output_device_index=outdeviceid,
        frames_per_buffer=chunk)

    #Start of recording loop
    print("RECORDING STARTED")
    while recording_key_pressed:
        data = stream.read(chunk)
        frames.append(data)

    #Recording stopped and saved to wav file
    stream.stop_stream()
    stream.close()
    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(sample_rate)
    wf.writeframes(b"".join(frames))
    wf.close()
    print("RECORDING ENDED")
    
        
def main():
    global recording_key_pressed
    global frames
    global indeviceid
    global outdeviceid
    global recordkey
    recordthread = ReusableThread(target=recordloop)
    firststart = True
    voicerate = 200
    voiceid = 1

    print("\n=====  SPEECH TO TEXT TO SPEECH  ======")
    print("      Press Enter to initialize")
    try:
        input()
    except KeyboardInterrupt:
        exit()
    while True:
        reset = 0
        #Selecting hotkey to be used for recording
        print("\n=============   HOTKEY   ==============")
        print("Select your preferred recording key:")
        recordkey = keyboard.read_key()
        print(recordkey,"selected. Press Enter to continue...")
        try:
            getpass("")
        except KeyboardInterrupt:
            sleep(1)
            continue

        #Selecting voice properties
        print("\n=============   VOICES   ==============")
        i = 0
        voices = engine.getProperty('voices')
        for voice in voices:
            print("Voice id ", i, " - ", voice.name)
            i+=1
        while True:
            try:
                voiceid = int(input('Select Voice ID: '))
            except ValueError: 
                print('Not a numerical value')
                continue
            except KeyboardInterrupt:
                sleep(1)
                reset = True
                break
            if voiceid >= i:
                print('ID Not in range')
            else:
                break
        if reset == True:
            continue
        engine.setProperty('voice', voices[voiceid].id)

        print("\n===============   RATE   ==============")
        while True:
            try:
                voicerate = int(input('Select Voice Rate in Words Per Min (Default 150): '))
            except ValueError: 
                print('Not a numerical value')
                continue
            except KeyboardInterrupt:
                sleep(1)
                reset = True
                break
            else:
                break
        if reset == True:
            continue
        engine.setProperty('rate', voicerate)

        #Selecting I/O audio devices
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        print("\n==========   INPUT DEVICES   ==========")
        for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
        while True:
            try:
                indeviceid = int(input('Select Input Device ID: '))
            except ValueError: 
                print('Not a numerical value')
                continue
            except KeyboardInterrupt:
                sleep(1)
                reset = True
                break
            if indeviceid > numdevices:
                print('ID Not in range')
            else:
                break
        if reset == True:
            continue

        print("\n==========   OUTPUT DEVICES  ==========")
        for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) < 1:
                    print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

        while True:
            try:
                outdeviceid = int(input('Select Output Device ID: '))
            except ValueError: 
                print('Not a numerical value')
                continue
            except KeyboardInterrupt:
                sleep(1)
                reset = True
                break
            if outdeviceid > numdevices:
                print('ID Not in range')
            else:
                break
        if reset == True:
            continue

        print("\n========   HOLD KEY TO RECORD  ========")
        print("         or press Ctrl+C to reset       ")
        #Creating and working in temp dir
        try:
            os.mkdir(tempfile.gettempdir()+"\speech2txt2speech")
        except:
            pass
        os.chdir(tempfile.gettempdir()+"\speech2txt2speech")

        #Main keyboard detection loop
        while True:
            try:
                if keyboard.is_pressed(recordkey):

                    #Case when recording key is pressed down
                    if recording_key_pressed == False:
                        if os.path.isfile(filename):
                            os.remove(filename)
                        frames = []
                        recording_key_pressed = True
                        if firststart:
                            recordthread.start()
                            firststart = False
                        else:
                            recordthread.restart()

                    #Case when recording key is currently held down
                    else:
                        print("...")
                #Case when recording key is released
                elif recording_key_pressed == True:
                    recording_key_pressed = False
                    recordthread.join()
                    recordedaudio = speech_recognition.AudioFile(filename)
                    with recordedaudio as source:
                        audiofile = recognizer.record(source)
                    try:
                        speech_text = str(recognizer.recognize_google(audiofile))
                    except:
                        print("SPEECH RECOGNITION FAILED, TRY AGAIN.")
                        continue
                    print("TRANSCRIPT:",speech_text)
                    engine.save_to_file(speech_text, 'output.wav')
                    engine.runAndWait()
                    if os.path.isfile(filename):
                            os.remove(filename)
                    wf = wave.open('output.wav', 'rb')
                    out = pyaudio.PyAudio()
                    stream = out.open(format =
                        out.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True,
                        output_device_index=outdeviceid)
                    data = wf.readframes(chunk)
                    # play stream (looping from beginning of file to the end)
                    while data != b'':
                        # writing to the stream is what *actually* plays the sound.
                        stream.write(data)
                        data = wf.readframes(chunk)
                    wf.close()
                    stream.close()
                    out.terminate()

                    if os.path.isfile("output.wav"):
                            os.remove("output.wav")
                    print("TTS FINISHED. HOLD KEY TO RECORD AGAIN.")
                sleep(1)
            except KeyboardInterrupt:
                print("REINITIALIZING...")
                sleep(2)
                break

if __name__ == "__main__":
    main()

