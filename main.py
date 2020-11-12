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
                intersect=[i for i in RuningLeft if i  in Subsets[option]]#确保不重复选Subset
                if len(intersect)>0:#确保不重复选Subset
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
    print(" Indepent subsets: ", IndepentSets)
    #Select Indepent subsets
    RuningLeft=[ i for i  in TargetSet if i not in IndepentCover] 
    SubsetsLeft={ }
    for (k,v) in Subsets.items() :
        if k not in IndepentSets:
            SubsetsLeft[k]=v
    if len(SubsetsLeft.keys())>100:
        print("*** SubsetsLeft Too long :",len(SubsetsLeft.keys()),"! Dynamic programming fails for high complexity!")

    # while len(RuningLeft)
    else:
        Sk=Dpeqution(RuningLeft,SubsetsLeft,TargetSet)
        time_end=time.time()
        print(Sk+len(IndepentSets))

        #calculate Length  DV   "State":[cost, option]
        
        while Sk!=0:
            option= DV_RESTORE[State2Key(RuningLeft, TargetSet)][1]
            if option==None:
                print(DV_RESTORE[State2Key(RuningLeft, TargetSet)])
            RuningLeft=[it for it in RuningLeft if it not in SubsetsLeft[option]]
            Sk-=1
            IndepentSets.append(option)
        print("Final choice: ", IndepentSets)
        #Check Correctness:
        FinalCover=[]
        for it in IndepentSets:
            FinalCover.extend(Subsets[it])  
        FinalCover=[itm for itm in TargetSet if itm not in FinalCover]
        if len(FinalCover)>0:
            print("Wrong: Elments left behind:", FinalCover)
        else:
            CostTime=(time_end-time_start)
            print("* 通过代码 正确性验证, 耗时 ：",CostTime," s" )


def RandomGenerateData(n):
    m=n
    TestC=[str(t) for t in range(n)]  
    ValidCover=[]
    Subsets={}
    for tm in range(m):
        ID1=random.randint(0,int(n/5))
        Subset=[]
        for _ in range(ID1):
            Subset.append(str(random.randint(0, n)))
        Subsets[str(tm)]=Subset
        ValidCover.extend(Subset)
    Left=[it for it in TestC if it not in ValidCover]
    if len(Left )>=1:
        for item in Left:
            ID1=random.randint(0,m-1)
            ID2=random.randint(0,m-1)
            Subsets[str(ID1)]=Subsets[str(ID1)]+ [item]
            Subsets[str(ID2)]=Subsets[str(ID2)]+ [item]
    return Subsets,TestC


def main():
    """
    docstring
    """
    # S,C= loaExcelFile("工作簿1.xlsx")

    S,C=RandomGenerateData(28)

    # print("Input: C=",C) 
    # print("Input: S=", S)
    DpSolver(S,C)





if __name__ == "__main__":
    main()