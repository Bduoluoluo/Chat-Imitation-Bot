from flask import Flask, request
from api import reveiveMes
from trainMessage import initialTrain

app = Flask(__name__)

botStart = False

# '''监听端口，获取QQ信息'''
@app.route('/', methods = ["POST"])
def post_data ():
    global botStart
    requText = request.get_json()
    mid = requText.get('message_id')
    if requText.get('post_type') == 'message':
        meg_type = requText.get('message_type')
        uid = requText.get('sender').get('user_id')
        msg = requText.get('raw_message')
        # 接收消息
        if meg_type == 'group':
            rol = requText.get('sender').get('role')
            gid = requText.get('group_id')
            reveiveMes(msg, uid, gid, rol, mid)
    if (botStart is False):
        botStart = True
        initialTrain()
    return "OK"

if __name__ == '__main__':
    app.run(debug = True, host = '127.0.0.1', port = 5701)

