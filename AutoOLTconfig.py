import paramiko
import time
import datetime
from _cffi_backend import string
from _ast import If
import tkinter as tk  
from tkinter import ttk
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText
import pickle 
import re
# from  PIL import ImageTk

bras_username = "yangxtnj1"
bras_password = "420590yxT!"
pathfile = r''
ImagePath= r'bg.gif'

# 连接堡垒机登陆一台设备，然后退出到telnet界面
def ssh_connect(ip, username, password, hosttype, port): 
    paramiko.util.log_to_file("paramiko.log")
    try:
        # excmd = ';'.join(cmds)
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(hostname=ip, port=port, username='yangxtnj1', password='420590yxT!')
        # 激活连接的终端
        channel = s.invoke_shell()
        # 读、写操作超时时间，10秒
        channel.settimeout(10)
        choose = ''
        if hosttype == 'BRAS':
            print('开始登陆堡垒机')
            choose = '0' + '\n'
            channel.send(choose)
            time.sleep(1)
            choose = '0' + '\n'
            channel.send(choose)
            time.sleep(1)
            choose = '114' + '\n'
            channel.send(choose) 
            choose = '1' + '\n'
            channel.send(choose)
            print(channel.recv(65533).decode('utf-8').strip()) 
            time.sleep(1)
            choose = username + '\n'           
            channel.send(choose)
            time.sleep(1)
            print(channel.recv(65533).decode('utf-8').strip()) 
            choose = password + '\n'
            channel.send(choose) 
            time.sleep(1)
            print(channel.recv(65533).decode('utf-8').strip()) 
            # 等待连接成功
            while True:
                str1 = str(channel.recv(65533).decode('utf-8').strip())
                print(str1)
                if str1.endswith(">"):
                    break
                else:
                    time.sleep(1)                      
        elif hosttype == 'NE5000E':
            print ('选择省干NE5000E')
            choose = '1' + '\n'
            channel.send(choose)
        else:print ("hosttype输入错误！（normal/db）'")
        # 发送cmds中的指令到资源主机
        return channel    
    except Exception as e:
        channel.close()
        print(e)


# telnet设备
def telnet_connect(ssh_channel, ip, username, password, hosttype, port): 
    try:
        ssh_channel.send("Q" + '\n')
        time.sleep(2)
        print(ssh_channel.recv(65533).decode('utf-8').strip())
        ssh_channel.send("telnet "+ip + '\n')
        time.sleep(1)  
        ssh_channel.send(username +'\n')
        print(ssh_channel.recv(65533).decode('utf-8').strip()) 
        time.sleep(2)           
        while True:
            str1 = str(ssh_channel.recv(65533).decode('utf-8').strip())
            print(str1)
            if str1.endswith("word:"):
                break
            else:
                time.sleep(2)  
        ssh_channel.send(password +'\n')
        time.sleep(2) 
        print(ssh_channel.recv(65533).decode('utf-8').strip())
        return ssh_channel
    except Exception as e:
        ssh_channel.close()
        print("设备telnet失败，请核查bras清单信息")
        print(e)

#执行指令
def telnet_command(ssh_channel,command_script):
    ssh_channel.send(command_script)
    time.sleep(1)
    str1 = str(ssh_channel.recv(65533).decode('utf-8').strip())
    print(str1)
    return str1

