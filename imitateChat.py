import jieba
import trainMessage
import api
import random
from math import exp
import re

# 采用 Logistic 函数来改变回复概率
lastCnt = {}

# 处理新的聊天记录
def receiveMessage (mes, gid):
    if (gid not in lastCnt):
        lastCnt[gid] = -3
    mes = processMessage(mes)
    if (len(mes) == 0):
        return
    if (trainMessage.training is True):
        return
    if (gid not in trainMessage.groupQueue):
        trainMessage.groupQueue[gid] = []
    trainMessage.groupQueue[gid].append(mes)
    rand = random.uniform(0, 1)
    if (rand > 1 / (1 + exp(-lastCnt[gid]))):
        lastCnt[gid] += 1
        return
    predictMessage(mes, gid)

# 删除 CQ 码
def processMessage (mes):
    res = re.sub(r'\[CQ:(.*)\]', "", mes)
    res = re.sub(r'^\s*', "", res)
    return res

# 预测复读
def predictMessage (mes, gid):
    sims = trainMessage.getSortedMessage(mes)
    if (sims[0][1] < 0.6):
        return
    response = randomResponseMessage(str(sims[0][0]))
    if (response is None):
        lastCnt[gid] += 1
        return
    lastCnt[gid] = -3

    # 不能水的群
    if (gid == 1030450471 or gid == 260324771):
        return

    api.send_msg(trainMessage.chatMessage[int(response)], uid = None, gid = gid)

# 随机抽取可能的语料库
def randomResponseMessage (id):
    if (id not in trainMessage.relateMessage):
        return None
    total = 0
    for k in trainMessage.relateMessage[id].keys():
        if (trainMessage.relateMessage[id][k] < 3 or len(trainMessage.chatMessage[int(k)]) > 30):
            continue
        total += trainMessage.relateMessage[id][k]
    if (total == 0):
        return None
    rand = random.uniform(0, total)
    sum = 0
    for k in trainMessage.relateMessage[id].keys():
        if (trainMessage.relateMessage[id][k] < 3 or len(trainMessage.chatMessage[int(k)]) > 30):
            continue
        sum += trainMessage.relateMessage[id][k]
        if (rand <= sum):
            return k