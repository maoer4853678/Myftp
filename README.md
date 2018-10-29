# Myftp

## 基于 ftplib 的 通用 FTP 类

    API 特性
    1. 通用FTP类，支持递归下载远程目录文件夹，支持递归上传本地文件夹
    2. 支持递归创建远程目录

# 使用步骤：

  # 实例化 MYFTP

  	默认参数
    hostaddr="127.0.0.1", FTP 服务器地址 默认 本机IP
    username="anonymous", FTP 用户名 默认 匿名访问
    password='', FTP 密码 默认 无
    remotedir='./', FTP 服务器访问的根目录
    port=21 FTP 协议端口号，默认 21

    x = MYFTP()
    
# MYFTP方法调用

  # 设置本地根目录
    x.set_localdir(dirname)
    	dirname: 本地根目录地址

    	return None

  # 设置远程根目录
    x.set_remotedir(dirname)
    	dirname: 远程根目录地址

    	return None


  # 获取远程目录当前的所有文件夹和文件名
    x.list_all(dirname='./')
		dirname: 要获取的远程目录名称
		
		return [[]]

  # 获取远程目录当前的所有文件夹名称
    x.list_dirs(dirname='./')
		dirname: 要获取的远程目录名称
		
		return [[]]

  # 获取远程目录当前的所有文件名称
    x.list_files(dirname='./')
		dirname: 要获取的远程目录名称
		
		return [[]]

  # 递归创建远程目录
    x.makedirs(dirname='./')
		dirname: 待创建的远程多级目录
		
		return None


  # 下载远程目录文件至本地
    x.download_file(remotefile,localfile=None,localdir=None,delete=False,\
            include=None,exclude=None,same_write=False,over_write=False)
      	remotefile: 要下载的远程文件名称
		localfile: 存储本地的文件名称，默认None
		localdir: 存储本地的文件夹名称，默认None
		delete: 删除远程文件，默认 不删除
		include: 筛选条件，str or list ，include条件之间为或关系，满足其一均可下载
		exclude: 排除条件，str or list ，exclude条件之间为或关系，满足其一均不可下载
		over_write: 同名文件是否强制覆盖，默认 False ，若为True，同名文件直接强制覆盖
		same_write: 若over_write为False时， 同名文件不同文件大小时是否强制覆盖，默认 False，若为True，\
		只有文件同名且文件大小不同时才强制覆盖，若文件同名且大小相同，不会下载
      	
      	return None

  # 下载远程目录文件夹至本地
    x.download_files(remotedir=None,localdir=None,delete=False,include=None,\
            exclude=None,same_write=False,over_write=False,recursive=True)
        remotedir: 要下载的远程文件夹名称 ，默认None，即远程设置目录
        localdir: 存储本地的文件夹名称，默认None，即本地设置目录
        delete: 删除远程文件，默认 不删除
        include: 筛选条件，str or list ，include条件之间为或关系，满足其一均可下载
        exclude: 排除条件，str or list ，exclude条件之间为或关系，满足其一均不可下载
        over_write: 同名文件是否强制覆盖，默认 False ，若为True，同名文件直接强制覆盖
        same_write: 若over_write为False时， 同名文件不同文件大小时是否强制覆盖，默认 False，若为True，\
            只有文件同名且文件大小不同时才强制覆盖，若文件同名且大小相同，不会下载
        recursive: 递归遍历目录下载，默认True ，若为False，则仅下载remotedir当前目录下的文件

        return None

  # 上传本地目录文件至远程
    x.upload_file(localfile, remotefile=None,remotedir=None,delete=False,\
            include=None,exclude=None,same_write=False,over_write=False)
        localfile: 待上传的本地文件名称
        remotefile: 远程目录存储的文件名称 ，默认None
        remotedir: 远程目录存储文件夹名称，默认None
        delete: 删除本地文件，默认 不删除
        include: 筛选条件，str or list ，include条件之间为或关系，满足其一均可上传
        exclude: 排除条件，str or list ，exclude条件之间为或关系，满足其一均不可上传
        over_write: 同名文件是否强制覆盖，默认 False ，若为True，同名文件直接强制覆盖
        same_write: 若over_write为False时， 同名文件不同文件大小时是否强制覆盖，默认 False，若为True，\
            只有文件同名且文件大小不同时才强制覆盖，若文件同名且大小相同，不会上传

        return None

  # 递归上传本地目录文件夹至远程
    x.upload_files(localdir=None,remotedir=None,delete=False,include=None,\
            exclude=None,same_write=False, over_write=False,recursive=True):
        localdir: 待上传的本地文件夹名称，默认None，即本地设置目录
        remotedir: 远程目录存储的文件名称 ，默认None，即远程设置目录
        delete: 删除本地文件，默认 不删除
        include: 筛选条件，str or list ，include条件之间为或关系，满足其一均可上传
        exclude: 排除条件，str or list ，exclude条件之间为或关系，满足其一均不可上传
        over_write: 同名文件是否强制覆盖，默认 False ，若为True，同名文件直接强制覆盖
        same_write: 若over_write为False时， 同名文件不同文件大小时是否强制覆盖，默认 False，若为True，\
            只有文件同名且文件大小不同时才强制覆盖，若文件同名且大小相同，不会上传
        recursive: 递归遍历目录下载，默认True ，若为False，则仅上传localdir当前目录下的文件
        
        return None