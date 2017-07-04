import aiml
from konlpy.tag import Mecab
import telegram
from action import perform_action, actions

mecab = Mecab()

kernel = aiml.Kernel()
kernel.learn("std-startup.xml")
kernel.respond("load aiml b")

token = '<TOKEN>'
bot = telegram.Bot(token=token)
last_update_id = None

# Press CTRL-C to break this loop
while True:
    for update in bot.getUpdates(offset=last_update_id, timeout=10):
        chat_id = update.message.chat_id
        message = update.message.text.encode('utf-8')
        if message != None:
            nldata = mecab.morphs(message.decode('utf-8'))
            resp = kernel.respond(" ".join(nldata))
            if any(q in resp for q in actions.keys()):
                resp = perform_action(resp, kernel)
            if len(resp) != 0:
                bot.sendMessage(chat_id=chat_id, text=resp)
            last_update_id = update.update_id + 1

