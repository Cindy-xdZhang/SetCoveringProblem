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
    # print(states_order)
    return CostTime,len(states_order )




def AverageRunningTest():
    record1={}
    record2={}
    AvgRunTimes=200
    for comple in range(10,29):
        avgTime1=0.0
        avgTime2=0.0
        avgSE1=0.0
        avgSE2=0.0
        avgAccuracy=0.0
        print("Testing size=",comple)
        for _ in range(0,AvgRunTimes):
            S,C=RandomGenerateData(comple)
            RuningTimeDp, RightNumber=DpSolver(S,C)
            RuningTimeGreedy, ApproximateNumber=GreedySolver(S,C)
            avgTime1+=RuningTimeDp
            avgTime2+=RuningTimeGreedy
            Accuracy= RightNumber/ApproximateNumber
            InverseAccuracy= ApproximateNumber/RightNumber
            avgSE1+= (comple**2)  /  (RuningTimeDp+0.00000001 )  
            avgSE2+= (comple**2) /(  (RuningTimeGreedy+0.00000001)  *InverseAccuracy  )
            avgAccuracy+=Accuracy

        avgTime1/=AvgRunTimes
        avgTime2/=AvgRunTimes
        avgSE1/=AvgRunTimes
        avgSE2/=AvgRunTimes
        avgAccuracy/=AvgRunTimes
        record1[str(comple)]=(avgTime1, avgSE1  )
        record2[str(comple)]=(avgTime2,  avgSE2,avgAccuracy )
    print("record1=",record1) 
    print("record2=",record2)


# record1= {'10': (0.0003242814540863037, 7450023399.126878), 
# '11': (0.0005717360973358154, 7744037279.259804),
# '12': (0.0007928860187530518, 8784045783.00335), 
# '13': (0.0010219323635101319, 8450065582.662675),
# '14': (0.0022614741325378417, 7840076414.879299),
# '15': (0.004429367780685425, 5962585516.532829),
# '16': (0.009631952047348022, 6016079878.676352),
# '17': (0.014117741584777832, 3757107207.991474), 
# '18': (0.016532138586044312, 2916109196.6533875), 
# '19': (0.030278210639953614, 3068613798.301462), 
# '20': (0.10232037901878357, 2000084372.3522112), 
# '21': (0.1247658932209015, 1323068887.2965524), 
# '22': (0.25415498614311216, 1210059551.4195554), 
# '23': (0.2914220988750458, 264550705.09451005), 
# '24': (0.3958284175395966, 288052169.38737494), 
# '25': (1.4171453988552094, 312519523.0680994), 
# '26': (2.476246106624603, 27339.094657406124), 
# '27': (4.403908573389053, 16283.637658536323), 
# '28': (9.713156042098999, 9959.45755737888)}
# record2= {'10': (0.00017451882362365723, 7943588415.665187, 0.963761904761905), 
# '11': (0.00015131235122680664, 9843993068.61374, 0.9627777777777783), 
# '12': (0.00017440319061279297, 11509110469.133291, 0.9705515873015872), 
# '13': (0.00019459724426269532, 13228239022.60723, 0.9733194444444446), 
# '14': (0.00020470619201660157, 15004694511.905525, 0.963988095238095), 
# '15': (0.00024850130081176757, 16136036189.242273, 0.955886904761905), 
# '16': (0.0001944255828857422,  19819726026.414364, 0.9615613275613275), 
# '17': (0.0002492415904998779,  20875503076.99559, 0.9629204545454542), 
# '18': (0.00019458293914794922, 25051234194.79037, 0.9624936868686871), 
# '19': (0.00019414663314819335, 27899577697.731613, 0.956122474747475), 
# '20': (0.00022948384284973144, 29416566626.928177, 0.9537983405483405), 
# '21': (0.00022933721542358398, 32128714565.502777, 0.9446651126651127), 
# '22': (0.00021181464195251464, 36097639010.407234, 0.9481893939393938), 
# '23': (0.00022439837455749513, 39194256138.114784, 0.9555590520590523), 
# '24': (0.00031428217887878416, 37271075169.610985, 0.9444188034188032), 
# '25': (0.000273897647857666,   42394417710.81345,  0.9374911616161614), 
# '26': (0.0003091251850128174,  43508992746.434456,  0.9368545066045069), 
# '27': (0.0003023505210876465,  47702023100.4177,    0.9402469474969477), 
# '28': (0.0003293895721435547,  49149315848.76754, 0.9314894827394825)}



#TODO:
#1.debug greedy for warehouse_1.0.xlsx  --xiaodong done!
#2.accuracy --xingdi  
#3.visualization 

def main():
    """
    docstring
    """
    
    # S, C=loaExcelFile("warehouse_1.0.xlsx")
    # DpSolver(S, C)
    # use_real = 1 #if use real data: use_real=1, else: use_real=0
    # GreedySolver(S, C, use_real)
    AverageRunningTest()



if __name__ == "__main__":
    main()
