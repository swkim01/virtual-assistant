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

from pygame import mixer
import speech_recognition as sr
#import pyttsx
import warnings

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

def listen():
    r = sr.Recognizer()
    with sr.Microphone(device_index=2, sample_rate=44100) as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        #print r.recognize_google(audio)
        return r.recognize_google(audio, language="ko-KR")
    except sr.UnknownValueError:
        speak("무슨 말인지 모르겠습니다.")
        #return(listen())
    except sr.RequestError as e:
        print("구글 음성인식 서비스를 요청할 수 없습니다: {0}".format(e))

kernel = aiml.Kernel()

if os.path.isfile("bot_brain.brn"):
    kernel.bootstrap(brainFile = "bot_brain.brn")
else:
    kernel.bootstrap(learnFiles = "std-startup.xml", commands = "load aiml b")
    #kernel.saveBrain("bot_brain.brn")

# kernel now ready for use
while True:
    data = listen()

    #speech = kernel.respond(data)
    print "speech>> "
    if data != None:
      print "speech>> ", data
      nldata = mecab.morphs(data.decode('utf-8'))
      speech = kernel.respond(" ".join(nldata))
      print speech
      if any(q in speech for q in actions.keys()):
          speech = perform_action(speech, kernel)
      if len(speech) != 0:
          speak(speech)
      else:
        speak("무슨 말인지 모르겠습니다.")
