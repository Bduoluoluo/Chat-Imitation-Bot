import jieba
import json
from gensim import corpora, models, similarities
import time

chatMessage = []
relateMessage = {}
groupQueue = {}
tfidf = None
index = None
dictionary = None
training = False

# 获取相似度序列（递减）
def getSortedMessage (mes):
    messageDocList = [word for word in jieba.cut(mes)]
    messageDocVec = dictionary.doc2bow(messageDocList)
    sims = index[tfidf[messageDocVec]]
    sims = sorted(enumerate(sims), key = lambda item: -item[1])
    return sims

def train ():
    for i in groupQueue.keys():
        queue = groupQueue[i]
        groupQueue[i] = []
        for j in range(len(queue) - 1):
            lastList = []
            nowList = []
            sims = getSortedMessage(queue[j])
            for k in sims:
                if (k[1] < 0.8):
                    break
                lastList.append(k[0])
            if (len(lastList) == 0):
                chatMessage.append(queue[j])
                lastList.append(len(chatMessage) - 1)
                trainModel()
            sims = getSortedMessage(queue[j + 1])
            for k in sims:
                if (k[1] < 0.8):
                    break
                nowList.append(k[0])
            if (len(nowList) == 0):
                chatMessage.append(queue[j + 1])
                nowList.append(len(chatMessage) - 1)
                trainModel()
            for k in lastList:
                for l in nowList:
                    if (k not in relateMessage):
                        relateMessage[k] = {}
                    if (l not in relateMessage[k]):
                        relateMessage[k][l] = 0
                    relateMessage[k][l] += 1

# 每 60 分钟重新训练一次
def initialTrain ():
    global training
    loadMessage()
    trainModel()
    while True:
        time.sleep(3600)
        training = True
        train()
        training = False
        saveMessage()

# 训练聊天记录
def trainModel ():
    global tfidf, index, dictionary
    texts_list = []
    for sentence in chatMessage:
        sentence_list = [word for word in jieba.cut(sentence)]
        texts_list.append(sentence_list)
    dictionary = corpora.Dictionary(texts_list)
    corpus = [dictionary.doc2bow(doc) for doc in texts_list]
    tfidf = models.TfidfModel(corpus)
    index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features = len(dictionary.keys()))

# 读取本地文件并训练
def loadMessage ():
    global chatMessage, relateMessage
    tf = open("./chat/chatMessage.json", "r")
    chatMessage = json.load(tf)
    tf = open("./chat/relateMessage.json", "r")
    relateMessage = json.load(tf)
    trainModel()

# 保存收集的记录到本地文件
def saveMessage ():
    tf = open("./chat/chatMessage.json", "w")
    json.dump(chatMessage, tf)
    tf.close()
    tf = open("./chat/relateMessage.json", "w")
    json.dump(relateMessage, tf)
    tf.close()