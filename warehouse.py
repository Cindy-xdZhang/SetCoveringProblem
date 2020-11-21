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
def RandomGenerateData2(n,m):
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
        ID = list(np.random.choice(range(0, m), size=len(Left)*2, replace=True))
        for i, item in enumerate(Left):
            ID1 = str(ID[i*2])
            ID2 = str(ID[i*2+1])
            Subsets[ID1]=Subsets[ID1]+ [item]
            Subsets[ID2]=Subsets[ID2]+ [item]
    return Subsets,TestC


DV_RESTORE={}  
RuningSelect=[]
def State2Key(InputList,TargetSet):
    stringkey=""
    for item in TargetSet:
        if item in InputList:
            stringkey+="1"
        else:
            stringkey+="0"
    return stringkey
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
        return 999999999,999999999
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
            return 999999999,999999999
        else:
            CostTime=(time_end-time_start)
            # print('Correct, time :',CostTime, ' s')
            return CostTime,len(IndepentSets)


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
    # print(states_order)
    return CostTime,len(states_order )

def AverageRunningTest():
    record1={}
    record2={}
    AvgRunTimes=200
    for comple in range(10,29):
        avgTime1=0.0
        avgTime2=0.0
        avgRatio=0.0
        print("Testing size=",comple)
        for _ in range(0,AvgRunTimes):
            S,C=RandomGenerateData(comple)
            RuningTimeDp, RightNumber=DpSolver(S,C)
            RuningTimeGreedy, ApproximateNumber=GreedySolver(S,C)
            avgTime1+=RuningTimeDp
            avgTime2+=RuningTimeGreedy
            ratio= ApproximateNumber/RightNumber
            avgRatio+=ratio

        avgTime1/=AvgRunTimes
        avgTime2/=AvgRunTimes
        avgRatio/=AvgRunTimes
        record1[str(comple)]=(avgTime1)
        record2[str(comple)]=(avgTime2,avgRatio )
    print("record1=",record1) 
    print("record2=",record2)
# record1_DP_time= {'10': 0.0002798652648925781,
# '11': 0.0005084526538848877,
# '12': 0.0007184052467346191,
# '13': 0.0015070712566375732,
# '14': 0.002278109788894653, 
# '15': 0.004432696104049683, 
# '16': 0.006098926067352295, 
# '17': 0.012974853515625, 
# '18': 0.01497972846031189, 
# '19': 0.022857216596603395, 
# '20': 0.10202179431915283, 
# '21': 0.10491244077682495, 
# '22': 0.1674989914894104, 
# '23': 0.2043727970123291, 
# '24': 0.49154454708099365, 
# '25': 1.420781329870224, 
# '26': 2.559551054239273, 
# '27': 3.473370096683502, 
# '28': 7.276949617862702}
# record2_Greedy_time_approximate_ratio= {
# '10': (0.00011432766914367675, 1.032083333333333), 
# '11': (0.0001546013355255127, 1.0396428571428566), 
# '12': (0.00012909293174743653, 1.0315416666666664), 
# '13': (0.00018952369689941405, 1.0486349206349201), 
# '14': (0.00017937302589416505, 1.0489940476190474), 
# '15': (0.00017474174499511718, 1.0467996031746027), 
# '16': (0.00018971562385559083, 1.0425892857142853), 
# '17': (0.00022937774658203126, 1.0441112914862911), 
# '18': (0.0002445995807647705, 1.0444960317460317), 
# '19': (0.00018434762954711915, 1.0395265151515154), 
# '20': (0.0002161562442779541, 1.053222222222222), 
# '21': (0.00020480751991271972, 1.0531805555555558), 
# '22': (0.00029929876327514646, 1.0559689754689758), 
# '23': (0.0002839088439941406, 1.0599154595404594), 
# '24': (0.0002734363079071045, 1.0668695887445887), 
# '25': (0.00027927279472351075, 1.0728097041847042), 
# '26': (0.0002846193313598633, 1.076166666666667), 
# '27': (0.0003023242950439453, 1.0754392135642141), 
# '28': (0.00036504626274108887, 1.0789856254856263)}

def N_Mtest():
    record1={}
    record2={}
    AvgRunTimes=200
    for N in range(10,29,2):
        for m in range(int(N/2), int(N*1)):
            print("N size=",N, "M size=", m)
            avgTime1=0.0
            avgTime2=0.0
            avgRatio=0.0
            for _ in range(0,AvgRunTimes):
                S,C=RandomGenerateData2(N,m)
                RuningTimeDp, RightNumber=DpSolver(S,C)
                # RuningTimeGreedy, ApproximateNumber=GreedySolver(S,C)
                RuningTimeGreedy, ApproximateNumber=0,0
                avgTime1+=RuningTimeDp
                avgTime2+=RuningTimeGreedy
                ratio= ApproximateNumber/RightNumber
                avgRatio+=ratio
            avgTime1/=AvgRunTimes
            avgTime2/=AvgRunTimes
            avgRatio/=AvgRunTimes
            key1=str(N)+"-"+str(m)
            record1[key1]=(avgTime1)
            record2[key1]=(avgTime2,avgRatio )
    print("record_DP=",record1) 
    print("record_Greedy=",record2)

