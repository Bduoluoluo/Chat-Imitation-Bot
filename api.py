import requests
from imitateChat import receiveMessage
from urllib import parse
import trainMessage

baseUrl = 'http://127.0.0.1:5700/'

# 消息
def reveiveMes (message, uid, gid = None, rol = None, mid = None):
    if (message == "#save"):
        trainMessage.training = True
        trainMessage.train()
        trainMessage.training = False
        trainMessage.saveMessage()
        send_msg("Done!", None, gid)
        return
    receiveMessage(message, gid)

# 发送私聊或群聊消息
def send_msg (message, uid, gid = None):
    encodeMsg = parse.quote(message)
    if gid != None:
        payload = baseUrl + 'send_msg?group_id={0}&message={1}'.format(gid, encodeMsg)
    else:
        payload = baseUrl + 'send_msg?user_id={0}&message={1}'.format(uid, encodeMsg)
    requests.get(url = payload)
