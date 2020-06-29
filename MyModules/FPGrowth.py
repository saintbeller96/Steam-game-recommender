#Made by saintbeller96
import time
import logging
import pickle
import sys
from pprint import pprint
from MyMariaDB import MyDBController

sys.setrecursionlimit(10**6)

class Node(object):
    def __init__(self, item = None, parent = None, sup = 1):
        self.item = item
        self.children = dict()
        self.parent = parent
        self.sup = sup

class Header(object):
    def __init__(self, sup = 1, idx = -1):
        self.sup_ = sup
        self.idx = idx
        self.link_ = []

class FPTree(object):
    def __init__(self, minsup = 0):
        # 헤더 테이블 구성
        # 키: 아이템    값: Header 클래스
        self.headerTable = dict()
        self.rootNode = Node()
        self.minsup = minsup

    def pruning(self):#빈발하지 못한 패턴들을 헤더테이블에서 제거
        for item, value in list(self.headerTable.items()):
            if(value.sup_ < self.minsup):
                del(self.headerTable[item])
    def reorder(self):#헤더 테이블 지지도 내림차순으로 재정렬
        for idx, (item, value) in enumerate(sorted(self.headerTable.items(), key = lambda x:x[1].sup_, reverse = True)):
            self.headerTable[item].idx = idx

class FP_Growth(object):
    def __init__(self, minsup = 10, savePath = "Results/result.pickle"):
        self.gloabl_tree = FPTree(minsup=minsup)
        self.item_list = []
        self.minsup = minsup
        self.savePath = savePath

    def createTree(self, fp_tree = None, dataset = None, paths_sup = None, isGlobal = True):#데이터셋/조건부경로를 읽고 Fp-tree 생성        
        if(isGlobal):#글로벌 FP-Tree를 생성할 경우
            fp_tree = self.gloabl_tree
            paths_sup = [1 for i in range(len(dataset))]

        for t, s in zip(dataset, paths_sup):#FP-Tree의 헤더테이블 생성
            path_sup = s
            for item in t:
                if(item in fp_tree.headerTable):
                    fp_tree.headerTable[item].sup_ += path_sup
                else:
                    fp_tree.headerTable[item] = Header(sup = path_sup)

                if(isGlobal):
                    if(item not in self.item_list):
                        self.item_list.append(item)
        fp_tree.pruning()#빈발하지 못한 패턴을 헤더테이블에서 제거        
        if(isGlobal):
            fp_tree.reorder()

        for t, s in zip(dataset, paths_sup):#FP-Tree 트리 본체 생성
            tmp = [i for i in t if i in fp_tree.headerTable]
            path_sup = s
            curNode = fp_tree.rootNode
            for item in tmp:
                if(item not in curNode.children):#현재 노드의 자식으로 아이템의 노드가 없는 경우
                    curNode.children[item] = Node(item = item, parent = curNode, sup = path_sup)
                    fp_tree.headerTable[item].link_.append(curNode.children[item])
                else:#있으면 해당 노드의 sup을 경로 지지도만큼 증가시켜 줌
                    curNode.children[item].sup += path_sup
                curNode = curNode.children[item]

        return fp_tree

    def __mine(self, fp_tree, prefix_pattern=[], depth = 0):
        for item, h in sorted(fp_tree.headerTable.items(), key = lambda x:x[1].sup_):#가장 지지도가 낮은 아이템부터 마이닝 진행
            if(h.sup_ >= self.minsup):#최소 지지도 조건을 만족한 아이템만 마이닝                
                prefix = prefix_pattern + [item]
                prefix = sorted(prefix, key = lambda x:x)              
                yield prefix, h.sup_

                #Prefix 아이템를 기반으로하는 경로 추출
                conditional_paths = []#item을 기반으로 하는 경로를 저장하는 리스트
                paths_sup = []#각 경로의 지지도 저장하는 리스트
                for node_ in fp_tree.headerTable[item].link_:         
                    curNode = node_.parent
                    paths_sup.append(node_.sup)
                    tmp_tran = []
                    while(curNode.item != None):
                        tmp_tran.insert(0, curNode.item)
                        curNode = curNode.parent
                    conditional_paths.append(tmp_tran)

                #Prefix를 기반으로 하는 조건부 FP-Tree 생성 및 마이닝
                cfpTree = self.createTree(FPTree(self.minsup), conditional_paths, paths_sup, isGlobal = False)

                for p in self.__mine(fp_tree = cfpTree, prefix_pattern = prefix_pattern + [item], depth = depth+1):
                    yield p
    
    def mine(self):
        mylogger = logging.getLogger("my")
        mylogger.setLevel(logging.INFO)
        mylogger.addHandler(logging.StreamHandler())

        t = time.time()
        tmp = {tuple(pattern):sup for pattern, sup in list(self.__mine(fp_tree=self.gloabl_tree, prefix_pattern=[],depth = 0))}
        with open(self.savePath, 'wb') as handle:
            tmp["__header__"] = sorted(self.item_list, key=lambda x: x)
            pickle.dump(tmp, handle, protocol=pickle.HIGHEST_PROTOCOL)
        mylogger.info("마이닝에 걸린 시간: %s"% str(time.time() - t))
        mylogger.info("빈발 패턴의 개수: %s"% str(len(tmp) -1))
        return tmp


