# -*- encoding: utf-8 -*-
#' '
#@file_name    :main.py
#@description    :
#@time    :2020/11/05 17:13:06
#@author    :Xingdi Zhang 
#@CONTACT   :Xingdi.Zhang@KAUST.EDU.SA 
#@version   :0.1
import time
import random
import xlrd
import numpy as np
import pdb

def loaExcelFile(path):
    """
    docstring
    """
    book=xlrd.open_workbook(path)
    sheet=book.sheet_by_index(0)
    id2statename=sheet.row_values(0)[1:]
    dict1={"Invalid":["Invalid","Invalid"]}
    for i in range(1,sheet.nrows):
        datarow=sheet.row_values(i)
        subset=[ ]
        statename=datarow[0]
        for j in range(1,sheet.ncols):
            element=int(datarow[j][0])
            if(element==1):
                subset.append(id2statename[j-1])    
        dict1[statename]=subset
    del dict1["Invalid"]
    # print(dict1)
    # print(id2statename)
    return dict1,id2statename
def State2Key(InputList,TargetSet):
    stringkey=""
    for item in TargetSet:
        if item in InputList:
            stringkey+="1"
        else:
            stringkey+="0"
    return stringkey
DV_RESTORE={}  
RuningSelect=[]

def Dpeqution(RuningLeft,Subsets,TargetSet):
    KEY=State2Key(RuningLeft,TargetSet) 
    if(KEY  in DV_RESTORE.keys()):
        return DV_RESTORE[KEY][0]
    else:
        # print("working on : ",KEY)
        bestOption=None
        if len(RuningLeft)>0:
            minS =int(999999999)
            for option in Subsets.keys() :
                intersect=[i for i in RuningLeft if i  in Subsets[option]]#make sure not choose subset repeatly
                if len(intersect)>0:#make sure not choose subset repeatly
                    newRuningLeft=[i for i in RuningLeft if i not in Subsets[option]]
                    cost=Dpeqution(newRuningLeft,Subsets,TargetSet)+1
                    del newRuningLeft
                    if(minS> cost):
                        minS=cost
                        bestOption=option
            if bestOption ==None:
                cost=int(9999999999)
            else:
                cost=minS
            
        else:
            cost=0
        DV_RESTORE[KEY]=[cost, bestOption]
        return cost
    


def DpSolver( Subsets, TargetSet):
    time_start=time.time()
    #prepocess1 :find indepent subsets
    SpecialElements=[]
    for elment in TargetSet:
        count=0
        for Subset in Subsets.values():
            if elment in Subset:
                count+=1
        if count ==1:
            SpecialElements.append(elment)
    IndepentSets=[]
    IndepentCover=[]
    for Subset in Subsets.keys():
        intersect=[ i for i  in Subsets[Subset] if i in SpecialElements]
        if len(intersect):
            IndepentSets.append(Subset)
            IndepentCover.extend(Subsets[Subset]  )
    # print(" Indepent subsets: ", IndepentSets)
    #Select Indepent subsets
    RuningLeft=[ i for i  in TargetSet if i not in IndepentCover] 
    SubsetsLeft={ }
    for (k,v) in Subsets.items() :
        if k not in IndepentSets:
            SubsetsLeft[k]=v
    if len(SubsetsLeft.keys())>100:
        print("*** SubsetsLeft Too long :",len(SubsetsLeft.keys()),"! Dynamic programming fails for high complexity!")
        return 999999999
    else:
        DV_RESTORE.clear()  
        RuningSelect.clear()
        Sk=Dpeqution(RuningLeft,SubsetsLeft,TargetSet)
        time_end=time.time()

        #calculate Length  DV   "State":[cost, option]
        
        while Sk!=0:
            option= DV_RESTORE[State2Key(RuningLeft, TargetSet)][1]
            if option==None:
                print(DV_RESTORE[State2Key(RuningLeft, TargetSet)])
            RuningLeft=[it for it in RuningLeft if it not in SubsetsLeft[option]]
            Sk-=1
            IndepentSets.append(option)
        # print("Final choice: ", IndepentSets)
        #Check Correctness:
        FinalCover=[]
        for it in IndepentSets:
            FinalCover.extend(Subsets[it])  
        FinalCover=[itm for itm in TargetSet if itm not in FinalCover]
        if len(FinalCover)>0:
            print("Wrong: Elments left behind:", FinalCover)
            return 999999999
        else:
            CostTime=(time_end-time_start)
            print('Correct, time :',CostTime, ' s')
            return CostTime


