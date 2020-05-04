import numpy as np
import pandas as pd
import math
import pickle
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from pprint import pprint

class FP_Analyzer(object):
    def __init__(self, filePath = "MyModules/Results/result.pickle"):
        self.pattern_dict = dict()
        self.pattern_list = []
        self.header = []
        self.read(filePath = filePath)
    
    def read(self, filePath, minLen = 1):
        with open(filePath, 'rb') as handle:
            self.pattern_dict = pickle.load(handle)
            self.header = self.pattern_dict["__header__"]
            del(self.pattern_dict["__header__"])

    def fit_transform(self, patterns_, header):
        vectorizer = CountVectorizer(tokenizer = lambda x: x, lowercase=False)
        mat = vectorizer.fit_transform(patterns_ + [header])
        return mat[:-1]
    #패턴들을 2차원 매트릭스에 투영
    def consineSim(self, user_info = None, matrix = sparse.csr_matrix):
        temp = []
        for i in range(matrix.get_shape()[0]):
            row = matrix.getrow(i)
            x, y = row.nonzero()
            if(len(x)> 1 and len(y) > 1):
                arr = row.toarray()[0]
                cos_sim = lambda x, y: np.dot(x, y)/(np.linalg.norm(x)*np.linalg.norm(y))
                cosine_sim = cos_sim(user_info, arr)
                temp.append((i, cosine_sim))
        return sorted(temp, key = lambda x: x[1], reverse = True)
    #입력받은 패턴과 다른 패턴들의 코사인 유사도 계산
    def jarcardSim(self, user_info = None, matrix = sparse.csr_matrix):
        temp = []
        for i in range(matrix.get_shape()[0]):
            row = matrix.getrow(i)
            x, y = row.nonzero()
            if(len(x)> 1 and len(y) > 1):
                arr = row.toarray()[0]
                jar_sim = lambda x, y: np.dot(x, y)/(np.sum(x) + np.sum(y) - np.dot(x, y))
                sim = jar_sim(user_info, arr)
                temp.append((i, sim))
        return sorted(temp, key = lambda x: x[1], reverse = True)
    #입력받은 패턴과 다른 패턴들의 자카드 유사도 계산

    def devide(self, pattern, user):
        inter = []
        sub = []
        for item in pattern:
            if(item in user):
                inter.append(item)
            else:
                sub.append(item)
        if (len(sub) != 0 and len(inter) != 0):
            return inter, sub
        else:
            return None
    #두 패턴의 교집합(조건절)과 차집합(결과절) 반환
    def getSupp(self, item):
        item = tuple(sorted(item, key = lambda x:x))
        try:
            return self.pattern_dict[item]
        except KeyError:
            return None

    def estimate(self, condition = [], result = []):
        #조건, 결과 패턴들을 알파벳 순서로 정렬
        condition = sorted(condition, key = lambda x:x)
        result = sorted(result, key = lambda x:x)
        union = sorted(condition + result, key = lambda x:x)#조건절과 결과절의 합집합

        sup_cond = self.pattern_dict[tuple(condition)]
        sup_res = self.pattern_dict[tuple(result)]
        sup_inter = self.pattern_dict[tuple(union)]
        
        l = 30000#전체 트랜잭션 개수

        support = sup_inter/l
        confidence = sup_inter/sup_cond
        lift = sup_inter/(sup_cond * sup_res)*l

        return support, confidence, lift
        #패턴의 지지도, 신뢰도, 향상도 반환
    def recommend(self, user_info = [], num = 10):
        recommend_dict = dict()
        tmp_user_info = [1 if self.header[i] in user_info else 0 for i in range(len(self.header))]
        tmp_patterns = [item for item, sup in self.pattern_dict.items()]

        pattern_matrix = self.fit_transform(tmp_patterns, self.header)
        #패턴들을 벡터 공간으로 투영
        sim_list = self.jarcardSim(np.array(tmp_user_info), pattern_matrix)
        #자카드 유사도를 사용해 유저의 패턴과 가장 유사한 패턴들 추출
        
        tmp_dict = dict()
        for idx, sim in sim_list[:100]:#유사도 상위 100개 패턴 분석
            ret = self.devide(tmp_patterns[idx], user_info)
            #조건절과 결과절을 나눔
            if(ret is not None):
                supp, conf, lif = self.estimate(ret[0], ret[1])
                score = (sim + supp+ conf)/3 * 10**math.log(lif)
                #score = lif
                #랭킹 점수 계산
                recommend_item = tuple(ret[1])
                if(recommend_item not in tmp_dict):
                    tmp_dict[recommend_item] = (score, 1)
                else:
                    a, b = tmp_dict[recommend_item]
                    tmp_dict[recommend_item] = (a + score, b+1)#(점수의 합, 개수)

        for items, score_ in tmp_dict.items():
            score = score_[0]/score_[1]#평균 점수
            for item in items:
                if(item not in recommend_dict):
                    recommend_dict[item] = (score, score, 1)#평균 점수, 점수 총합, 개수
                else:
                    t, s_, c = recommend_dict[item]
                    recommend_dict[item] = ((s_ + score)/(1+c), s_ + score, 1+c)
        
        for item, score_ in recommend_dict.items():
            recommend_dict[item] = score_[0]
        return sorted(recommend_dict.items(), key = lambda x:x[1], reverse = True)[:num]
        #랭킹에 따른 추천 아이템 반환
if __name__ == "__main__":
    fpa = FP_Analyzer()
    user_info = ["brown bread", "cream cheese", "whole milk"]

    pprint(fpa.recommend(user_info = user_info, num = 20))