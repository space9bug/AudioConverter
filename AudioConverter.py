import json
import os
import re
import struct
import subprocess
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from urllib import parse

import requests

# 当前版本号
version = "V3.0.1"
# 创建应用程序窗口
root = tk.Tk()
root.title("Soul录音格式转换器3.0.1 - 独居者")
root.iconbitmap("logo.ico")
root.attributes("-alpha", 0.99)
# 设置颜色
progress_color = "#1E94A0"
progress_chunk_color = "#FA7268"
declare_color = "red"
update_color = "#F9425B"
update_bg_color = "#0071CF"
font_color = "#EBE5D9"
btn_color = "#14B09B"
frame_color = "#0359AE"
# 设置字体
l_font = ("宋体", 12)
m_font = ("宋体", 11)
s_font = ("宋体", 9)
# 设置窗口大小
width = 603
height = 339
# 获取屏幕尺寸以计算布局参数，使窗口居于屏幕中央
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
geometry_str = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 3)
root.geometry(geometry_str)
root.resizable(width=False, height=False)
L_frame = tk.Frame(width=373, height=height, bg=frame_color)
R_frame = tk.Frame(width=230, height=height, bg=frame_color)
L_frame.grid(row=0, column=0)
R_frame.grid(row=0, column=1)


# 反馈信息发送函数，具体实现可以自定义，钉钉机器人和与你机器人均可
# 钉钉机器人文档：https://ding-doc.dingtalk.com/doc#/serverapi2/krgddi
# 与你机器人文档：http://www.uneed.com/openapi/pages/index.html#/chatbot/intro
def send_message():
    try:
        print(text.get("1.0", "end"))
        msg = text.get("1.0", "end")

        # 填写自己的与你群id和token
        yuni_group_id = "XXXXXX"
        yuni_group_token = "XXXXXX"
        url = "https://api.uneedx.com/v2/robot/message"

        payload = "token=" + yuni_group_token + "&unionGid=" + yuni_group_id + "&msgType=text&content=" + msg
        headers = {
            'Host': "api.uneedx.com",
            'Content-Type': "application/x-www-form-urlencoded"
        }

        response = requests.request("POST", url, data=payload.encode("utf-8"), headers=headers)

        print(response.text)
        status = json.loads(response.text)["ec"]
        error_msg = json.loads(response.text)["em"]
        if status == 200:
            print("发送成功")
            messagebox.showinfo(title="提示", message="发送成功")
        if status == 400:
            print("当前反馈人数较多，请稍后再试")
            messagebox.showwarning(title="警告", message="当前反馈人数较多，请稍后再试")
        if status == 500:
            print("系统错误，请稍后再试")
            messagebox.showerror(title="错误", message="系统错误，请稍后再试")
        if status == 501:
            print("参数错误：" + error_msg)
            messagebox.showerror(title="错误", message="参数错误：" + error_msg)
        if status == 505:
            print("文本违规，不可发送")
            messagebox.showwarning(title="警告", message="文本违规，不可发送")
        if status == 506:
            print("软件已更新，请下载新版使用")
            messagebox.showinfo(title="提示", message="软件已更新，请下载新版使用")
    except Exception as e:
        print("网络未连接，请检查连接后重试")
        print(e)
        messagebox.showwarning(title="警告", message="网络未连接，请检查连接后重试")


# 创建按钮组件，并设置事件
buttonSend = tk.Button(R_frame, text="给开发者的话", command=send_message, font=m_font, bd=0, bg=btn_color, fg=font_color,
                       activeforeground=font_color, activebackground=frame_color)
buttonSend.place(x=65, y=230, width=101, height=30)


# ————————————————————————————————————————————————————————————
def del_show(event):
    text.delete("1.0", "end")


text = tk.Text(R_frame, width=5, height=5, bd=1, relief="solid", font=s_font, bg=frame_color, fg=font_color)
text.place(x=30, y=50, width=170, height=155)
text.insert(tk.INSERT, "有什么想对开发者说的可以说")
text.bind("<Button-1>", del_show)


