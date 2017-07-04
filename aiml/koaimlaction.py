import aiml
from konlpy.tag import Mecab
from action import perform_action, actions

mecab = Mecab()

kernel = aiml.Kernel()
kernel.learn("std-startup.xml")
kernel.respond("load aiml b")

# Press CTRL-C to break this loop
while True:
    data = raw_input("Input >> ")
    nldata = mecab.morphs(data.decode('utf-8'))
    resp = kernel.respond(" ".join(nldata))
    if any(q in resp for q in actions.keys()):
        resp = perform_action(resp, kernel)
    print resp

