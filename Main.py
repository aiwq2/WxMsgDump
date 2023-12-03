# 版本号
VER = "V1.1"
import WechatManager
import CrackWeChatDB
import os
import sys
import sqlite3
import SQLManager
# import keyboard
import pymem
from pymem import Pymem
# from pick import pick
from win32com.shell import shell
from tkinter import *
from analyze import analyze


# Msg目录下的表
msg_table = ["MicroMsg.db"] 
# Mutil目录下的表 除了msgn.db
mutil_table = []
# Micromsg.db的路径
micromsg_path = ""
# MSGn.db文件数组
msgn_path = []

# 聊天列表 下标对应UserName,Alias,Remark,NickName
wxlist = []



def main(wx_path,name):
    res = [] #所有db文件的名称数组
    isSkipDc = False #跳过解密

    print("WxMsgDump%s | 微信聊天记录导出"%VER)
    print()
    print("Copyright(c) Jiang")
    print("----------------------------------------")

    # 定义对象
    try:
        wechat = Pymem("WeChat.exe")
        ret = WechatManager.Wechat(wechat).GetInfo()
        keyAddress = ret[0]
        aeskey = ret[1]
    except pymem.exception.ProcessNotFound:
        print("[!]微信没有登录")
    except pymem.exception.CouldNotOpenProcess:
        print("[!]权限不足")
    except Exception as e:
        print(e)
    
    print('aesky:',aeskey)
    wx =  WechatManager
    ret = wx.Wechat(wechat).GetUserBasicInfo(keyAddress)
    wxid = ret[0]
    wxprofile = ret[1]

    # 自动获取文件路径
    # win_user = os.path.expandvars('$HOMEPATH')
    # wx_config = open(os.getenv("SystemDrive") + win_user + '\\AppData\\Roaming\\Tencent\\WeChat\\All Users\\config\\3ebffe94.ini')

    # if wx_config.read() == 'MyDocument:':
    #     wx_path = shell.SHGetFolderPath(0, 5, None, 0)+"\\WeChat Files\\"+wxid+"\\Msg" # 如果目录在 文档 下
    # else:
    #     wx_path = wx_config.read() + "\\WeChat Files\\"+wxid+"\\Msg"
    #     # wx_path = 'D:\\WeChat' + "\\WeChat Files\\"+wxid+"\\Msg"
    dir_path = wx_path + "\\Multi"

    print("[+]微信号: "+wxprofile+" 工作路径: "+wx_path)


    # 检查是否有留存过的解密文件
    files = os.listdir(dir_path)

    for name in files:
        if name.endswith(".dec.db"):
            key = input("[>]发现上次解密过的文件。跳过解密步骤->Y 删除全部解密文件->D 覆盖解密->回车:").capitalize()
            if key == 'Y':
                isSkipDc = True
            if key == 'D':
                del_decryptf(wx_path)
                del_decryptf(dir_path)
                input("[+]操作完成，任意键退出")
                exit(0)
            break

    # 获取Mutil下的表
    try:
        for path in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, path)) and path.endswith(".db") and path.endswith("dec.db") is not True:
                if path.startswith("MSG") or path in mutil_table:
                    res.append(path)
            #TODO 需要额外询问
    except:
        #输入d可以打开debug
        #if(dir_path == "d\\Msg\\Multi"):
        #    print("[Opening Debug]")
        #    DBManagement.main()
        #    return
        #else:
        print("[-]路径无效。请注意，你可能忽略了点击“打开文件夹”按钮这个步骤")
        exit(-1)
    
    # 获取Msg目录下的表
    for path in os.listdir(wx_path):
        if os.path.isfile(os.path.join(wx_path, path)) and path in msg_table:
            res.append(path)

    print("[+]发现以下表: "+str(list(res)))
    if res is []:
        print("[+]解密完成，没有发现任何聊天文件，或者已经解密过")
        exit(0)
    
    
    if isSkipDc is not True:
        #删除以前的解密
        for file_name in os.listdir(dir_path):
            if file_name.endswith(".dec.db"):
                try:
                    os.remove(file_name)
                except:
                    pass
        #执行加密
        decryptMsg(res,dir_path,wx_path,aeskey)
    
    

    # 将之转换成路径数组
    for path in res:
        if(path.startswith("MSG")):
            msgn_path.append(dir_path+"\\"+path+".dec.db")
        elif path in msg_table:
            if path == "MicroMsg.db":
                micromsg_path = wx_path+"\\"+path+".dec.db"

    print("[+]正在获取聊天列表")
    wxlist = SQLManager.get_chatlist(micromsg_path)
    # while True:
    print("[+]请输入要导出的聊天名称，或者你给他/她的备注。空表示退出操作。")
    aimChat = name
    # if aimChat=="":
    #     break
    if aimChat!="":
        repeat_count = 1
        for chat in wxlist:
            #print(chat[3])
            if chat[3]==aimChat or chat[2]==aimChat:
                print("============FOUND TARGET===========")
                print("[+]匹配到第"+str(repeat_count)+"个聊天: ",chat[0])
                print("[+]微信号: ", chat[1])
                print("[+]备注: ",chat[2])
                print("[+]昵称: ",chat[3])
                outputPath=export_msg(msgn_path,chat[0],chat[3],chat[1])
                repeat_count = repeat_count+1
                print("=============END OUTPUT============")
        if repeat_count == 1:
            print("[!]找不到此聊天: ",aimChat)
    del_decryptf(wx_path)
    del_decryptf(dir_path)


   
            


