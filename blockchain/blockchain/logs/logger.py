from colorama import init,Fore
import os
import time
init(autoreset=True)
class Logger:
    def __init__(self,dir=None,tick=True):
        self.dir=dir
        self.tick=tick
        self.key={0:'[DEBUG] ',1:'[INFO] ',2:'[WARRING] ',3:'[ERROR] ',4:'[MESSAGE]'}
        self.color={0:Fore.CYAN,1:Fore.GREEN,2:Fore.YELLOW,3:Fore.RED,4:Fore.CYAN}
    def print(self,ty,msg):
        print(self.color[ty]+(self.key[ty]+msg))
        now=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        if self.dir!=None and self.tick==True:
            try:
                if os.path.isfile(self.dir)==False:
                    f=open(self.dir,'w')
                    f.close()
                f=open(self.dir,'a')
                f.write("{} {}: {} \n".format(now,self.key[ty],msg))
                f.close()
            except:
                print("日志保存路径出错")

Log=Logger()


