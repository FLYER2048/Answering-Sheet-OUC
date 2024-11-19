from PIL import Image
import os
import csv
import matplotlib.pyplot as plt

black_degree=180#判断已填涂的灰度值上限
black_rate=0.64#判断区域填涂有效的下限比率

def is_image_file(filename):
    return filename.split(".")[-1].lower() in ["jpg","png","bmp"]

def splitMark(x1r,x2r,y1r,y2r):
    x1,x2,y1,y2=int(x1r*width+0.5),int(x2r*width+0.5),int(y1r*height+0.5),int(y2r*height+0.5)
    for x in range(x1,x2+1):
        pic.putpixel((x,y1),(0,0,255))
        pic.putpixel((x,y2),(0,0,255))
    for y in range(y1+1,y2):
        pic.putpixel((x1,y),(0,0,255))
        pic.putpixel((x2,y),(0,0,255))

def splitMarkOPos(x1op,x2op,y1op,y2op):
    x1,x2,y1,y2=(int((x1op-15)/100*width)),int(((x2op-15)/100*width)),int(((y1op-15)/150*height)),int(((y2op-15)/150*height))
    for x in range(x1,x2+1):
        pic.putpixel((x,y1),(0,0,255))
        pic.putpixel((x,y2),(0,0,255))
    for y in range(y1+1,y2):
        pic.putpixel((x1,y),(0,0,255))
        pic.putpixel((x2,y),(0,0,255))

# 根据输入的RGB色值判断该点是否为黑
def isBlack(R,G,B):
    grey_degree=0.299*R+0.587*G+0.114*B
    if grey_degree<black_degree:
        return True
    else:
        return False