#N-M test:
# record_DP= {
# '10-5': 4.004359245300293e-05, '10-6': 7.961392402648926e-05, '10-7': 6.000638008117676e-05, '10-8': 0.00012984514236450196, '10-9': 0.00017947793006896972, 
# '12-6': 2.4974346160888672e-05, '12-7': 6.479501724243164e-05, '12-8': 8.99505615234375e-05, '12-9': 0.00015962719917297363, '12-10': 0.00021934032440185547, '12-11': 0.00035407423973083497, 
# '14-7': 5.51152229309082e-05, '14-8': 5.4824352264404294e-05, '14-9': 0.00013856172561645507, '14-10': 0.00015457510948181153, '14-11': 0.0003290557861328125, '14-12': 0.0005834376811981201, '14-13': 0.000862584114074707, 
# '16-8': 7.482528686523437e-05, '16-9': 0.00012954354286193848, '16-10': 0.0001791083812713623, '16-11': 0.00037958621978759763, '16-12': 0.0007679486274719239, '16-13': 0.001132364273071289, '16-14': 0.001612182855606079, '16-15': 0.004403108358383178, 
# '18-9': 0.0001245427131652832, '18-10': 0.00015946507453918458, '18-11': 0.00025362730026245116, '18-12': 0.0005734515190124512, '18-13': 0.0012667119503021241, '18-14': 0.002493147850036621, '18-15': 0.0034657251834869385, '18-16': 0.004792236089706421, '18-17': 0.007115749120712281, 
# '20-10': 0.0002444052696228027, '20-11': 0.0003887450695037842, '20-12': 0.0007232964038848877, '20-13': 0.0008723866939544677, '20-14': 0.0017399859428405761, '20-15': 0.004836635589599609, '20-16': 0.008786441087722778, '20-17': 0.011097847223281861, '20-18': 0.031089686155319214, '20-19': 0.036355568170547484, 
# '22-11': 0.00033378481864929197, '22-12': 0.00032379746437072754, '22-13': 0.001070934534072876, '22-14': 0.0013019835948944092, '22-15': 0.00236850380897522, '22-16': 0.004494000673294068, '22-17': 0.010028715133666993, '22-18': 0.016087411642074584, '22-19': 0.03583617329597473, '22-20': 0.07778719663619996, '22-21': 0.13958309173583985, 
# '24-12': 0.00033511757850646974, '24-13': 0.0005372810363769531, '24-14': 0.0013167178630828858, '24-15': 0.001271597146987915, '24-16': 0.0029817521572113037, '24-17': 0.007295528650283814, '24-18': 0.00876156210899353, '24-19': 0.027804120779037475, '24-20': 0.05697077035903931, '24-21': 0.056932560205459594, '24-22': 0.1355559241771698, '24-23': 0.21280259013175964, 
# '26-13': 0.000609968900680542, '26-14': 0.001301274299621582, '26-15': 0.002363206148147583, '26-16': 0.006038761138916016, '26-17': 0.010117342472076416, '26-18': 0.02429749011993408, '26-19': 0.041402496099472046, '26-20': 0.12608700394630432, '26-21': 0.13267290472984314, '26-22': 0.26220317244529723, 
# '26-23': 0.5492830598354339, '26-24': 1.1552123892307282, '26-25': 1.127032607793808, 
# '28-14': 0.0009023392200469971, '28-15': 0.0021247148513793947, '28-16': 0.004822062253952026, '28-17': 0.006717536449432373, '28-18': 0.014701269865036011, 
# '28-19': 0.03995298624038696, '28-20': 0.056896317005157473, '28-21': 0.0665033221244812, '28-22': 0.15205081343650817, '28-23': 0.2973851120471954, 
# '28-24': 0.6095074570178985, '28-25': 
# 0.8849427211284637, '28-26': 2.7471520602703094, '28-27': 3.976942117214203}






#TODO:
#1.debug greedy for warehouse_1.0.xlsx  --xiaodong done!
#2.accuracy --xingdi  done!
#2.1: space consumption: Dp=2**n
#3.visualization 

def main():
    """
    docstring
    """
    
    # S, C=loaExcelFile("warehouse_1.0.xlsx")
    # DpSolver(S, C)
    # use_real = 1 #if use real data: use_real=1, else: use_real=0
    # GreedySolver(S, C, use_real)
    N_Mtest()



if __name__ == "__main__":
    main()
