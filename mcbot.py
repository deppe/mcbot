import os
import re
import time
import random
from textblob import TextBlob
from slackclient import SlackClient

class MCBot(object):
    def __init__(self, token):
        self.token = token
        self.delay = 1
        self.user_id = None
        self.client = SlackClient(token)

    def connect(self):
        self.client.rtm_connect()
        self.user_id = self.query_user_id('michellecarter')

    def start(self):

        while True:
            command, channel = self.parse_rtm(self.client.rtm_read())
            if command and channel:
                self.handle_msg(command, channel)
            time.sleep(self.delay)

    def parse_rtm(self, rtm):
        for msg in rtm:
            print(msg)
            if msg['type'] == 'message' and msg['user'] != self.user_id:
                return msg['text'], msg['channel']
        return None, None

    def handle_msg(self, text, channel):
        if channel[0] == 'D' or self.is_mention(text):
            parser = Parser(text)
            self.client.api_call("chat.postMessage", channel=channel, text=parser.respond(), as_user=True)

    def is_mention(self, text):
        return re.search('<@' + self.user_id + '>', text)

    def query_user_id(self, name):
        res = self.client.api_call('users.list')
        for member in res['members']:
            if member['name'] == name:
                return member['id']


class Parser(object):
    GREETINGS = [':smiley: My day was okay. How was yours?', 'When are you doing it?', 'When are you gonna do it? Stop ignoring the question']

    def __init__(self, text):
        self.parsed = TextBlob(text)
        
    def respond(self):
        return random.choice(self.GREETINGS)


def main():
    token = os.environ.get('SLACK_BOT_TOKEN')
    bot = MCBot(token)
    bot.connect()
    bot.start()
    
if __name__ == "__main__":
    main()