def isFilled(x1op,x2op,y1op,y2op):# 判定有效填涂，注意输入的位置都是基于带留空部分的文档的、从左上角起算的、以毫米为单位的相对位置
    x1,x2,y1,y2=(int((x1op-15)/100*width)),int(((x2op-15)/100*width)),int(((y1op-15)/150*height)),int(((y2op-15)/150*height))
    cnt=0#黑色像素计数器
    for x in range(x1,x2+1):
        for y in range(y1,y2+1):
            R,G,B=pic.getpixel((x,y))[:3]
            if isBlack(R,G,B):
                cnt+=1
    # print("({},{}):{:.1f}%".format(x1,y1,cnt/(x2-x1+1)/(y2-y1+1)*100),end="\t")#调试用，输出填涂可信度表
    if cnt>=(x2-x1+1)*(y2-y1+1)*black_rate: #调试用，标注填涂有效性
        for x in range((x1*3+x2)//4,(x1+x2*3)//4+1):
            for y in range((y1*3+y2)//4,(y1+y2*3)//4+1):
                pic.putpixel((x,y),(0,255,0))
    return cnt>=(x2-x1+1)*(y2-y1+1)*black_rate
### 寻找标志圆

def is_very_black(x,y):
    # 绝对位置x,y-->判断是不是黑色像素（判断的标准严于填涂像素）
    R,G,B=pix[x,y][:3]
    grey_degree=0.299*R+0.587*G+0.114*B
    return grey_degree<100

def is_four_sides_black(x,y,r):# 从上下左右四个方向上取样
    # 绝对位置x,y,偏移量r
    return is_very_black(x+r,y) and is_very_black(x,y+r) and is_very_black(x-r,y) and is_very_black(x,y-r)

def find_largest_circle_radius(x,y):
    r=1
    try:
        while is_four_sides_black(x,y,r):
            r+=1
    except IndexError:
        return r-1
    else:
        return r

def find_3_marks():
    global max_r
    # 第一标志块
    max_r=[1,0,0]# 第0位是最大的半径，第1、2位是最大半径下对应的坐标
    for u in range(0,int(height*0.3)):
        for v in range(0,u+1):
            y=u-v
            x=v
            rr=find_largest_circle_radius(x,y)
            if max_r[0]<=rr:
                max_r=[rr,x,y]
    pos1=max_r[1:]

    # 第二标志块
    max_r=[1,0,0]# 第0位是最大的半径，第1、2位是最大半径下对应的坐标
    for u in range(0,int(height*0.3)):
        for v in range(0,u+1):
            y=u-v
            x=width-2-v
            rr=find_largest_circle_radius(x,y)
            if max_r[0]<=rr:
                max_r=[rr,x,y]
    pos2=max_r[1:]

    # 第三标志块
    max_r=[1,0,0]# 第0位是最大的半径，第1、2位是最大半径下对应的坐标
    for u in range(0,int(height*0.3)):
        for v in range(0,u+1):
            y=height-2-u+v
            x=v
            rr=find_largest_circle_radius(x,y)
            if max_r[0]<=rr:
                max_r=[rr,x,y]
    pos3=max_r[1:]

    # 第四标志块
    max_r=[1,0,0]# 第0位是最大的半径，第1、2位是最大半径下对应的坐标
    for u in range(0,int(height*0.3)):
        for v in range(0,u+1):
            y=height-2-u+v
            x=width-2-v
            rr=find_largest_circle_radius(x,y)
            if max_r[0]<=rr:
                max_r=[rr,x,y]

    pos4=max_r[1:]
    return(pos1,pos2,pos3,pos4)

def find_mark(path,filename):
    global width,height,pix,pic
    pic=Image.open(path+"\\images\\"+filename)
    pix=pic.load()
    width=pic.size[0]
    height=pic.size[1]

    return(find_3_marks())

def mark_blocks(path,filename):# 一级函数
    filled_ans={}
    zkzh=["" for i in range(12)]
    global width,height,pix,pic
    pic=Image.open(path+"\\transformed\\"+filename)
    pix=pic.load
    width=pic.size[0]
    height=pic.size[1]
    splitMarkOPos(35.14,38.86,48.24,49.88)#缺考标记
    if isFilled(35.14,38.86,48.24,49.88):
        print("缺考")
        return(None)

    splitMarkOPos(55,110,40,70)#准考证号
    for x in range(11):#11位准考证号
        for y in range(10):
            splitMarkOPos(55.64+5*x,59.36+5*x,40.64+3.01*y,42.27+3.01*y)
            if isFilled(55.64+5*x,59.36+5*x,40.64+3.01*y,42.27+3.01*y):
                if zkzh[x]=="":
                    zkzh[x]=str(y)
                else:
                    zkzh="Error!"
                    # return("Error!")
                    break
        else:
            continue
        break

    print("准考证号："+"".join(zkzh))
    filled_ans[0]="".join(zkzh)
    # 80*4选项
    for I in range(4):
        for J in range(4):
            for i in range(5):
                for j in range(4):
                    splitMarkOPos(16.71+i*4.50+J*25,20.36+i*4.50+J*25,80.29+j*2.983+I*21,81.85+j*2.983+I*21)
                    if isFilled(16.71+i*4.50+J*25,20.36+i*4.50+J*25,80.29+j*2.983+I*21,81.85+j*2.983+I*21):
                        # print("T{}:{}".format(I*20+J*5+i+1,chr(j+65)))
                        filled_ans[I*20+J*5+i+1]=filled_ans.get(I*20+J*5+i+1,"")+chr(j+65)

    pic.save(path+"\\marked\\Marked_"+filename)
    return(filled_ans)

def transforms_2D(path,filename,pos):# 一级函数
    (x1,y1),(x2,y2),(x3,y3),(x4,y4)=pos
    # x4,y4=-x1+x2+x3,-y1+y2+y3
    imtra=pic.transform((100*5,150*5),Image.QUAD,(x1,y1,x3,y3,x4,y4,x2,y2))
    imtra.save(path+"\\transformed\\"+filename)

def Distinguish():
    project_path=os.path.dirname(__file__)
    files=list(os.walk(project_path+"\\images"))[0][2]

    ANS={}
    for filecnt,file in enumerate(files):
        if is_image_file(file):
            print("正在识别：{}\t第{}份/共{}份".format(file,filecnt+1,len(files)))
            
            #第一模块 答题卡的识别
            pos=find_mark(project_path,file)# 寻找3个边角定位圆的位置
            transforms_2D(project_path,file,pos)# 进行透视变换，保存在transformed目录下
            ans=mark_blocks(project_path,file)# 识别填涂状态并输出，图片保存在marked目录下
            if ans!=None:
                ANS[ans[0]]=ans# 存进二维答案字典中

        else:
            print(file+"\tInvalid file format:")
    # print(ANS)
    return ANS
    # print("有效扫描{}份".format(len(files)))


def Assess(ANS):
    TrueKey=ANS.get("00000000000",{})# 获取标准答案的子字典
    Q_nums=list(TrueKey.keys())[1:]# 取到标答里所有有填涂的答案的题号
    AS={}
    TruePoints=ANS.get("99999999999",{})# 获取标准答案的子字典
    point={i:2 for i in Q_nums}# 每道题的分数权值，默认每题2分
    for i,j in list(TruePoints.items())[1:]:
        point[i]=sum([0.5*2**(ord(j0)-65) for j0 in j])

    for key,value in ANS.items():
        son_dic=value
        if son_dic[0] in ["00000000000","99999999999"]:
            continue
        son_dic2={0:son_dic[0]}
        total_point=0
        for i in Q_nums:
            if son_dic.get(i,"")==TrueKey[i]:
                son_dic2[i]=point[i]
                total_point+=point[i]
            elif son_dic.get(i,"") in TrueKey[i] and son_dic.get(i,"")!="":
                son_dic2[i]=point[i]//2
                total_point+=point[i]//2
            else:
                son_dic2[i]=0
        son_dic2["total"]=total_point
        AS[son_dic[0]]=son_dic2
    # print(AS)
    return(AS)

def Analyse(ANS,AS):
    selection={}
    selections={}
    TrueKey=ANS.get("00000000000","")# 获取标准答案的子字典
    Q_nums=list(TrueKey.keys())[1:]# 取到标答里所有有填涂的答案的题号
    mark={}#每個人的字典被裝在列表裡
    for i in AS.values():
        mark[i[0]]=[i.get("total",0)]
    # mark1=mark.values()
    stu_cnt=len(ANS)-2

    Options_Counts={i:[0,0,0,0] for i in Q_nums}
    # print(Options_Counts)
    for key,value in ANS.items():
        son_dic=value
        if son_dic[0] in ["00000000000","99999999999"]:
            continue
        for i in Q_nums:
            option=son_dic.get(i,"")
            for j in option:
                Options_Counts[i][ord(j)-65]+=1

    for i in Options_Counts.values():
        for j in range(4):
            # i[j]=str(i[j])+"__"+str(i[j]*100//stu_cnt)+"%"
            i.append(str(i[j]*100//stu_cnt)+"%")

       

#均值
    c=0     
    k=0 
    for i in mark.values():
        c+=1
        k+=i[0]
    junzhi=k/c

    for i in mark.values():
        cnt=1
        for j in mark.values():
            if j[0]>i[0]:
                cnt+=1
        i.append(cnt)

    return Options_Counts,mark,junzhi

# def draw(Q_n,Y):
#     plt.rcParams["font.sans-serif"] = ["SimHei"]  # 添加这条可以让图形显示中文
#     plt.title("单题选项分布柱状图(第{}题)".format(Q_n))   # 图片标题
#     plt.style.use("ggplot")     # 设置图形的显示风格
#     plt.xlabel("Choices选项")      # 设置 x 轴名字
#     plt.ylabel("Number人数")      # 设置 y 轴名字
#     X=["A","B","C","D"] # x 轴单位名称
#     plt.bar(X,Y,color="c")
#     print(Y)
#     plt.savefig(os.path.dirname(__file__)+'\\题'+str(Q_n)+'.jpg')
#     plt.close()


def DrawGraph(ANA):
    print("正在输出图表……")
    for key,value in ANA[0].items():
        # draw(key,value[0:4])
        Q_n,Y=key,value[0:4]
        plt.rcParams["font.sans-serif"] = ["SimHei"]  # 添加这条可以让图形显示中文
        plt.title("单题选项分布柱状图(第{}题)".format(Q_n))   # 图片标题
        # plt.style.use("ggplot")     # 设置图形的显示风格
        plt.xlabel("Choices选项")      # 设置 x 轴名字
        plt.ylabel("Number人数")      # 设置 y 轴名字
        X=["A","B","C","D"] # x 轴单位名称
        plt.bar(X,Y,color="c")
        plt.savefig(os.path.dirname(__file__)+'\\output\\题'+str(Q_n)+'.jpg')
        plt.close()



def PrintTable(ANS,AS,ANA):
    print("正在输出csv表格……")
    Q_nums=list(ANS.get("00000000000",{}).keys())[1:]
    header1 = ["准考证号","总分","排名",*["题"+str(i) for i in Q_nums]]
    header2 = ["题号",*["选"+chr(i)+j for j in ["人数","比例"] for i in range(65,69)]]
    #这里指的是给出的二元字典格式的最终输出数据
    data1 = [] #原始选项
    data1_0=[] #小题分数
    data2 = [] #选项统计

    for i in ANS.values():
        zkzh=i.get(0,"")
        if zkzh in ["00000000000","99999999999"]:
            continue
        s1 = ["'"+zkzh,*ANA[1][zkzh]]
        s2 = ["'"+zkzh,*ANA[1][zkzh]]
        for j in Q_nums:
            s1.append(i.get(j,""))
            s2.append(AS.get(zkzh,{}).get(j,""))
        data1.append(s1)
        data1_0.append(s2)

    for key,value in ANA[0].items():
        data2.append(["题"+str(key),*value])
    

    with open(os.path.dirname(__file__)+'\\output\\score.csv', 'w', encoding='UTF-8', newline='') as SYC:
    #这里用的‘utf-8’是一个包含了ASCII的一个可变的字符编码，用于防止出现汉字bug
    #这里的newline是为了防止出现空行，但是为什么出现空行这件事情我还不是很清楚
        writer = csv.writer(SYC)
    #第一行标题
        writer.writerow(["【学生作答情况报表】"])
        writer.writerow(header1)
        writer.writerows(data1)
        writer.writerow(["全体平均",ANA[2]])

        writer.writerows([''] for i in range(5))

        writer.writerow(["【学生得分情况报表】"])
        writer.writerow(header1)
        writer.writerows(data1_0)
        writer.writerow(["全体平均",ANA[2]])

        writer.writerows([''] for i in range(5))

        writer.writerow(["【选项分析报表】"])
        writer.writerow(header2)
        writer.writerows(data2)
        