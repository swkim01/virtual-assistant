#-*- coding: utf-8 -*-

import os
import subprocess
import datetime

def today():
    day = datetime.date.today().strftime("%Y년 %m월 %d일")
    return " ".join([u"오늘은", day.decode('utf-8'), u"입니다"])

def disk_space():
    '''Check available disk space'''

    result = subprocess.check_output("df -h .", shell=True)
    output = result.split()
    formatted_output = {
        'total':output[8],
        'used':output[9],
        'used_percentage':output[11],
        'free':output[10]}
    return 'Disk space:\nTotal: {total}\nUsed:{used} ({used_percentage})\nFree:{free}'.format(
        **formatted_output)

def load_aiml(kernel):
    '''reload aiml files'''

    kernel.respond('load aiml b')
    return 'Data crammed...brain reloaded..shoot'

def save(kernel):
    '''save brain file'''

    #from koaimlaction import kernel
    kernel.saveBrain("bot_brain.brn")
    return 'brain saved'

def perform_action(message, kernel):
    '''perform user actions '''

    action_index = [c in message for c in actions.keys()].index(True)
    try:
        response = actions[actions.keys()[action_index]](kernel)
    except ValueError:
        response = 'Insufficient Permissions to execute actions'

    return response

actions = {
    'disk':disk_space,
    'load_aiml':load_aiml,
    'space':disk_space,
    'day':today,
    'save':save}

if __name__ == "__main__":
    print today()
