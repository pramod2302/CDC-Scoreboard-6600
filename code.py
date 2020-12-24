import re

config=[["INTEGER","DATA"],[1,1],[1,1]]
unit_busy=[[],[]]
branch=-1
decoded_inst=[]
fetch_q=[]
issue_q=[]
read_q=[]
exec_q=[]
write_q=[]
reg_busy=[[],[]]
scoreboard=[[0 for _ in range(36)]for _ in range(9) ]
dest_l=["SW","S.D"]
curr_inst = 0
iteration=0
cacheflag=0
stallvar=0
reg_var={}
max_iterations=1
cachecycle=curr_inst
dirtybit=[[0,0],[0,0]]
ia=0
ih=0
da=0
dh=0

def read_config():
    file_name = "config.txt"
    f = open(file_name, "r")
    l = f.read()
    l = l.split("\n")
    data = []
    for i in range(len(l)):
        l[i] = l[i].strip()
        a=re.split(": |,",l[i])
        config[0].append(a[0].upper())
        config[1].append(int(a[1]))
        config[2].append(int(a[2]))

    for i in range(len(config[0])):
        unit_busy[0].append(config[0][i].upper())
        unit_busy[1].append(config[1][i])

    print("config ",config)
    print("unit ",unit_busy)


def read_data():
      file_name = "data.txt"
      f = open(file_name, "r")
      l = f.read()
      #l=uploaded[file_name].decode("utf-8")
      l=l.split("\n")
      data=[]
      for i in range(len(l)):
        l[i]=l[i].strip()
        data.append(binaryToDecimal(int(l[i])))

      print("data ", data)



def read_inst():
      global branch,decoded_inst
      file_name = "inst.txt"
      f = open(file_name, "r")
      l=f.read()
      #l=uploaded[file_name].decode("utf-8")
      l=l.split("\n")
      print(l)
      while l[-1]=='':
          l.pop()
      for i in range(len(l)):
            decoded_inst.append(l[i].strip().split())

            #fetch_q.append(i)
      removecomma()
      for i in range(len(decoded_inst)):
              unit=find_unit(decoded_inst[i][0])
              if decoded_inst[i][0]=='LI':
                  reg_var[decoded_inst[i][1]]=int(decoded_inst[i][2])
              if unit=="":
                  decoded_inst[i].pop(0)
                  branch=i
                  break
      x=decoded_inst.pop()
      ll=decoded_inst[branch:]
      for i in range(max_iterations):
        decoded_inst+=ll
      decoded_inst+=[x]
      print("decoded inst ", decoded_inst)



def binaryToDecimal(binary):
        binary1 = binary
        decimal, i, n = 0, 0, 0
        while (binary != 0):
            dec = binary % 10
            decimal = decimal + dec * pow(2, i)
            binary = binary // 10
            i += 1
        return (decimal)


def fetch():

    global curr_inst,hlt_flag,iteration,cachecycle

    if curr_inst==-1:
        return -1
    print(curr_inst,(decoded_inst[curr_inst]))
    unit=find_unit(decoded_inst[curr_inst][0])

    if unit=="HLT" :
            cachecycle=branch
            return curr_inst




    if len(issue_q)!=0:
        return -1

    if len(read_q)!=0:
        unit1 = find_unit(decoded_inst[read_q[0]][0])
        if unit1=="BNE":
            return -1
    issue_q.append(curr_inst)
    return curr_inst



def find_unit(val):
    unit = ""
    int1=["DADD","DADDI","DSUB","DSUBI","AND","ANDI","OR","ORI","LI","LUI"]
    add1=["ADD.D","SUB.D"]
    mul1=["MUL.D"]
    div1=["DIV.D"]
    data1=["L.D","S.D","LW","SW"]

    if val.upper() in int1:
        unit="INTEGER"
    elif val.upper() in add1:
        unit="FP ADDER"
    elif val.upper() in mul1:
        unit="FP MULTIPLIER"
    elif val.upper() in div1:
        unit="FP DIVIDER"
    elif val.upper() in data1:
        unit="DATA"
    elif val.upper() == "BNE":
        unit="BNE"
    elif val.upper() == "HLT":
        unit="HLT"
    return unit