def RandomGenerateData(n):
    m=n
    TestC=[t for t in range(n)]  
    ValidCover=[]
    Subsets={}
    for tm in range(m):
        ID1=random.randint(1,int(n/5))
        Subset = list(np.random.choice(range(0, n), size=ID1, replace=False))
        Subsets[str(tm)]=Subset
        ValidCover.extend(Subset)
    Left=[it for it in TestC if it not in ValidCover]
    if len(Left)>=1:
        ID = list(np.random.choice(range(0, m), size=len(Left)*2, replace=False))
        for i, item in enumerate(Left):
            ID1 = str(ID[i*2])
            ID2 = str(ID[i*2+1])
            Subsets[ID1]=Subsets[ID1]+ [item]
            Subsets[ID2]=Subsets[ID2]+ [item]
    return Subsets,TestC

def GreedySolver(Subsets, TargetSet, use_real=0): 
    time_start=time.time()
    #modify subsets
    if use_real == 0:
        n = len(TargetSet)
        S = np.zeros((n,n))
        for key in Subsets.keys():
    	    for item in Subsets[key]:
    		    S[int(key), int(item)] = 1.0
    elif use_real == 1:
        states2id = {}
        for k, item in enumerate(TargetSet):
            states2id[item] = k
        n = len(TargetSet)
        S = np.zeros((n,n))
        for key in Subsets.keys():
            for item in Subsets[key]:
                S[states2id[key], states2id[item]] = 1.0
                
    #algorithm
    states = TargetSet
    states_order = []
    while np.sum(S) != 0:
        #find max cover
        sum_row = S.sum(1)
        maximum = np.max(sum_row)
        #print(maximum)
        index = np.where(sum_row == maximum)
        if len(index[0]) > 1:
            row = int(index[0][0])
        else:
            row = int(index[0])
        
        #choose the state
        states_chosen = states[row]
        states_order.append(states_chosen)
        
        #modify S
        for i, value in enumerate(S[row]):
            if value == 1:
                S[:,i] = 0
    time_end=time.time()
    CostTime=(time_end-time_start)
    print(states_order)
    return CostTime


def AverageRunningTimeTest():
    record1={}
    record2={}
    AvgRunTimes=200
    for comple in range(10,29):
        avgTime1=0.0
        avgTime2=0.0
        print("Testing size=",comple)
        for _ in range(0,AvgRunTimes):
            S,C=RandomGenerateData(comple)
            avgTime1+=DpSolver(S,C)
            avgTime2+=GreedySolver(S,C)
        avgTime1/=AvgRunTimes
        avgTime2/=AvgRunTimes
        record1[str(comple)]=avgTime1
        record2[str(comple)]=avgTime2
    print("record1=",record1)
    print("record2=",record2)
# record= {   
# '10': 0.00036903142929077147, 
# '11': 0.000483701229095459, 
# '12': 0.001161123514175415, 
# '13': 0.0011628305912017823, 
# '14': 0.0023096323013305662, 
# '15': 0.004047138690948486, 
# '16': 0.009481863975524902, 
# '17': 0.016377025842666627, 
# '18': 0.015543426275253297, 
# '19': 0.03680110692977905, 
# '20': 0.08568682312965394, 
# '21': 0.1425240957736969, 
# '22': 0.24144449710845947, 
# '23': 0.2642457389831543, 
# '24': 0.5444713473320008, 
# '25': 2.539850001335144, 
# '26': 2.6736352896690367, 
# '27': 3.9067941653728484, 
# '28': 9.939897587299347}
#TODO:
#1.debug greedy for warehouse_1.0.xlsx  --xiaodong done!
#2.accuracy --xingdi 
#3.visualization 

def main():
    """
    docstring
    """
    
    S, C=loaExcelFile("warehouse_1.0.xlsx")
    DpSolver(S, C)
    use_real = 1 #if use real data: use_real=1, else: use_real=0
    GreedySolver(S, C, use_real)
    AverageRunningTimeTest()



if __name__ == "__main__":
    main()
