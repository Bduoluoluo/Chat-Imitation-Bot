import jieba
from gensim import corpora, models, similarities
import json
import time
import api
import random
from math import exp
import re

chatMessage = []

groupMessage = {}

relateMessage = {}

tfidf = None
index = None
dictionary = None

# 采用 Logistic 函数来改变回复概率
lastCnt = {}

def receiveMessage (mes, gid):
    if (gid not in lastCnt):
        lastCnt[gid] = -5
    mes = processMessage(mes)
    if (len(mes) == 0):
        return
    if (mes not in chatMessage):
        chatMessage.append(mes)
    if (gid in groupMessage):
        lastMessage = groupMessage[gid]
        if (lastMessage not in relateMessage):
            relateMessage[lastMessage] = {}
        if (mes not in relateMessage[lastMessage]):
            relateMessage[lastMessage][mes] = 1
        else:
            relateMessage[lastMessage][mes] += 1
    groupMessage[gid] = mes
    rand = random.uniform(0, 1)
    if (rand > 1 / (1 + exp(-lastCnt[gid]))):
        lastCnt[gid] += 1
        return
    predictMessage(mes, gid)
    
def processMessage (mes):
    res = re.sub(r'\[CQ:(.*)\]', "", mes)
    res = re.sub(r'^\s*', "", res)
    return res

def predictMessage (mes, gid):
    messageDocList = [word for word in jieba.cut(mes)]
    messageDocVec = dictionary.doc2bow(messageDocList)
    sims = index[tfidf[messageDocVec]]
    sims = sorted(enumerate(sims), key = lambda item: -item[1])
    if (sims[0][1] < 0.7):
        return
    response = randomResponseMessage(chatMessage[sims[0][0]])
    if (response is None):
        lastCnt[gid] += 1
        return
    lastCnt[gid] = -5

    # 不能水的群
    if (gid == 1030450471 or gid == 260324771):
        return

    api.send_msg(response, uid = None, gid = gid)

def randomResponseMessage (mes):
    if (mes not in relateMessage):
        return None
    total = 0
    for k in relateMessage[mes].keys():
        total += relateMessage[mes][k]
    rand = random.uniform(0, total)
    sum = 0
    for k in relateMessage[mes].keys():
        sum += relateMessage[mes][k]
        if (rand <= sum):
            return k

def startChat ():
    loadMessge()
    while True:
        time.sleep(600)
        saveMessage()

def saveMessage ():
    tf = open("./chat/chatMessage.json", "w")
    json.dump(chatMessage, tf)
    tf.close()
    tf = open("./chat/relateMessage.json", "w")
    json.dump(relateMessage, tf)
    tf.close()
    loadMessge()

def loadMessge ():
    global chatMessage, relateMessage, tfidf, index, dictionary
    tf = open("./chat/chatMessage.json", "r")
    chatMessage = json.load(tf)
    tf = open("./chat/relateMessage.json", "r")
    relateMessage = json.load(tf)

    # 训练聊天记录
    texts_list=[]
    for sentence in chatMessage:
        sentence_list = [word for word in jieba.cut(sentence)]
        texts_list.append(sentence_list)
    
    dictionary = corpora.Dictionary(texts_list)
    corpus = [dictionary.doc2bow(doc) for doc in texts_list]
    tfidf = models.TfidfModel(corpus)
    index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features = len(dictionary.keys()))