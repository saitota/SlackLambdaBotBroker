import json
import logging
import os
import boto3

print('Loading function... ')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    #getenv
    HOOK_CHANNEL = os.environ['HOOK_CHANNEL']
    BOT_NAME = os.environ['BOT_NAME']
    #HOOK_REACTION = os.environ['HOOK_REACTION']
    HOOK_REACTIONS = os.environ['HOOK_REACTIONS']
    HOOK_KEYWORD = os.environ['HOOK_KEYWORD']
    FNC_REACT = os.environ['FNC_REACT']
    FNC_REPLY = os.environ['FNC_REPLY']
    FNC_ANONY = os.environ['FNC_ANONY']
    
    #受信したjsonをLogsに出力
    logging.info(json.dumps(event))
    
    #print (type(event))
    # json処理
    if 'body' in event:
        body = json.loads(event.get('body'))
    elif 'token' in event:
        body = event
    else:
        logger.error('unexpected event format')
        return {'statusCode': 500, 'body': 'error:unexpected event format'}
        
    #url_verificationイベントに返す
    if 'challenge' in body:
        challenge = body.get('challenge')
        logging.info('return challenge key %s:', challenge)
        return {
            'isBase64Encoded': 'true',
            'statusCode': 200,
            'headers': {},
            'body': challenge
        }
        
    client = boto3.client("lambda")
    # SlackAnonymousChannel
    if body.get('event').get('channel','') == HOOK_CHANNEL and body.get('event').get('username') != BOT_NAME:
        logger.info('hit: %s',HOOK_CHANNEL)
        logger.info('call: %s',FNC_ANONY)
        res = client.invoke(
            FunctionName=FNC_ANONY,
            InvocationType="Event",
            Payload=json.dumps(body)
        )
    # SlackReplyBot
    if HOOK_KEYWORD in body.get('event').get('text',''):
        logger.info('hit: %s',HOOK_KEYWORD)
        logger.info('call: %s',FNC_REPLY)
        res = client.invoke(
            FunctionName=FNC_REPLY,
            InvocationType="Event",
            Payload=json.dumps(body)
        )
    # SlackServerlessReactionBot
    emojis = HOOK_REACTIONS.split(',')
    if body.get('event').get('reaction') in emojis:
        logger.info('hit: %s',body.get('event').get('reaction'))
        logger.info('call: %s',FNC_REACT)
        res = client.invoke(
            FunctionName=FNC_REACT,
            InvocationType="Event",
            Payload=json.dumps(body)
        )
        
    # exit always normally
    return {'statusCode': 200, 'body': 'quit'}