def if_reg_free(r1,a):
    if r1 not in reg_busy[0]:
        return True
    if r1 in reg_busy[0] and a<reg_busy[1][reg_busy[0].index(r1)]:
        return True
    return False

hlt_flag=0
def hlt():
    global decoded_inst, hlt_flag,iteration
    if hlt_flag==0 and iteration==0:
        hlt_flag=1
        iteration=1
        #curr_inst+=1
    return


def issue():
    flag=0
    if len(issue_q)==0:
        return -1
    a=issue_q[0]
    print("issue stage.........",decoded_inst[a])
    unit=find_unit(decoded_inst[a][0])

    if unit == "BNE":
        issue_q.pop(0)
        read_q.append(a)
        return a
    if decoded_inst[a][0].upper() in dest_l:
        dest = decoded_inst[a][2]
    else:
        dest=decoded_inst[a][1]
    if dest in reg_busy[0]:
        scoreboard[7][a]='Y'
        flag=1


    if unit_busy[1][unit_busy[0].index(unit)]>0:
        if flag==1:
            return -1
        unit_busy[1][unit_busy[0].index(unit)] -= 1
        issue_q.pop(0)
        read_q.append(a)
        dest=""

        return a
    else:
        scoreboard[8][a]='Y'
        return -1


def read1():
    if len(read_q)==0:
        return -1
    for a in read_q:
        print(decoded_inst[a],".............. read stage")
        unit=find_unit(decoded_inst[a][0])
        r1=decoded_inst[a][1]
        r2=decoded_inst[a][2]
        r3=""
        if len(decoded_inst[a])==4:
            r3=decoded_inst[a][3]
        if if_reg_free(r1,a) and if_reg_free(r2,a) and if_reg_free(r3,a):
            if unit!="BNE":
                exec_q.append(a)
                if decoded_inst[a][0].upper() in dest_l:
                    dest = decoded_inst[a][len(decoded_inst[a])-1]
                else:
                    dest = decoded_inst[a][1]
                reg_busy[0].append(dest)
                reg_busy[1].append(a)
            read_q.pop(read_q.index(a))
            return a
        else:
            scoreboard[6][a]='Y'
    return -1

dcache=[[],[]]
dcache_flag=0
icache_flag=0
def dcache2(a):

    global dcache_flag,da,dh
    da += 1
    val= decoded_inst[a][2]
    val=(val.split('('))
    reg=val[1].strip(')')
    val=int(val[0])
    c1=reg_var[reg]+val
    c2=c1+4
    ind1=int(c1/16)
    ind2=int(c2/16)
    lat=0
    print(c1,c2,ind1,ind2,dcache," dcacheee ................................. ")
    if decoded_inst[a][0]=='L.D' or decoded_inst[a][0]=='S.D':
        lat=2
    elif decoded_inst[a][0]=='LW' or decoded_inst[a][0]=='SW':
        lat=1
    if ind1 not in dcache[ind1%2]:

        if len(dcache[ind1%2])<2:
            dcache[ind1%2].append(ind1)
        else:
            if dirtybit[ind1%2][0]=='D':
                lat+=12
            dirtybit[ind1 % 2][0]=0
            dcache[ind1%2].pop(0)
            dcache[ind1%2].append(ind1)
        dcache_flag=1
        lat=lat+12
        return lat
    if ind1 in dcache[ind1%2]:
        dh+=1
        if decoded_inst[a][0]=='S.D' or decoded_inst[a][0]=='SW' :
            dirtybit[ind1%2][dcache[ind1%2].index(ind1)]='D'

        if ind1==dcache[ind1%2][0] and len(dcache[ind1%2])==2:
            dcache[ind1%2][0],dcache[ind1%2][1]=dcache[ind1%2][1],dcache[ind1%2][0]
            dirtybit[ind1 % 2][0], dirtybit[ind1 % 2][1] = dirtybit[ind1 % 2][1], dirtybit[ind1 % 2][0]
    if ind2 not in dcache[ind2 % 2]:

        if len(dcache[ind2 % 2]) < 2:
            dcache[ind2 % 2].append(ind2)
        else:
            if dirtybit[ind2%2][0]=='D':
                lat+=12
            dirtybit[ind2 % 2][0]=0
            dcache[ind2 % 2].pop(0)
            dcache[ind2 % 2].append(ind2)
        lat = lat + 12
        dcache_flag=1
    if ind2 in dcache[ind2%2]:
        dh+=1
        if decoded_inst[a][0]=='S.D' or decoded_inst[a][0]=='SW' :
            dirtybit[ind2%2][dcache[ind2%2].index(ind2)]='D'
        if ind2==dcache[ind2%2][0] and len(dcache[ind2%2])==2:
            dcache[ind2%2][0],dcache[ind2%2][1]=dcache[ind2%2][1],dcache[ind2%2][0]
            dirtybit[ind2 % 2][0],dirtybit[ind2 % 2][1]=dirtybit[ind2 % 2][1],dirtybit[ind2 % 2][0]
    print(lat)
    return lat





