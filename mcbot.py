import os
import re
import time
import random
from textblob import TextBlob
from slackclient import SlackClient
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

class MCBot(object):
    def __init__(self, token, chatbot):
        self.token = token
        self.delay = 1
        self.user_id = None
        self.client = SlackClient(token)
        self.chatbot = chatbot
        self.trainer = Trainer('data.txt')

    def connect(self):
        self.client.rtm_connect()
        self.user_id = self.query_user_id('michellecarter')
        self.train()

    def start(self):
        while True:
            command, channel = self.parse_rtm(self.client.rtm_read())
            if command and channel:
                self.handle_msg(command, channel)

    def parse_rtm(self, rtm):
        for msg in rtm:
            print(msg)
            if msg['type'] == 'message' and msg['user'] != self.user_id:
                return msg['text'], msg['channel']
        return None, None

    def handle_msg(self, text, channel):
        if channel[0] == 'D' or self.is_mention(text):
            response = self.chatbot.get_response(text)
            self.client.api_call("chat.postMessage", channel=channel, text=str(response), as_user=True)
            self.train()

    def train(self):
        os.remove('database.db')
        self.trainer.train(self.chatbot)

    def is_mention(self, text):
        return re.search('<@' + self.user_id + '>', text)

    def query_user_id(self, name):
        res = self.client.api_call('users.list')
        for member in res['members']:
            if member['name'] == name:
                return member['id']


class Trainer(object):
    def __init__(self, filename):
        self.filename = filename

    def train(self, chatbot):
        for convo in self.get_next_convo():
            chatbot.train(convo)

    def get_next_convo(self):
        with open(self.filename) as f:
            M = ''
            F = ''
            for line in f:
                person, text = map(lambda x: x.strip(), line.split(':'))

                if person == 'M':
                    if F:
                        yield [M.strip(), F.strip()]
                        M = ''
                        F = ''
                    M += text + ' '
                elif person == 'F':
                    F += text + ' '

def main():
    chatbot = ChatBot('mcbot')
    chatbot.set_trainer(ListTrainer)
    token = os.environ.get('SLACK_BOT_TOKEN')
    bot = MCBot(token, chatbot)
    bot.connect()
    bot.start()
    
if __name__ == "__main__":
    main()


