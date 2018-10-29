# coding=utf-8
from ftplib import FTP
import os
import socket


def get_dir(dirname):
    dirs = []
    a, b = os.path.split(dirname)
    dirs.append(dirname)
    if a in ['', '/', '.']:
        return dirs
    else:
        dirs.extend(get_dir(a))
    return dirs


def diff_path(path1, path2):
    # path1 为子路径
    # path2 为父路径
    temp = os.path.realpath(path1)
    temp1 = os.path.realpath(path2)
    path = temp.replace(temp1, '').replace("\\", "/")[1:]
    return path


def check_filename(filename, include, exclude):
    # include 条件之间是 或关系 , 即满足任一 include条件均可
    # exclude 条件之间是 或关系 , 即满足任一 exclude条件均不可
    # include 和 exclude 之间是 与关系
    if isinstance(include, unicode) or isinstance(include, str):
        include = [include]
    elif not include:
        include = ['']
    if isinstance(exclude, unicode) or isinstance(exclude, str):
        exclude = [exclude]
    elif not exclude:
        exclude = []

    temp = False
    for i in include:
        if i in filename:
            temp = True
            break

    if not temp:
        return False

    for i in exclude:
        if i in filename:
            temp = False
            break
    return temp


class MYFTP:
    def __init__(
            self,
            hostaddr="127.0.0.1",
            username="anonymous",
            password='',
            remotedir='./',
            port=21):
        self.hostaddr = hostaddr
        self.username = username
        self.password = password
        self.port = port
        self.ftp = FTP()
        self.file_list = []
        self.localdir = os.getcwd().replace("\\", "/")
        self.set_localdir(self.localdir)
        self.remotedir = remotedir
        print (self.login())

    def set_localdir(self, dirname):
        u'''
        设置本地根目录
        dirname: 本地根目录地址
        '''
        try:
            os.chdir(dirname)
            self.localdir = dirname
            print (u'本机当前目录为: %s' % self.localdir)
        except BaseException:
            print (u'error: 目录不存在')

    def set_remotedir(self, dirname):
        u'''
        设置远程根目录
        dirname: 远程根目录地址
        '''
        try:
            self.ftp.cwd(dirname)
            self.remotedir = dirname
            print (u'远程当前目录为: %s' % self.remotedir)
        except BaseException:
            print (u'error: 目录不存在')

    def login(self):
        ftp = self.ftp
        try:
            timeout = 1
            socket.setdefaulttimeout(timeout)
            ftp.set_pasv(True)
            ftp.connect(self.hostaddr, self.port)
            ftp.login(self.username, self.password)
        except Exception:
            return(u"error: 连接或登录失败")
        try:
            ftp.cwd(self.remotedir)
            print (u'远程当前目录为: %s' % self.remotedir)
            return(u'连接服务器成功')

        except(Exception):
            return(u'error: 切换目录失败')

    def __del__(self):
        self.ftp.close()

    def get_file_list(self, line):
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

    def list_dirs(self, dirname='./'):
        u'''
        获取远程目录当前的所有文件夹名称
        dirname: 要获取的远程目录名称
        '''
        temp = self.list_all()
        return [i for i in temp if i[1] == 'dir']

    def list_files(self, dirname='./'):
        u'''
        获取远程目录当前的所有文件名称
        dirname: 要获取的远程目录名称
        '''
        temp = self.list_all()
        return [i for i in temp if i[1] == 'file']

    def list_all(self, dirname='./'):
        u'''
        获取远程目录当前的所有文件夹和文件名
        dirname: 要获取的远程目录名称
        '''
        cwd = self.ftp.pwd()
        try:
            self.ftp.cwd(dirname.encode("gb2312"))
        except BaseException:
            print (u'目录不存在')
            return None

        self.file_list = []
        self.ftp.dir(self.get_file_list)
        remotenames = self.file_list
        x = []
        for item in remotenames:
            filetype = item[1][:item[1].find(" ")].strip()
            filename = item[1][item[1].find(" ") + 1:].strip()
            if filetype.find('DIR') != -1:
                x.append([filename.decode("gb2312"), 'dir', ''])
            else:
                x.append([filename.decode("gb2312"),
                          'file', float(filetype) / 1024])
        self.ftp.cwd(cwd)
        return x

    def is_same_size(self, localfile, remotefile):
        try:
            remotefile_size = self.ftp.size(remotefile.encode("gb2312"))
        except BaseException:
            remotefile_size = -1
        try:
            localfile_size = os.path.getsize(localfile.encode("gb2312"))
        except BaseException:
            localfile_size = -1
        return remotefile_size != localfile_size

    def download_allow(self, localfile, remotefile, same_write, over_write):
        if over_write:
            # over_write为 True 时， 直接强制覆盖
            return True
        elif same_write:
            return self.is_same_size(localfile, remotefile)
        else:
            return not os.path.exists(localfile)

    def upload_allow(self, localfile, remotefile, same_write, over_write):
        if over_write:
            # over_write为 True 时， 直接强制覆盖
            return True
        elif same_write:
            return self.is_same_size(localfile, remotefile)
        else:
            try:
                self.ftp.size(remotefile)
                return False
            except BaseException:
                return True

    def download_files(
            self,
            remotedir=None,
            localdir=None,
            delete=False,
            include=None,
            exclude=None,
            same_write=False,
            over_write=False,
            recursive=True):
        u'''
        下载远程目录文件夹至本地
        remotedir: 要下载的远程文件夹名称 ，默认None，即远程设置目录
        localdir: 存储本地的文件夹名称，默认None，即本地设置目录
        delete: 删除远程文件，默认 不删除
        include: 筛选条件，str or list ，include条件之间为或关系，满足其一均可下载
        exclude: 排除条件，str or list ，exclude条件之间为或关系，满足其一均不可下载
        over_write: 同名文件是否强制覆盖，默认 False ，若为True，同名文件直接强制覆盖
        same_write: 若over_write为False时， 同名文件不同文件大小时是否强制覆盖，默认 False，若为True，\
            只有文件同名且文件大小不同时才强制覆盖，若文件同名且大小相同，不会下载
        recursive: 递归遍历目录下载，默认True ，若为False，则仅下载remotedir当前目录下的文件
        '''
        if not remotedir:
            remotedir = self.remotedir
        temp = self.list_all(remotedir)
        self.temp_dir = './'
        if temp:
            if not localdir:
                localdir = self.localdir
            if not os.path.exists(localdir):
                os.makedirs(localdir)
            for item in temp:
                if item[1] == 'dir':
                    if recursive:
                        self.download_files(
                            os.path.join(
                                remotedir,
                                item[0]),
                            localdir,
                            delete,
                            include,
                            exclude,
                            same_write,
                            over_write,
                            recursive)
                else:
                    self.download_file(
                        os.path.join(
                            remotedir,
                            item[0]),
                        None,
                        localdir,
                        delete,
                        include,
                        exclude,
                        same_write,
                        over_write)

    def download_file(
            self,
            remotefile,
            localfile=None,
            localdir=None,
            delete=False,
            include=None,
            exclude=None,
            same_write=False,
            over_write=False):
        u'''
        下载远程目录文件至本地
        remotefile: 要下载的远程文件名称
        localfile: 存储本地的文件名称，默认None
        localdir: 存储本地的文件夹名称，默认None
        delete: 删除远程文件，默认 不删除
        include: 筛选条件，str or list ，include条件之间为或关系，满足其一均可下载
        exclude: 排除条件，str or list ，exclude条件之间为或关系，满足其一均不可下载
        over_write: 同名文件是否强制覆盖，默认 False ，若为True，同名文件直接强制覆盖
        same_write: 若over_write为False时， 同名文件不同文件大小时是否强制覆盖，默认 False，若为True，\
            只有文件同名且文件大小不同时才强制覆盖，若文件同名且大小相同，不会下载
        '''
        remotefile = os.path.join(self.remotedir, remotefile)
        if localfile and localdir:
            localfile = os.path.join(localdir, localfile)

        if not localdir:
            localdir = self.localdir
        if not localfile:
            filename = diff_path(remotefile, self.remotedir)
            localfile = os.path.join(localdir, filename)

        if check_filename(
                remotefile,
                include,
                exclude) and self.download_allow(
                localfile,
                remotefile,
                same_write,
                over_write):
            try:
                os.makedirs(os.path.dirname(localfile))
            except BaseException:
                pass
            file_handler = open(localfile, 'wb')
            self.ftp.retrbinary(
                'RETR %s' %
                (remotefile.encode("gb2312")),
                file_handler.write)
            file_handler.close()
            print (u'已下载: %s' % localfile)
            if delete:
                self.ftp.delete(remotefile.encode("gb2312"))
                print (u'已删除: %s' % remotefile)

    def makedirs(self, dirname):
        u'''
        递归创建目前目录
        dirname: 待创建的远程多级目录
        '''
        dirs = get_dir(dirname)
        dirs.reverse()
        for dirname in dirs:
            try:
                self.ftp.mkd(dirname)
            except BaseException:
                pass

    def upload_file(
            self,
            localfile,
            remotefile=None,
            remotedir=None,
            delete=False,
            include=None,
            exclude=None,
            same_write=False,
            over_write=False):
        u'''
        上传本地目录文件至远程
        localfile: 待上传的本地文件名称
        remotefile: 远程目录存储的文件名称 ，默认None
        remotedir: 远程目录存储文件夹名称，默认None
        delete: 删除本地文件，默认 不删除
        include: 筛选条件，str or list ，include条件之间为或关系，满足其一均可上传
        exclude: 排除条件，str or list ，exclude条件之间为或关系，满足其一均不可上传
        over_write: 同名文件是否强制覆盖，默认 False ，若为True，同名文件直接强制覆盖
        same_write: 若over_write为False时， 同名文件不同文件大小时是否强制覆盖，默认 False，若为True，\
            只有文件同名且文件大小不同时才强制覆盖，若文件同名且大小相同，不会上传
        '''
        if not os.path.isfile(localfile):
            print (u'本地文件不存在')
            return

        if remotefile and remotedir:
            remotefile = os.path.join(remotedir, remotefile)

        if not remotedir:
            remotedir = self.remotedir

        if not remotefile:
            filename = diff_path(localfile, self.localdir)
            remotefile = os.path.join(remotedir, filename)

        self.makedirs(os.path.dirname(remotefile))

        if check_filename(
                localfile,
                include,
                exclude) and self.upload_allow(
                localfile,
                remotefile,
                same_write,
                over_write):

            file_handler = open(localfile, 'rb')
            self.ftp.storbinary('STOR %s' % remotefile, file_handler)
            file_handler.close()
            print(u'已传送: %s' % (remotefile.decode("gb2312")))
            if delete:
                os.remove(localfile)
                print (u'已删除: %s' % localfile.decode("gb2312"))

    def upload_files(
            self,
            localdir=None,
            remotedir=None,
            delete=False,
            include=None,
            exclude=None,
            same_write=False,
            over_write=False,
            recursive=True):
        u'''
        递归上传本地目录文件夹至远程
        localdir: 待上传的本地文件夹名称，默认None，即本地设置目录
        remotedir: 远程目录存储的文件名称 ，默认None，即远程设置目录
        delete: 删除本地文件，默认 不删除
        include: 筛选条件，str or list ，include条件之间为或关系，满足其一均可上传
        exclude: 排除条件，str or list ，exclude条件之间为或关系，满足其一均不可上传
        over_write: 同名文件是否强制覆盖，默认 False ，若为True，同名文件直接强制覆盖
        same_write: 若over_write为False时， 同名文件不同文件大小时是否强制覆盖，默认 False，若为True，\
            只有文件同名且文件大小不同时才强制覆盖，若文件同名且大小相同，不会上传
        recursive: 递归遍历目录下载，默认True ，若为False，则仅上传localdir当前目录下的文件
        '''
        if not os.path.isdir(localdir):
            print (u'本地目录不存在')
            return
        localnames = os.listdir(localdir)

        for item in localnames:
            src = os.path.join(localdir, item)
            if os.path.isdir(src):
                self.upload_files(
                    src,
                    remotedir,
                    delete,
                    include,
                    exclude,
                    same_write,
                    over_write,
                    recursive)
            else:
                self.upload_file(
                    src,
                    None,
                    remotedir,
                    delete,
                    include,
                    exclude,
                    same_write,
                    over_write)

