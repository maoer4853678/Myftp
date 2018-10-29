#coding=utf-8
from ftplib import FTP
import os,sys,string,datetime,time
import socket

def debug_print(s):
    print (s)
def deal_error(e):
    logstr = u'发生错误: %s' %e
    debug_print(logstr)
    sys.exit()

class MYFTP:
     def __init__(self, hostaddr= "127.0.0.1", username = "anonymous", password = '', remotedir = './', port=21):
          self.hostaddr = hostaddr
          self.username = username
          self.password = password
          self.remotedir  = remotedir
          self.port     = port
          self.ftp      = FTP()
          self.file_list = []
          self.Bz = False
        
        # self.ftp.set_debuglevel(2)
     def keywords(self,key):
         if key == '':
             self.keys = []
         else:
             self.keys = [i.lower() for i in key.split(",")]

     def includes(self,msg):
         if msg =='':
             self.includewords = []
         else:
             self.includewords = [i.lower() for i in msg.split(",")]

     def excludes(self,msg):
         if msg =='':
             self.excludewords = []
         else:
             self.excludewords = [i.lower() for i in msg.split(",")]
         
     def __del__(self):
          self.ftp.close()
        # self.ftp.set_debuglevel(0)

     def listdirs(self,):
         self.file_list = []
         self.ftp.dir(self.get_file_list)
         remotenames = self.file_list
         print remotenames
         x = []
         for item in remotenames:
             filetype = item[1][:item[1].find(" ")].strip()
             filename = item[1][item[1].find(" ")+1:].strip()
             if filetype.find('DIR')!=-1:
                 x.append(filename)
             
         return x
         
     def filedates(self,tmp):
          lastday = datetime.datetime.strptime(tmp,'%Y%m%d')
          today = datetime.datetime.now()
          Nday = today - lastday
          filedates= []
          for i in range(Nday.days):
               tmp = lastday+datetime.timedelta(days=i)
               filedates.append(tmp.strftime('%Y%m%d')[2:])
          self.filedates = filedates

     def login(self):
          ftp = self.ftp
          try:
               timeout = 1
               socket.setdefaulttimeout(timeout)
               ftp.set_pasv(True)
               ftp.connect(self.hostaddr, self.port)
               ftp.login(self.username, self.password)
          except Exception:
               return(u"连接或登录失败")
          try:
               ftp.cwd(self.remotedir)
               return(u'连接服务器成功')
          except(Exception):
               return(u'切换目录失败')

     def is_same_size(self, localfile, remotefile):
          try:
               remotefile_size = self.ftp.size(remotefile)
          except:
               remotefile_size = -1
          try:
               localfile_size = os.path.getsize(localfile)
          except:
               localfile_size = -1
          if remotefile_size == localfile_size:
               return 1
          else:
               return 0

     def download_file(self, localfile, remotefile,delete = False):
          for i in self.filedates:
               if i in remotefile:
                    if not os.path.exists(localfile):
                         bz = False
                         for key in self.keys:
                             if key in localfile.lower():
                                 bz=True
                         for key in self.includewords:
                             if key not in localfile.lower():
                                 bz=False
                         for key in self.excludewords:
                             if key in localfile.lower():
                                 bz=False
                         if bz:
                             file_handler = open(localfile, 'wb')
                             self.ftp.retrbinary('RETR %s'%(remotefile), file_handler.write)
                             file_handler.close()
                             self.Bz = True
                             debug_print(u'>>>>>>>>>>>>下载文件 %s ... ...' %localfile)
                             if delete:
                                  self.ftp.delete(remotefile)
                             break
        
     def download_files(self, localdir='./', remotedir='./',delete = False):
          try:
               self.ftp.cwd(remotedir)
          except:
               debug_print(u'目录%s不存在，继续...' %remotedir)
               return
          if not os.path.isdir(localdir):
               os.makedirs(localdir)
          debug_print(u'切换至目录 %s' %self.ftp.pwd())
          self.file_list = []
          self.ftp.dir(self.get_file_list)
          remotenames = self.file_list
          for item in remotenames:
               filetype = item[1][:item[1].find(" ")].strip()
               filename = item[1][item[1].find(" ")+1:].strip()
               local = os.path.join(localdir, filename)
               if filetype.find('DIR')!=-1:
                    ## self.download_files(local, filename)\
                    ## 下载到同级目录下
                    self.download_files(localdir, filename,delete)
               else:
                    self.download_file(local, filename,delete)      
          self.ftp.cwd('..')
          debug_print(u'返回上层目录 %s' %self.ftp.pwd())
          
        
     def down_files(self, localdir='./', remotedir='./',delete = False,ftype = 'root',condition = ''):
          rr = False
          try:
               self.ftp.cwd(remotedir)
          except:
               debug_print(u'目录%s不存在，继续...' %remotedir)
               return
          if not os.path.isdir(localdir):
               os.makedirs(localdir)
          debug_print(u'切换至目录 %s' %self.ftp.pwd())
          self.file_list = []
          self.ftp.dir(self.get_file_list)
          remotenames = self.file_list
          for item in remotenames:
               filetype = item[1][:item[1].find(" ")].strip()
               filename = item[1][item[1].find(" ")+1:].strip()
               local = os.path.join(localdir, filename)
               if filetype.find('DIR')!=-1:
                    if ftype == 'root':
                        self.down_files(localdir, filename,delete,ftype,condition)
                    if ftype == 'same':    
                        self.down_files(local, filename,delete,ftype,condition)
