import json
import logging
import os
import boto3

print('Loading function... ')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def event_to_dict(event):
    if 'body' in event:
        body = json.loads(event.get('body'))
        return body
    elif 'token' in event:
        body = event
        return body
    else:
        logger.error('unexpected event format')
        exit


class ChallangeJson(object):
    def data(self, key):
        return {
            'isBase64Encoded': 'true',
            'statusCode': 200,
            'headers': {},
            'body': key
        }


def invoke_function(function_name, body):
    logger.info('call: %s', function_name)
    client = boto3.client("lambda")
    res = client.invoke(
        FunctionName=function_name,
        InvocationType="Event",
        Payload=json.dumps(body))
    return


def handler(event, context):
    #getenv
    HOOK_CHANNEL = os.environ['HOOK_CHANNEL']
    BOT_NAME = os.environ['BOT_NAME']
    HOOK_REACTIONS = os.environ['HOOK_REACTIONS']
    HOOK_KEYWORD = os.environ['HOOK_KEYWORD']
    FNC_REACT = os.environ['FNC_REACT']
    FNC_REPLY = os.environ['FNC_REPLY']
    FNC_ANONY = os.environ['FNC_ANONY']
    HOOK_CHANNEL_FGO = os.environ['HOOK_CHANNEL_FGO']
    HOOK_KEYWORD_FGO = os.environ['HOOK_KEYWORD_FGO']
    FNC_FGO = os.environ['FNC_FGO']

    # Output the received event to the log
    logging.info(json.dumps(event))
    body = event_to_dict(event)

    # return if it was challange-event
    if 'challenge' in body:
        challenge_key = body.get('challenge')
        logging.info('return challenge key %s:', challenge_key)
        return ChallangeJson().data(challenge_key)

    # SlackAnonymousChannel
    if body.get('event').get('channel', '') == HOOK_CHANNEL and body.get(
            'event').get('username') != BOT_NAME:
        invoke_function(FNC_ANONY, body)

    # SlackReplyBot
    if HOOK_KEYWORD in body.get('event').get('text', ''):
        logger.info('hit: %s', HOOK_KEYWORD)
        invoke_function(FNC_REPLY, body)

    # SlackServerlessReactionBot
    emojis = HOOK_REACTIONS.split(',')
    if body.get('event').get('reaction') in emojis:
        logger.info('hit: %s', body.get('event').get('reaction'))
        invoke_function(FNC_REACT, body)

    # FgoBot
    if body.get('event').get('channel', '') in HOOK_CHANNEL_FGO.split(',') and body.get('event').get('text', '') in HOOK_KEYWORD_FGO.split(','):
        invoke_function(FNC_FGO, body)


    # exit always normally
    return {'statusCode': 200, 'body': 'quit'}
