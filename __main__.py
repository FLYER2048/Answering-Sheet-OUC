import time
from __function__ import * 

start_time=time.time()

# 第一模块
ANS=Distinguish()
# 第二模块：判分
AS=Assess(ANS)
# 第三模块：分析成绩
ANA=Analyse(ANS,AS)
# 第四模块：输出图表
DrawGraph(ANA)
# 第五模块：输出csv
PrintTable(ANS,AS,ANA)

end_time=time.time()
print("运行时间：{:.2f}ms".format((end_time-start_time)*1000))