#自动配置 
def AutoConfig():
    BrasIP = (BrasChosen_GUI.get()).split('\t')[0]
    print (BrasIP)
    
    BrasType_GUI = (BrasChosen_GUI.get()).split('\t')[1]
    if (re.findall('ME60', BrasType_GUI)):
        BrasType = 'ME60'
    elif (re.findall('M6000', BrasType_GUI)):
        BrasType = 'M6000'
    elif (re.findall('7750', BrasType_GUI)):
        BrasType = '7750'
    print(BrasType)
    
    #端口配置格式检查
    Port_Info = Port_GUI.get()
    print (Port_Info)
    if (len(re.findall(r'\d*/\d*/\d*',Port_Info)) == 0):
        tkinter.messagebox.showerror(title='配置格式错误', message="格式为 slot_no/subcard_no/port_no")
        return
   
    Description = Description_GUI.get()
    print (Description)
    
    OLT_Vlan = OLT_Vlan_GUI.get()
    print (OLT_Vlan)
    if (len(re.findall(r'\d*',OLT_Vlan)) == 0):
        tkinter.messagebox.showerror(title='配置格式错误', message="请输入正确vlan")
        return
    
    OLT_IP = OLT_IP_GUI.get()
    print (OLT_IP)
    if (len(re.findall(r'\d*.\d*.\d*.\d*',OLT_IP)) == 0):
        tkinter.messagebox.showerror(title='配置格式错误', message="请输入正确OLT互联 IP")
        return
     
    Multicast_IP= Multicast_IP_GUI.get()
    print (Multicast_IP)
    # if (len(re.findall(r'\d.\d.\d.\d',Multicast_IP)) == 0):
    #    tkinter.messagebox.showerror(title='配置格式错误', message="请输入正确组播IP")
    #    return
    
    bras_username = Loguser_GUI.get()
    bras_password = Password_GUI.get()
    
    #生成配置文件
    if (BrasType == 'ME60'):
       Template =  open(pathfile+r'ME60_Template.log', 'r') 
    elif (BrasType == 'M6000'): 
       Template =  open(pathfile+r'M6000_Template.log', 'r')
    elif (BrasType == '7750'): 
       Template =  open(pathfile+r'7750_Template.log', 'r')    
    
    Content_Tem = Template.read()
    Template.close()
    
    Content = Content_Tem.replace('Port_Temp',Port_Info)
    Content = Content.replace('Description_Temp',Description)
    Content = Content.replace('Domain_Temp',Domain_GUI.get())
    Content = Content.replace('Vlan_Temp',OLT_Vlan)
    Content = Content.replace('IP_Temp',OLT_IP)
    Content = Content.replace('Multicast_Temp',Multicast_IP)  
    
    with open(pathfile+r"olt_config.log","w") as ME60_olt_config:
        ME60_olt_config.write(Content)
    ME60_olt_config.close()
    
    #登录SSH
    ssh_channel1 = ssh_connect("10.40.115.250", bras_username,bras_password, "BRAS", "22")
    print("SSH 连接成功，开始登陆")
    
    ssh_channel1 = telnet_connect(ssh_channel1,BrasIP,bras_username,bras_password,BrasType,23)
    print("telnet 连接成功，开始配置")
    
    with open(pathfile+r"olt_config.log",'r') as com_file:
        com_list = com_file.readlines()
        for j in range(0, len(com_list)): 
            telnet_command(ssh_channel1,com_list[j].strip('\n')+ '\n') 
            
    tkinter.messagebox.showinfo(title='OLT 配置完成', message="auto_config successful")
    # with open(pathfile+r'\ME60_olt_config.log', 'r') as bras_file:
    #   bras_list = bras_file.readlines()
    #   #逐行读取BRAS清单
    #   for i in range(0, len(bras_list)):
    #     bras_list[i] = bras_list[i].strip('\n')
    #     bras_type,bras_ip = str(bras_list[i]).split(',')
    #     #ME60设备执行指令
    #     print(bras_type)
    #     if bras_type == 'ME60':
    #         print(bras_type+bras_ip+"开始登陆")
    #         ssh_channel1 = telnet_connect(ssh_channel1,bras_ip,bras_username,bras_password,bras_type,23)
    #         with open(pathfile+r"\ME60_olt_config.log",'r') as com_file:
    #             com_list = com_file.readlines()
    #             for j in range(0, len(com_list)): 
    #                 #print(com_list[j].strip('\n')+ '\n')
    #                 telnet_command(ssh_channel1,com_list[j].strip('\n')+ '\n')              
    #     elif bras_type == "M6000":
    #         print(bras_type+bras_ip+"开始执行")
    #     else:
    #         print("文件格式错误，无法正常解析")
    #         ssh_channel1.close()
    #         bras_file.close()
    #         com_file.close()
    #     break    


