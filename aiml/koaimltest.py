import aiml
from konlpy.tag import Mecab

mecab = Mecab()

kernel = aiml.Kernel()
kernel.learn("std-startup.xml")

kernel.respond("load aiml b")

# Press CTRL-C to break this loop
while True:
    data = raw_input("Input >> ")
    nldata = mecab.morphs(data.decode('utf-8'))
    print kernel.respond(" ".join(nldata))