latency=[0 for _ in range(10)]
def exe(cc):
    global dcache_flag ,latency
    if len(exec_q)==0:
        return -1
    for a in range(len(exec_q)):
        print("exec inst.................................",decoded_inst[exec_q[a]])
        unit=find_unit(decoded_inst[exec_q[a]][0])
        if unit=="BNE":
            latency[a]=1
        elif unit=="DATA":
            #if decoded_inst[a][0]=="L.D" or decoded_inst[a][0]=="S.D":
                 if dcache_flag==0:
                    latency[a]=dcache2(exec_q[a])+stallvar

        else:
            latency[a]= config[2][config[0].index(unit)]
        print(scoreboard[3][exec_q[a]],latency[a],cc,"...................................... exec stage")
        if scoreboard[3][exec_q[a]]+latency[a]<=cc:
            latency[a]=0
            if unit!="BNE":
                write_q.append(exec_q[a])
            re=exec_q.pop(a)

            return re
    return -1

def writeb():
    if len(write_q)==0:
        return -1
    a=write_q[0]

    write_q.pop(0)
    return a

def cachecheck():
    global ia,ih
    ia+=1
    if icache[int(cachecycle/len(icache))%len(icache)]!=int(cachecycle/len(icache)):

        return len(icache)*3
    else:
        ih+=1
        return 0