def decryptMsg(res,dir_path,wx_path,aeskey):
    for path in res:
        if(path.startswith("MSG")): # 解密Mutil下的文件
            CrackWeChatDB.decrypt_msg(dir_path+"\\"+path,aeskey,res.index(path)+1,len(res))
        else: # 解密Msg下的文件
             CrackWeChatDB.decrypt_msg(wx_path+"\\"+path,aeskey,res.index(path)+1,len(res))
        if(res.index(path)+1!=len(res)):
             # 覆盖原来的进度条
            print("\r","                                                                                  ",end="",flush=True)
    print()

def del_decryptf(path):
    for root , dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".dec.db"):   #指定要删除的格式，这里是jpg 可以换成其他格式
                os.remove(os.path.join(root, name))

def export_msg(msg_paths,uuid,nick,wxid):
    outputPath = ""
    for path in msg_paths:
        flag,outputPath = SQLManager.msg_export(path,uuid,nick,wxid,msg_paths.index(path)+1)
    print("[+]完成，导出到"+outputPath)
    return outputPath

def GUI():
    def get_entry_value(root):
        wx_path= entry_path.get()
        start_time=entry_start_time.get()
        end_time=entry_end_time.get()
        name=entry_name.get()
        print("Entry的值为：", wx_path)
        print("start_time的值为：", start_time)
        print("end_time的值为：", end_time)
        print("entry_name的值为：", name)
        analyzing=Label(root,text='正在分析中，请稍后...')
        analyzing.pack()

        outputPath=main(wx_path,name)
        analyze(outputPath)


    root=Tk()

    # 窗口大小
    
    root.geometry("700x450+674+182")
    #  窗口标题
    root.title("微信聊天记录导出")

    # 添加标签控件
    label_path = Label(root,text="请输入你的微信MSG文件路径：",font=("宋体",10))
    # 定位
    # label.grid(row=1,column=0)
    label_path.pack()





    # 添加输入框
    entry_path = Entry(root,font=("宋体",15),width=50)
    # entry.grid(row=1,column=1)
    entry_path.pack()

    label_start_time = Label(root,text="请输入查询的开始时间(格式为例如2022-10-29)：",font=("宋体",10))
    # 定位
    # label.grid(row=1,column=0)
    label_start_time.pack()

    # 添加输入框
    entry_start_time = Entry(root,font=("宋体",15),width=50)
    # entry.grid(row=1,column=1)
    entry_start_time.pack()

    label_end_time = Label(root,text="请输入查询的结束时间(格式为例如2022-10-29)：",font=("宋体",10))
    # 定位
    # label.grid(row=1,column=0)
    label_end_time.pack()

        # 添加输入框
    entry_end_time = Entry(root,font=("宋体",15),width=50)
    # entry.grid(row=1,column=1)
    entry_end_time.pack()

    
    label_name = Label(root,text="请输入要导出的聊天名称，或者你给他/她的备注",font=("宋体",10))
    # 定位
    # label.grid(row=1,column=0)
    label_name.pack()

        # 添加输入框
    entry_name = Entry(root,font=("宋体",15),width=50)
    # entry.grid(row=1,column=1)
    entry_name.pack()

    # 添加点击按钮
    button = Button(root,text="提交",font=("宋体",15),fg="blue",command=lambda:get_entry_value(root))
    # button.grid(row=2,column=1)
    button.pack()


    
    root.mainloop()
    


if __name__ == '__main__':
    # main()
    GUI()