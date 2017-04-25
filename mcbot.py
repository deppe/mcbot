import os
import re
import time
import random
import argparse
from slackclient import SlackClient
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

class MCBot(object):
    def __init__(self, token, chatbot):
        self.token = token
        self.user_id = None
        self.slack = Slacker(token)
        self.chatbot = chatbot
        self.trainer = Trainer('data.txt')

    def connect(self):
        self.slack.connect()
        self.user_id = self.query_user_id('michellecarter')
        self.train()

    def start(self):
        for command, channel, user in self.slack.read_rtm():
            if user != self.user_id:
                self.handle_msg(command, channel)

    def handle_msg(self, text, channel):
        rand = random.random()

        if channel[0] == 'D' or self.is_mention(text):
            response = self.chatbot.get_response(text)
            self.slack.post_message(channel, str(response))
            self.train()

    def train(self):
        os.remove('database.db')
        self.trainer.train(self.chatbot)

    def is_mention(self, text):
        return re.search('<@' + self.user_id + '>', text)

    def query_user_id(self, name):
        return self.slack.find_user(name)['id']

class Slacker(object):
    def __init__(self, token):
        self.client = SlackClient(token)
        self.delay = 2

    def connect(self):
        self.client.rtm_connect()

    def read_rtm(self):
        while True:
            rtm = self.client.rtm_read()
            if rtm:
                command, channel, user = self.parse_rtm(rtm)
                if command and channel:
                    yield command, channel, user
            else:
                time.sleep(self.delay)

    def parse_rtm(self, rtm):
        for msg in rtm:
            print(msg)
            if msg['type'] == 'message' and msg.get('user'):
                return msg['text'], msg['channel'], msg['user']
        return None, None, None


    def post_message(self, channel, text):
        res = self.client.api_call("chat.postMessage", channel=channel, text=text, as_user=True)
        print(res)

    def list_channels(self):
        return self.client.api_call('channels.list')['channels']

    def list_users(self):
        return self.client.api_call('users.list')['members']

    def find_user(self, name):
        res = self.list_users()
        for member in res:
            if member['name'] == name:
                return member

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

def print_slack_list(func):
    for item in func():
        print('%s %s' % (item['id'], item['name']))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', nargs='?', choices=['channels', 'users'])
    parser.add_argument('-m', '--message')
    parser.add_argument('-c', '--channel')
    args = parser.parse_args()
    print (args)

    token = os.environ['SLACK_BOT_TOKEN']

    if args.list == 'channels':
        print_slack_list(Slacker(token).list_channels)
    elif args.list == 'users':
        print_slack_list(Slacker(token).list_users)
    elif args.message and args.channel:
        Slacker(token).post_message(args.channel, args.message)
    else:
        chatbot = ChatBot('mcbot')
        chatbot.set_trainer(ListTrainer)
        bot = MCBot(token, chatbot)
        bot.connect()
        bot.start()
    
if __name__ == "__main__":
    main()