# print(text.get("1.0", "end"))
# ————————————————————————————————————————————————————————————
def del_url_show():
    entry_url.delete(0, "end")


entry_url = tk.Entry(L_frame, validate="focusin", validatecommand=del_url_show, font=s_font, bd=1, relief="solid",
                     bg=frame_color,
                     fg=font_color)
entry_url.place(x=30, y=160, width=238, height=30)
entry_url.insert(0, "请输入分享链接即可")


# 解析jsonp数据格式为json
def loads_jsonp(_jsonp):
    try:
        return json.loads(re.match(".*?({.*}).*", _jsonp, re.S).group(1))
    except:
        raise ValueError('Invalid Input')


def get_kg_music_parm(music_url):
    print("开始获取全民K歌的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    # url里的查询参数
    query_dict = parse.parse_qs(result.query)
    s_id = query_dict["s"]
    print(s_id)

    url = "https://cgi.kg.qq.com/fcgi-bin/kg_ugc_getdetail"

    querystring = {"inCharset": "GB2312", "outCharset": "utf-8", "v": "4", "shareid": s_id,
                   "callback": "jQuery111303031616258176071_1574126320517", "_": "1574126320520"}

    headers = {
        'Host': "cgi.kg.qq.com",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    music_data = loads_jsonp(response.text)["data"]
    print(music_data["song_name"] + ".m4a")
    play_url = "http://node.kg.qq.com/cgi/fcgi-bin/fcg_get_play_url?shareid=" + s_id[0]
    print(play_url)
    print(music_data["playurl"])
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["song_name"])
    music_parm = [music_name, play_url]
    return music_parm


def get_xima_music_parm(music_url):
    print("开始获取喜马拉雅的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    song_id = result.path.rsplit('/', 1)[1]
    print(song_id)

    url = "https://m.ximalaya.com/tracks/" + song_id + ".json"

    headers = {
        'Host': "m.ximalaya.com",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers)
    print(response.text)

    music_data = json.loads(response.text)
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["title"])
    print(music_name)
    play_path_64 = music_data["play_path_64"]

    music_parm = [music_name, play_path_64]
    return music_parm


def get_changba_music_parm(music_url):
    print("开始获取唱吧的参数")
    html = requests.get(music_url).text

    title_res = re.search(r'<div class="title">(?P<title>[\s\S]*?)</div>', html)
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", title_res.groupdict()['title'])
    print(music_name)
    work_id_res = re.search(r'<span class="fav" data-workid="(?P<work_id>[\s\S]*?)" data-status="0">', html)
    work_id = work_id_res.groupdict()['work_id']
    mp3_url = "http://qiniuuwmp3.changba.com/" + work_id + ".mp3"

    music_parm = [music_name, mp3_url]
    return music_parm


# （已发现缺陷）打印日志不全，文件头过长，不过文件转换没有问题
def get_lizhi_music_parm(music_url):
    print("开始获取荔枝的参数")
    # 将%xx转义符替换为它们的单字符等效项
    url_data = parse.unquote(music_url)

    # url结果
    result = parse.urlparse(url_data)
    print(result)

    song_id = result.path.rsplit('/', 1)[1]
    print(song_id)

    url = "https://m.lizhi.fm/vodapi/voice/info/" + song_id

    headers = {
        'Host': "m.lizhi.fm",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers)
    print(response.text)

    music_data = json.loads(response.text)["data"]
    # 文件名不能包含下列任何字符：\/:*?"<>|       英文字符
    music_name = re.sub(r'[\\/:*?"<>|\r\n]+', "", music_data["userVoice"]["voiceInfo"]["name"])
    print(music_name)
    track_url = music_data["userVoice"]["voicePlayProperty"]["trackUrl"]

    music_parm = [music_name, track_url]
    return music_parm


def get_all_music_parm(music_url):
    if re.match(r"^((https|http)?:\/\/kg2.qq.com)[^\s]+", music_url) is not None:
        music_parm = get_kg_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/node.kg.qq.com)[^\s]+", music_url) is not None:
        music_parm = get_kg_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/www.ximalaya.com)[^\s]+", music_url) is not None:
        music_parm = get_xima_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/changba.com)[^\s]+", music_url) is not None:
        music_parm = get_changba_music_parm(music_url)
    elif re.match(r"^((https|http)?:\/\/www.lizhi.fm)[^\s]+", music_url) is not None:
        music_parm = get_lizhi_music_parm(music_url)
    else:
        music_parm = ["null", "null"]

    # music_parm = ['音乐名', '音乐链接']
    return music_parm