##                  self.down_files(localdir, filename)
               else:
                    if self.down_file(local, filename,delete,condition):
                         rr = True         
          self.ftp.cwd('..')
          debug_print(u'返回上层目录 %s' %self.ftp.pwd())
          
          return rr
        
     def down_file(self, localfile, remotefile,delete=False,condition =''):
         rr = False
         if not os.path.exists(localfile) and condition in remotefile:
             file_handler = open(localfile, 'wb')
             self.ftp.retrbinary('RETR %s'%(remotefile), file_handler.write)
             file_handler.close()
             rr = True
             debug_print(u'>>>>>>>>>>>>下载文件 %s ... ...' %localfile)
             if delete:
                 debug_print(u'删除文件 %s ... ...' % remotefile)
                 self.ftp.delete(remotefile)
                 debug_print(u'删除文件 %s 成功' % remotefile)
         return rr
    
     def upload_file(self, localfile, remotefile):
          if not os.path.isfile(localfile):
               return
          if self.is_same_size(localfile, remotefile):
               debug_print(u'跳过[相等]: %s' %localfile)
               return
          file_handler = open(localfile, 'rb')
          self.ftp.storbinary('STOR %s' %remotefile, file_handler)
          file_handler.close()
          debug_print(u'已传送: %s' %localfile)
     def upload_files(self, localdir='./', remotedir = './'):
          if not os.path.isdir(localdir):
               return
          localnames = os.listdir(localdir)
          self.ftp.cwd(remotedir)
          for item in localnames:
               src = os.path.join(localdir, item)
               if os.path.isdir(src):
                    try:
                         self.ftp.mkd(item)
                    except:
                         debug_print(u'目录已存在 %s' %item)
                    self.upload_files(src, item)
               else:
                    self.upload_file(src, item)
          self.ftp.cwd('..')

     def get_file_list(self, line):
          print line
          ret_arr = []
          file_arr = self.get_filename(line)
          if file_arr[1] not in ['.', '..']:
               self.file_list.append(file_arr)
            
     def get_filename(self, line):
          pos = line.rfind(':')
          while(line[pos] != ' '):
               pos += 1
          while(line[pos] == ' '):
               pos += 1
          file_arr = [line[0], line[pos:]]
          return file_arr
