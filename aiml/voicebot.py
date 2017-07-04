#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import aiml
import os
import time
from gtts import gTTS
from konlpy.tag import Mecab
from action import perform_action, actions

#import pyttsx
from pygame import mixer
import warnings


import re
from google.cloud import speech
import grpc
import pyaudio
from six.moves import queue
# [END import_libraries]

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

mecab = Mecab()

def speak(speech):
   tts = gTTS(text=speech, lang='ko')
   tts.save('/dev/shm/speech.mp3')
   mixer.init()
   mixer.music.load('/dev/shm/speech.mp3')
   mixer.music.play()
   while mixer.music.get_busy():
       time.sleep(1)
   #os.system('mpg123 /dev/shm/speak.mp3')

class MicAsFile(object):
    """Opens a recording stream as a file-like object."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Flush out the read, just in case
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def read(self, chunk_size):
        if self.closed:
            return

        # Use a blocking get() to ensure there's at least one chunk of data.
        data = [self._buff.get()]

        # Now consume whatever other data's still buffered.
        while True:
            try:
                data.append(self._buff.get(block=False))
            except queue.Empty:
                break

        if self.closed:
            return
        return b''.join(data)
# [END audio_stream]

def listen_print_loop(results_gen):
    """Iterates through server responses and prints them.

    The results_gen passed is a generator that will block until a response
    is provided by the server. When the transcription response comes, print it.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    for result in results_gen:
        if not result.alternatives:
            continue

        # Display the top transcription
        transcript = result.transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * max(0, num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            #print(transcript + overwrite_chars)
            #print(transcript)
            nldata = mecab.morphs(transcript.decode('utf-8'))
            speech = kernel.respond(" ".join(nldata))
            if any(q in speech for q in actions.keys()):
                speech = perform_action(speech, kernel)
            print speech
            if len(speech) != 0:
                speak(speech)
            else:
                speak("무슨 말인지 모르겠습니다.")

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break

            num_chars_printed = 0


def main():
    speech_client = speech.Client()

    with MicAsFile(RATE, CHUNK) as stream:
        audio_sample = speech_client.sample(
            stream=stream,
            encoding=speech.encoding.Encoding.LINEAR16,
            sample_rate_hertz=RATE)
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        language_code = 'ko-KR'  # a BCP-47 language tag
        results_gen = audio_sample.streaming_recognize(
                language_code=language_code, interim_results=True)
        #results_gen = audio_sample.recognize(language_code=language_code)

        # Now, put the transcription responses to use.
        listen_print_loop(results_gen)


if __name__ == '__main__':
    kernel = aiml.Kernel()

    if os.path.isfile("bot_brain.brn"):
        kernel.bootstrap(brainFile = "bot_brain.brn")
    else:
        kernel.bootstrap(learnFiles = "std-startup.xml", commands = "load aiml b")
    #kernel.saveBrain("bot_brain.brn")

    main()