def simulate():
    global curr_inst,cacheflag,stallvar,dcache_flag,cachecycle

    for clock_cycle in range(1,300):


        print(clock_cycle," SCOREBOARD-------------------------------------------",curr_inst,decoded_inst[curr_inst])

        print(" unit busy .... ", unit_busy)
        print(" issue q .... ", issue_q)
        print(" read q .... ", read_q)
        print(" exec q .... ", exec_q)
        print("reg_busy ... ", reg_busy)
        print("write_q .... ", write_q)
        print(icache, stallvar,cacheflag,"................. icache",int(cachecycle/len(icache)))
        print( dcache, " dcacheee ................................. ")
        print("Dirty bit",dirtybit)
        print("reg_var.......",reg_var)
        for i in range(len(scoreboard[0])):
            for j in range(len(scoreboard)):
                print(scoreboard[j][i], "  ", end='')
            print("")


        flag=writeb()
        if flag!=-1:
            scoreboard[5][flag]=(clock_cycle)

        exe_var=exe(clock_cycle)
        if exe_var!=-1:
            if decoded_inst[exe_var][0]=='DADDI':
                print(reg_var[decoded_inst[exe_var][1]])
                reg_var[decoded_inst[exe_var][1]] += int(decoded_inst[exe_var][3])
            if dcache_flag!=0 and (decoded_inst[exe_var][0]=='L.D' or decoded_inst[exe_var][0]=='S.D'):
                dcache_flag=0
            scoreboard[4][exe_var]=(clock_cycle)

        read_var = read1()
        if read_var!=-1:
            scoreboard[3][read_var]=(clock_cycle)
            if find_unit(decoded_inst[read_var][0]) == "BNE":
                if stallvar>0:
                    stallvar-=1
                continue

        issue_var=issue()
        if issue_var!=-1:
            scoreboard[2][issue_var]=(clock_cycle)

        #unit1=find_unit(decoded_inst[issue_q[0]][0])

        if cacheflag==0:
            cacheflag=cachecheck()
            stallvar=cacheflag

        if stallvar!=0:
            icache_flag=1
            stallvar-=1
            if flag != -1:
                unit = find_unit(decoded_inst[flag][0])
                if unit == "HLT" or unit == "BNE":
                    continue
                unit_busy[1][unit_busy[0].index(unit)] += 1
                dest = ""
                if decoded_inst[flag][0].upper() in dest_l:
                    dest = decoded_inst[flag][len(decoded_inst[flag]) - 1]
                else:
                    dest = decoded_inst[flag][1]
                reg_busy[1].pop(reg_busy[0].index(dest))
                reg_busy[0].pop(reg_busy[0].index(dest))

            continue

        if cacheflag>0 and stallvar==0:
            cacheflag=0
            icache_flag=0
            icache[int(cachecycle/len(icache))%len(icache)]=int(cachecycle/len(icache))
        print("cache.............................................",cacheflag,stallvar,cachecycle)
        fetch_var=fetch()
        if fetch_var!=-1:
            scoreboard[0][fetch_var]=(" ".join(decoded_inst[fetch_var]))
            scoreboard[1][fetch_var]=(clock_cycle)
            curr_inst+=1
            cachecycle+=1

        if flag!=-1:
            unit = find_unit(decoded_inst[flag][0])
            if unit=="HLT" or unit=="BNE":
                continue
            unit_busy[1][unit_busy[0].index(unit)] += 1
            dest = ""
            if decoded_inst[flag][0].upper() in dest_l:
                dest = decoded_inst[flag][len(decoded_inst[flag]) - 1]
            else:
                dest = decoded_inst[flag][1]
            reg_busy[1].pop(reg_busy[0].index(dest))
            reg_busy[0].pop(reg_busy[0].index(dest))
        if curr_inst==-1 and len(issue_q)==0 and len(read_q)==0 and len(exec_q)==0:
            break
        if curr_inst==len(decoded_inst):
            curr_inst=-1


def removecomma():
    print(decoded_inst)
    for i in range(len(decoded_inst)):
        for j in range(len(decoded_inst[i])):
            decoded_inst[i][j]=decoded_inst[i][j].replace(",","")

def hazard():
    for i in range (len(scoreboard)):
        for j in range(len(scoreboard[i])):
            if i>=6:
                scoreboard[i][j]='N'

#
icache=[]
def icache2():
    global config, icache
    icache = [-1 for i in range(config[1][config[0].index('I-CACHE')])]
    print(icache)


def print_file():

    f = open("results.txt", "w")
    f.write("Instruction\tFetch\tIssue\tRead\tExecute\tWrite Back\tRAW\tWAW\tStruct\n")
    for i in range(len(scoreboard[0])):
        for j in range(len(scoreboard)):
            if j==6:
                f.write(str("\t"))
            f.write(str(scoreboard[j][i])+"\t")
        f.write('\n')
    f.close()
def main():
    read_config()
    read_data()
    read_inst()
    #removecomma()
    icache2()
    hazard()
    simulate()
    print(ia,ih,da,dh)
    print_file()

main()