def open_urlfile():
    # 禁用开始按钮
    buttonStart.config(state="disabled")
    music_url = entry_url.get()
    if music_url == "" or music_url == "请输入分享链接即可":
        messagebox.showwarning(title="警告", message="请输入分享链接后执行")
        # 恢复开始按钮
        buttonStart.config(state="normal")
        return
    try:
        music_data = get_all_music_parm(music_url)
        if music_data[0] == "null" and music_data[1] == "null":
            print("不支持此分享链接或者链接格式错误")
            messagebox.showwarning(title="警告", message="不支持此分享链接或者链接格式错误")
            # 恢复开始按钮
            buttonStart.config(state="normal")
            return
        music_name = music_data[0]
        music_play_url = music_data[1]
    except Exception as e:
        print("网络未连接，请检查连接后重试")
        print(e)
        messagebox.showwarning(title="警告", message="网络未连接，请检查连接后重试")
        # 恢复开始按钮
        buttonStart.config(state="normal")
        return
    content.set(music_name)
    # 开始转换
    ##########################################################################################################
    start_time = time.perf_counter()
    sampling_rate = "48000"
    if vc1.get() == 1:
        sampling_rate = "32000"
    temp_path = "TEMP\\"
    mkdir(temp_path)
    # 临时音乐名
    temp_music_name = str(round(time.time() * 1000))
    str_out = ['ffmpeg.exe', '-i', music_play_url, '-ar', sampling_rate, '-ac', '1', '-acodec', 'pcm_s16le',
               '-hide_banner',
               temp_path + temp_music_name + ".wav"]
    print(str_out)
    si = subprocess.STARTUPINFO()
    si.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    process = subprocess.Popen(str_out, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8",
                               text=True, startupinfo=si)
    for line in process.stdout:
        # print(line)

        duration_res = re.search(r'\sDuration: (?P<duration>\S+)', line)
        if duration_res is not None:
            duration = duration_res.groupdict()['duration']
            duration = re.sub(r',', '', duration)

        result = re.search(r'\stime=(?P<time>\S+)', line)
        if result is not None:
            elapsed_time = result.groupdict()['time']
            progress = (get_seconds(elapsed_time) / get_seconds(duration)) * 100
            print(elapsed_time)
            print(progress)
            # content.set("进度:%3.2f" % progress + "%")
            p1["value"] = progress
            root.update()
    process.wait()
    if process.poll() == 0:
        infile_path = temp_path + temp_music_name + ".wav"
        outfile_path = "WAV\\" + music_name + ".wav"

        del_wavparm(infile_path, outfile_path)

        elapsed = (time.perf_counter() - start_time)
        print("耗时:%6.2f" % elapsed + "秒")
        content.set("耗时:%6.2f" % elapsed + "秒")
        del_file(temp_path)
        print("success:", process)
        # 设置终点
        p1["value"] = 115
    else:
        print("error:", process)
    # 恢复开始按钮
    buttonStart.config(state="normal")


# 创建按钮组件，并设置事件
buttonOpenUrl = tk.Button(L_frame, text="网络转换", command=open_urlfile, font=m_font, bd=0, bg=btn_color, fg=font_color,
                          activeforeground=font_color,
                          activebackground=frame_color)
buttonOpenUrl.place(x=268, y=160, width=75, height=30)

