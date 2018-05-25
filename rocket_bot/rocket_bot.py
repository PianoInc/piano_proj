from rocketchat_API.rocketchat import RocketChat

def rocket_notify(text=None, channel='test', username='bot'):
    rocket = RocketChat(username, '12345678', server_url='https://soorokim.duckdns.org')
    rocket.chat_post_message(text, channel='marketing')

def send_to_general(slack_message):
        rocket_notify(slack_message, 'general')

def send_to_marketing(slack_message):
    rocket_notify(slack_message, 'marketing')

##delete##
def ask_business(slack_msg):
    rocket_notify(slack_msg, 'test')
##delete##