#TK GUI
#window = tk.Toplevel()
window = tk.Tk()

window.title('OLTAutoConfig_V1.1')
window.geometry('800x600')
canvas = tk.Canvas(window, width=800, height=600, bg='green')
ImagePath = tk.PhotoImage(file=ImagePath)
image = canvas.create_image(800, -100, anchor='n', image=ImagePath)

canvas.pack(side='top')
tk.Label(window, text='Script_Transformer',font=('微软雅黑', 16)).pack()

with open(pathfile+r'Bras.log', 'r') as bras_file:
    bras_list = bras_file.readlines()
    for i in range(0, len(bras_list)):
        bras_list[i] = bras_list[i]
bras_file.close()

tk.Label(window, text='Bras选择', font=('微软雅黑', 12)).place(x=10, y=50)
BrasChosen_GUI = ttk.Combobox(window, width=50, state='readonly')
BrasChosen_GUI['value']  = bras_list
BrasChosen_GUI.place(x=100,y=50)

tk.Label(window, text='Bras端口', font=('微软雅黑', 12)).place(x=10, y=100)
Port_GUI = tk.Entry(window, width=30,textvariable='Port_GUI')
Port_GUI.place(x=100,y=100)


tk.Label(window, text='端口描述', font=('微软雅黑', 12)).place(x=10, y=150)
# Descrip = ScrolledText(window, height=1,width=50)
Description_GUI = tk.Entry(window, width=30,textvariable='Description')
Description_GUI.place(x=100,y=150)

tk.Label(window, text='Domain', font=('Times New Roman', 14)).place(x=10, y=200)
Domain_GUI = ttk.Combobox(window, width=27, state='readonly')
Domain_GUI['value']  = ['pppoe.lishuiqu','pppoe.gaochunqu','pppoe.jiangningqu','pppoe.gulouqu','pppoe.jianyequ','pppoe.yuhuaqu','pppoe.liuhequ','pppoe.qixiaqu','pppoe.xuanwuqu']
Domain_GUI.place(x=100,y=200)

tk.Label(window, text='OLT_Vlan', font=('Times New Roman', 14)).place(x=10, y=250)
# Descrip = ScrolledText(window, height=1,width=50)
OLT_Vlan_GUI = tk.Entry(window, width=30,textvariable='OLT_Vlan')
OLT_Vlan_GUI.place(x=100,y=250)

tk.Label(window, text='OLT_IP', font=('Times New Roman', 14)).place(x=400, y=250)
# Descrip = ScrolledText(window, height=1,width=50)
OLT_IP_GUI = tk.Entry(window, width=30,textvariable='OLT_IP')
OLT_IP_GUI.place(x=500,y=250)

tk.Label(window, text='组播IP', font=('微软雅黑', 12)).place(x=10, y=300)
# Descrip = ScrolledText(window, height=1,width=50)
Multicast_IP_GUI = tk.Entry(window, width=30,textvariable='Multicast_IP')
Multicast_IP_GUI.place(x=100,y=300)

tk.Label(window, text='Username', font=('Times New Roman', 12)).place(x=10, y=450)
# Descrip = ScrolledText(window, height=1,width=50)
Loguser_GUI = tk.Entry(window, width=30,textvariable='Loguser')
Loguser_GUI.place(x=100,y=450)
tk.Label(window, text='Password', font=('Times New Roman', 12)).place(x=400, y=450)
# Descrip = ScrolledText(window, height=1,width=50)
Password_GUI = tk.Entry(window, width=30,textvariable='Password')
Password_GUI.place(x=500,y=450)


btn_login_GUI = tk.Button(window, text='自动配置',height=2,width=10,command=AutoConfig)
btn_login_GUI.place(x=350, y=500)

# D:\ProgramData\Anaconda3\Scripts>pyinstaller -F  E:\python\CMNETautoconfig\AutoOLTconfig.py
window.mainloop()