labOut = tk.Label(L_frame, text="输出配置：", justify="left", font=m_font, bg=frame_color, fg=font_color)
labOut.place(x=30, y=250, width=75, height=30)

vc1 = tk.IntVar()
C1 = tk.Checkbutton(L_frame, text="旧版", font=m_font, variable=vc1, bg=frame_color, fg=font_color,
                    activeforeground=font_color, activebackground=frame_color,
                    selectcolor=frame_color)
C1.place(x=110, y=250, width=71, height=30)

content = tk.StringVar()
content.set("请选择要转换的音频文件")
lab = tk.Label(L_frame, textvariable=content, font=m_font, bg=frame_color, fg=font_color)
lab.place(x=30, y=110, width=313, height=20)

name = ""


# 按钮事件处理函数
def openfile():
    # print("文本框内容：" + entry_url.get())
    file_path = filedialog.askopenfilename(title="选择音频文件")
    global name
    name = file_path
    filename = os.path.basename(name)
    print(name)
    content.set(filename)


# 创建按钮组件，并设置事件
buttonOpen = tk.Button(L_frame, text="打开本地文件", command=openfile, font=m_font, bd=0, bg=btn_color, fg=font_color,
                       activeforeground=font_color,
                       activebackground=frame_color)
buttonOpen.place(x=110, y=200, width=101, height=30)


def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
    os.rmdir(path)


