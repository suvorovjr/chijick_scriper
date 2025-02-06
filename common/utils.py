import random


def get_headers():
    user_agent = f'chizhik_app/394 CFNetwork/1410.1 Darwin/{random.randint(21, 22)}.{random.randint(1, 6)}.0'
    headers = {
        'accept': '*/*',
        'accept-language': 'ru',
        'appversion': '1.17.0',
        'baggage': 'sentry-environment=production,sentry-public_key=d4f93d58429f462cb9ebf00cc7018aa9,sentry-release=chizhik-mobile-app%401.17.0,sentry-trace_id=3686556fc3ad499a9b141f0780b2d68c',
        'connection': 'keep-alive',
        'host': 'app.chizhik.club',
        'sentry-trace': '3686556fc3ad499a9b141f0780b2d68c-781b9ffee6094780-0',
        'user-agent': user_agent,
    }
    return headers
