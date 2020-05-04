from MyModules.FP_Analyzer import FP_Analyzer
from MyModules.MyMariaDB import MyDBController
from gensim.models.word2vec import Word2Vec
from pprint import pprint

import json
import random

w2vPath = "MyModules/Results/temp3.model"
tagsPath = "MyModules/Results/tags_sim3.json"
fimPath = "MyModules/Results/fps_steam250.pickle"

class SGRecommender(object):
    def __init__(self, num = 30):
        self.num = num
        self.db_con = MyDBController('127.0.0.1', 'guest', '0000', 'steam_db')

    def __fpm(self, input_data):
        fpa = FP_Analyzer(filePath=fimPath)
        recom_from_fpm = fpa.recommend(input_data, num=self.num)

        return {item[0]:item[1] for item in recom_from_fpm}
        #return [item[0] for item in recom_from_fpm]

    def __word2vec(self, input_data):
        model = Word2Vec.load(w2vPath)
        recom_from_w2v = model.wv.most_similar(positive=input_data, topn=self.num)
        return {item[0]:item[1] for item in recom_from_w2v}
        #return [item[0] for item in recom_from_w2v]

    def __cbf(self, input_data, mode= 0):
        tmp = {}
        with open(tagsPath, 'r', encoding='utf-8') as handle:
            tmp = json.load(handle)

        d = dict()    
        for game in input_data:
            for i in tmp[game]:
                if(i[0] in input_data):
                    continue
                if(i[0] not in d):
                    d[i[0]] = [(game, i[1])]
                else:
                    d[i[0]].append((game, i[1]))
        
        def temp(x):
            sum = 0
            for i in x:
                sum += i[1]
            return sum

        if(mode == 1):
            t = sorted(d.items(), key = lambda x: self.db_con.getTotalPlayTime(x[0]), reverse = True)
            return [item[0] for item in t[:12]]
        elif(mode == 2):
            t = sorted(d.items(), key = lambda x: self.db_con.getDate(x[0]), reverse = True)
            return [item[0] for item in t[:12]]
        else:
            t = sorted(d.items(), key = lambda x: temp(x[1]), reverse = True)
            return [item[0] for item in t[:12]]

    def temp_rec(self, user_info):
        fpm_set = self.__fpm(user_info)
        w2v_set = self.__word2vec(user_info)
        # pprint(fpm_set)
        # pprint(w2v_set)
        inter = fpm_set.intersection(w2v_set)

        pprint(inter)    

    def recommend(self, user_info, mode = 0):
        recommend_list = []
        if(len(user_info) == 0):
            pass
        else:
            cf = [] 
            fpm_dict = self.__fpm(user_info)
            w2v_dict = self.__word2vec(user_info)

            fpm_set = set(fpm_dict.keys())
            w2v_set = set(w2v_dict.keys())

            inter = list(set.intersection(fpm_set, w2v_set))
            subset_fpm = list(set.difference(fpm_set, w2v_set))
            subset_w2v = list(set.difference(w2v_set, fpm_set))
            union = list(set.union(fpm_set, w2v_set))


            if(mode == 1):#인기순
                ss = sorted(union, key = lambda x:self.db_con.getTotalPlayTime(x), reverse = True)
                ss = [item for item in ss[:15]]
                cf.extend(ss)
            elif(mode == 2):#출시일순
                ss = sorted(union, key = lambda x:self.db_con.getDate(x), reverse = True)
                ss = [item for item in ss[:15]]
                cf.extend(ss)
            else:#새로운 게임
                cf.extend(inter)
                ss1 = sorted(subset_fpm, key = lambda x:fpm_dict[x], reverse = True)[:int((15-len(inter))/2+0.5)]
                ss2 = sorted(subset_w2v, key = lambda x:w2v_dict[x], reverse = True)[:int((15-len(inter))/2+0.5)]
                cf.extend(ss1)
                cf.extend(ss2)

            cbf = self.__cbf(user_info, mode)

            # for i in list(cf):
            #     for j in cbf:
            #         if(i == j or i in user_info):
            #             cf.remove(i)

            return cf, cbf

if __name__ == "__main__":
    user_info = ["107100"]
    sgr = SGRecommender()
    rl = sgr.recommend(user_info)

    print(rl)
    #sgr.temp_rec(["domestic eggs","mayonnaise"])
    #pass
    