def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    is_exists = os.path.exists(path)

    # 判断结果
    if not is_exists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)

        print(path + ' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(path + ' 目录已存在')
        return False


def get_seconds(input_time):
    h = int(input_time[0:2])
    # print("时：" + str(h))
    m = int(input_time[3:5])
    # print("分：" + str(m))
    s = int(input_time[6:8])
    # print("秒：" + str(s))
    ms = int(input_time[9:12])
    # print("毫秒：" + str(ms))
    ts = (h * 60 * 60) + (m * 60) + s + (ms / 1000)
    return ts


def del_wavparm(infile_path, outfile_path):
    file_in = open(infile_path, 'rb')
    data = file_in.read(100)
    # print(data[4:8])
    if data[36:40] == b'LIST':
        print(data[36:70])
        length5 = struct.unpack('<L', bytes(data[40:44]))
        cut_len = length5[0] + 8

        length0 = struct.unpack('<L', bytes(data[4:8]))
        f_len = struct.pack('<L', length0[0] - cut_len)
        print(f_len)

    file_out = open(outfile_path, "wb")
    file_out.write(data[0:4])
    file_out.write(f_len)
    file_out.write(data[8:36])
    file_in.seek(36 + cut_len, 0)
    file_out.write(file_in.read())
    file_out.close()
    file_in.close()


def start():
    # 禁用网络按钮
    buttonOpenUrl.config(state="disabled")
    start_time = time.perf_counter()
    if not name:
        messagebox.showwarning(title="警告", message="请先选择文件后执行")
        # 恢复网络按钮
        buttonOpenUrl.config(state="normal")
        return
    sampling_rate = "48000"
    if vc1.get() == 1:
        sampling_rate = "32000"
    temp_path = "TEMP\\"
    mkdir(temp_path)
    music_name = os.path.splitext(os.path.basename(name))[0]
    temp_music_name = str(round(time.time() * 1000))
    str_out = ['ffmpeg.exe', '-i', name, '-ar', sampling_rate, '-ac', '1', '-acodec', 'pcm_s16le', '-hide_banner',
               temp_path + temp_music_name + ".wav"]
    print(str_out)
    si = subprocess.STARTUPINFO()
    si.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    process = subprocess.Popen(str_out, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8",
                               text=True, startupinfo=si)
    for line in process.stdout:
        # print(line)

        duration_res = re.search(r'\sDuration: (?P<duration>\S+)', line)
        if duration_res is not None:
            duration = duration_res.groupdict()['duration']
            duration = re.sub(r',', '', duration)

        result = re.search(r'\stime=(?P<time>\S+)', line)
        if result is not None:
            elapsed_time = result.groupdict()['time']
            progress = (get_seconds(elapsed_time) / get_seconds(duration)) * 100
            print(elapsed_time)
            print(progress)
            # content.set("进度:%3.2f" % progress + "%")
            p1["value"] = progress
            root.update()
    process.wait()
    if process.poll() == 0:
        infile_path = temp_path + temp_music_name + ".wav"
        outfile_path = "WAV\\" + music_name + ".wav"

        del_wavparm(infile_path, outfile_path)

        elapsed = (time.perf_counter() - start_time)
        print("耗时:%6.2f" % elapsed + "秒")
        content.set("耗时:%6.2f" % elapsed + "秒")
        del_file(temp_path)
        print("success:", process)
        # 设置终点
        p1["value"] = 115
    else:
        print("error:", process)
    # 恢复网络按钮
    buttonOpenUrl.config(state="normal")


s = ttk.Style()
s.theme_use('alt')
s.configure("blue.Vertical.TProgressbar", troughcolor=progress_color, background=progress_chunk_color,
            troughrelief="flat")
p1 = ttk.Progressbar(root, style="blue.Vertical.TProgressbar", length=115, mode="determinate", orient="vertical")
p1.place(x=368, y=0, width=5, height=height)

buttonStart = tk.Button(L_frame, text="本地转换", command=start, font=m_font, bd=0, bg=btn_color, fg=font_color,
                        activeforeground=font_color,
                        activebackground=frame_color)
buttonStart.place(x=268, y=200, width=75, height=30)

help_str = "使用指南\n1.本地音频转换：打开选择本地文件，开始进行转换\n2.网络分享音频：支持全民K歌、唱吧、荔枝FM、喜马拉雅FM"
labShow = tk.Label(L_frame, text=help_str, wraplength=313, justify="left", font=s_font, bd=1, relief="solid",
                   bg=frame_color,
                   fg=font_color)
labShow.place(x=30, y=25, width=313, height=70)

declare_str = "声明：仅供个人录制音频转换使用"
labDeclare = tk.Label(R_frame, text=declare_str, wraplength=151, justify="left", font=s_font, bd=1, relief="solid",
                      bg=frame_color,
                      fg=declare_color)
labDeclare.place(x=40, y=282, width=151, height=41)


def show_file_path():
    subprocess.run(['explorer.exe', '/n,WAV'])


buttonFile = tk.Button(L_frame, text="浏览输出", command=show_file_path, font=s_font, bd=0, bg=btn_color,
                       fg=font_color,
                       activeforeground=font_color,
                       activebackground=frame_color)
buttonFile.place(x=268, y=291, width=75, height=23)


def open_browser(event):
    open_url = update_url.get()
    if open_url != "":
        print(open_url)
        webbrowser.open(open_url)


def update_fun():
    try:
        url = "https://space9.gitee.io/sharesoftware/s/version.json"

        headers = {
            'Host': "space9.gitee.io",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        response = requests.request("GET", url, headers=headers)

        print(response.text)
        version_data = json.loads(response.text)
        latest_version = version_data["latestVersion"]
        if version != latest_version:
            print(version_data["downUrl"])
            update_info.set(version_data["info"])
            update_url.set(version_data["downUrl"])
        else:
            update_info.set("已是最新版本:" + version)
            update_url.set(version_data["downUrl"])
    except Exception as e:
        print("网络未连接，请检查连接后重试")
        print(e)
        update_info.set("已是最新版本:" + version)


update_info = tk.StringVar()
update_url = tk.StringVar()
update_info.set("检测更新中......")

# 创建
t = threading.Thread(target=update_fun)
# 守护 !!!
t.setDaemon(True)
# 启动
t.start()

updateLab = tk.Label(R_frame, textvariable=update_info, font=l_font, bg=update_bg_color, fg=update_color)
updateLab.place(x=0, y=0, width=230, height=25)
updateLab.bind("<Button-1>", open_browser)

# 启动消息循环
root.mainloop()
