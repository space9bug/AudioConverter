import glob
import json
import os
import random
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

import requests

import Amusic


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


def burying_point():
    # print("埋点统计")
    bury_url = "https://sourl.cn/NcRtPm"
    cookie_file_name = "cookie.json"

    if os.path.exists(cookie_file_name):
        with open(cookie_file_name, "r", encoding="utf-8") as load_file:
            load_dict = json.load(load_file)
            # print(load_dict)

        headers = {
            'Cookie': 'xm_v=' + load_dict["xm_v"]
        }

        response = requests.request("GET", bury_url, headers=headers, allow_redirects=False)
        print(response.elapsed.total_seconds())
    else:
        # 第一次请求，获取cookie并保存
        session = requests.session()
        session.get(bury_url, allow_redirects=False)
        set_cookie = requests.utils.dict_from_cookiejar(session.cookies)
        print(set_cookie)

        with open(cookie_file_name, "w", encoding="utf-8") as out_file:
            json.dump(set_cookie, out_file)


def show_file_path():
    subprocess.run(['explorer.exe', '/n,WAV'])


def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
    os.rmdir(path)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.version = "V3.1.1"
        self.sampling_rate_ver = tk.IntVar()
        self.content = tk.StringVar()
        self.update_url = tk.StringVar()
        self.update_info = tk.StringVar()
        self.read_url = ""
        self.read_str = tk.StringVar()

        # 创建一个顶级弹窗
        self.withdraw()
        self.top = tk.Toplevel()
        self.top.title("请勿关闭")
        self.top.iconbitmap("logo.ico")
        self.top.attributes("-alpha", 0.99)

        def close_fun():
            ans = messagebox.askokcancel(title="警告", message="首次使用需要网络，确定要关闭吗？")
            if ans:
                self.top.destroy()
                self.destroy()

        self.top.protocol("WM_DELETE_WINDOW", close_fun)
        # 设置窗口大小
        width = 301
        height = 169
        # 获取屏幕尺寸以计算布局参数，使窗口居于屏幕中央
        screenwidth = self.top.winfo_screenwidth()
        screenheight = self.top.winfo_screenheight()
        geometry_str = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 3)
        self.top.geometry(geometry_str)
        self.top.resizable(width=False, height=False)

        tk.Label(self.top, text="首次使用会自动下载一些工具文件，可\r\n能需要等待一分钟左右，过程中请保持\r\n网络正常连接，请稍等。。。。。。", wraplength=280,
                 justify="left", font=("宋体", 12), fg="red").pack(pady=10)

        self.downBar = ttk.Progressbar(self.top, length=110, mode="determinate")
        self.downBar.pack(fill=tk.X, padx=25, pady=15)
        self.top.withdraw()

        # 创建
        t2 = threading.Thread(target=self.init_fun)
        # 守护 !!!
        t2.setDaemon(True)
        # 启动
        t2.start()

        self.createWidgets()

    def init_fun(self):
        # 创建输出文件夹
        mkdir("WAV\\")

        # print("开始下载ffmpeg包")
        if not os.path.exists("ffmpeg.exe"):
            self.top.deiconify()
            try:
                str_out = ['aria2c.exe', '-o', "ffmpeg.7z",
                           "https://ncstatic.clewm.net/rsrc/2020/0520/14/0b9f34392178f1c5aaee7baaa677da05.obj"]
                print(str_out)
                si = subprocess.STARTUPINFO()
                si.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = subprocess.SW_HIDE
                process = subprocess.Popen(str_out, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           encoding="utf-8",
                                           text=True, startupinfo=si)
                for line in process.stdout:
                    # print(line)

                    status_res = re.search(r'\((?P<status>[\s\S]*?)\):', line)
                    if status_res is not None:
                        if status_res.groupdict()['status'] == "ERR":
                            raise Exception("下载错误")

                    percent_res = re.search(r'\((?P<percent>[\s\S]*?)%\)', line)
                    if percent_res is not None:
                        progress = percent_res.groupdict()['percent']
                        print(progress)
                        self.downBar["value"] = progress
                        self.top.update()
                process.wait()
                if process.poll() == 0:
                    # 解压文件
                    str_out = ['7z.exe', 'x', "ffmpeg.7z"]
                    print(str_out)
                    si = subprocess.STARTUPINFO()
                    si.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
                    si.wShowWindow = subprocess.SW_HIDE
                    process_1 = subprocess.Popen(str_out, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                 encoding="utf-8",
                                                 text=True, startupinfo=si)
                    process_1.wait()
                    if process_1.poll() == 0:
                        for item_7z in glob.glob("ffmpeg*.7z"):
                            os.remove(item_7z)
                        print("解压完成")
                        self.downBar["value"] = 110
                        self.top.destroy()
                        self.deiconify()
            except Exception as e:
                print("网络未连接，请检查连接后重试")
                print(e)
                self.top.withdraw()
                messagebox.showwarning(title="警告", message="网络未连接，请检查连接后重试（首次使用需要网络）")
                self.top.destroy()
                self.destroy()
        else:
            self.top.destroy()
            self.deiconify()

    def createWidgets(self):
        self.title("嗖音HOME " + self.version[1:] + " - 独居者")
        self.iconbitmap("logo.ico")
        self.attributes("-alpha", 0.99)
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
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry_str = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 3)
        self.geometry(geometry_str)
        self.resizable(width=False, height=False)
        L_frame = tk.Frame(width=373, height=height, bg=frame_color)
        R_frame = tk.Frame(width=230, height=height, bg=frame_color)
        L_frame.grid(row=0, column=0)
        R_frame.grid(row=0, column=1)

        self.update_info.set("检测更新中......")

        # 创建
        t = threading.Thread(target=self.update_fun)
        read_t = threading.Thread(target=self.read_fun)
        # 守护 !!!
        t.setDaemon(True)
        read_t.setDaemon(True)
        # 启动
        t.start()
        read_t.start()

        # 右边开始布局
        updateLab = tk.Label(R_frame, textvariable=self.update_info, font=l_font, bg=update_bg_color, fg=update_color)
        updateLab.place(x=0, y=0, width=230, height=25)
        updateLab.bind("<Button-1>", self.open_browser)

        self.text = tk.Text(R_frame, width=5, height=5, bd=1, relief="solid", font=s_font, bg=frame_color,
                            fg=font_color)
        self.text.place(x=30, y=50, width=170, height=155)
        self.text.insert(tk.INSERT, "有什么想对开发者说的可以说")
        self.text.bind("<Button-1>", self.del_show)

        buttonSend = tk.Button(R_frame, text="给开发者的话", command=self.send_message, font=m_font, bd=0, bg=btn_color,
                               fg=font_color,
                               activeforeground=font_color, activebackground=frame_color)
        buttonSend.place(x=65, y=230, width=101, height=30)

        declare_str = "声明：仅供个人录制音频转换使用"
        labDeclare = tk.Label(R_frame, text=declare_str, wraplength=151, justify="left", font=s_font, bd=1,
                              relief="solid",
                              bg=frame_color,
                              fg=declare_color)
        labDeclare.place(x=40, y=282, width=151, height=41)

        # 左边开始布局
        self.read_str.set("随机阅读：正在加载中......")
        labShow = tk.Label(L_frame, textvariable=self.read_str, wraplength=252, justify="left", anchor="w", padx=5,
                           bd=1,
                           relief="solid",
                           bg=frame_color,
                           fg=font_color)
        labShow.place(x=30, y=25, width=313, height=70)

        labReadAll = tk.Label(L_frame, text="查看全文", bg=frame_color, fg="#22B14C")
        labReadAll.place(x=287, y=26, width=55, height=68)
        labReadAll.bind("<Button-1>", self.read_page)

        self.content.set("请选择要转换的音频文件")
        lab = tk.Label(L_frame, textvariable=self.content, font=m_font, bg=frame_color, fg=font_color)
        lab.place(x=30, y=110, width=313, height=20)

        self.entry_url = tk.Entry(L_frame, validate="focusin", validatecommand=self.del_url_show, font=s_font, bd=1,
                                  relief="solid",
                                  bg=frame_color,
                                  fg=font_color)
        self.entry_url.place(x=30, y=160, width=238, height=30)
        self.entry_url.insert(0, "请输入分享链接即可")

        self.buttonOpenUrl = tk.Button(L_frame, text="网络转换", command=self.urlfile_convert, font=m_font, bd=0,
                                       bg=btn_color,
                                       fg=font_color,
                                       activeforeground=font_color,
                                       activebackground=frame_color)
        self.buttonOpenUrl.place(x=268, y=160, width=75, height=30)

        self.buttonStart = tk.Button(L_frame, text="本地转换", command=self.localfile_convert, font=m_font, bd=0,
                                     bg=btn_color,
                                     fg=font_color,
                                     activeforeground=font_color,
                                     activebackground=frame_color)
        self.buttonStart.place(x=268, y=200, width=75, height=30)

        buttonOpen = tk.Button(L_frame, text="打开本地文件", command=self.openfile, font=m_font, bd=0, bg=btn_color,
                               fg=font_color,
                               activeforeground=font_color,
                               activebackground=frame_color)
        buttonOpen.place(x=110, y=200, width=101, height=30)

        labOut = tk.Label(L_frame, text="输出配置：", justify="left", font=m_font, bg=frame_color, fg=font_color)
        labOut.place(x=30, y=250, width=75, height=30)

        buttonVer = tk.Checkbutton(L_frame, text="旧版", font=m_font, variable=self.sampling_rate_ver, bg=frame_color,
                                   fg=font_color,
                                   activeforeground=font_color, activebackground=frame_color,
                                   selectcolor=frame_color)
        buttonVer.place(x=110, y=250, width=71, height=30)

        buttonFile = tk.Button(L_frame, text="浏览输出", command=show_file_path, font=s_font, bd=0, bg=btn_color,
                               fg=font_color,
                               activeforeground=font_color,
                               activebackground=frame_color)
        buttonFile.place(x=268, y=291, width=75, height=23)

        labHelp = tk.Label(L_frame, text="<使用指南>", font=s_font, bg=frame_color, fg=font_color)
        labHelp.place(x=10, y=306, width=75, height=23)
        labHelp.bind("<Button-1>", self.show_help)

        progressbar_style = ttk.Style()
        progressbar_style.theme_use('alt')
        progressbar_style.configure("blue.Vertical.TProgressbar", troughcolor=progress_color,
                                    background=progress_chunk_color,
                                    troughrelief="flat")
        self.progressBar = ttk.Progressbar(self, style="blue.Vertical.TProgressbar", length=115, mode="determinate",
                                           orient="vertical")
        self.progressBar.place(x=368, y=0, width=5, height=height)

    # 反馈信息发送函数，具体实现可以自定义，钉钉机器人和与你机器人均可
    # 钉钉机器人文档：https://ding-doc.dingtalk.com/doc#/serverapi2/krgddi
    # 与你机器人文档：http://www.uneed.com/openapi/pages/index.html#/chatbot/intro
    def send_message(self):
        try:
            # print(self.text.get("1.0", "end").strip('\n'))
            msg = self.text.get("1.0", "end").strip('\n')
            if msg == "" or msg == "有什么想对开发者说的可以说":
                messagebox.showwarning(title="警告", message="请输入内容后发送")
                return

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

    def del_show(self, event):
        print(event)
        self.text.delete("1.0", "end")

    def del_url_show(self):
        self.entry_url.delete(0, "end")

    def urlfile_convert(self):
        # 禁用本地转换按钮
        self.buttonStart.config(state="disabled")
        music_url = self.entry_url.get()
        if music_url == "" or music_url == "请输入分享链接即可":
            messagebox.showwarning(title="警告", message="请输入分享链接后执行")
            # 恢复本地转换按钮
            self.buttonStart.config(state="normal")
            return
        self.progressBar["value"] = 0
        self.content.set("请选择要转换的音频文件")
        self.update()
        try:
            music_data = Amusic.get_all_music_parm(music_url)
            if music_data[0] == "null" and music_data[1] == "null":
                print("不支持此分享链接或者链接格式错误")
                messagebox.showwarning(title="警告", message="不支持此分享链接或者链接格式错误")
                # 恢复本地转换按钮
                self.buttonStart.config(state="normal")
                return
            music_name = music_data[0]
            music_play_url = music_data[1]
        except Exception as e:
            print("网络未连接，请检查连接后重试")
            print(e)
            messagebox.showwarning(title="警告", message="网络未连接，请检查连接后重试")
            # 恢复本地转换按钮
            self.buttonStart.config(state="normal")
            return
        self.content.set(music_name)
        # 开始转换
        ##########################################################################################################
        start_time = time.perf_counter()
        sampling_rate = "48000"
        if self.sampling_rate_ver.get() == 1:
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
        process = subprocess.Popen(str_out, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   encoding="utf-8",
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
                self.progressBar["value"] = progress
                self.update()
        process.wait()
        if process.poll() == 0:
            infile_path = temp_path + temp_music_name + ".wav"
            outfile_path = "WAV\\" + music_name + ".wav"

            del_wavparm(infile_path, outfile_path)

            elapsed = (time.perf_counter() - start_time)
            print("耗时:%6.2f" % elapsed + "秒")
            self.content.set("耗时:%6.2f" % elapsed + "秒")
            del_file(temp_path)
            print("success:", process)
            # 设置终点
            self.progressBar["value"] = 115
        else:
            print("error:", process)
        # 恢复本地转换按钮
        self.buttonStart.config(state="normal")

    def openfile(self):
        # print("文本框内容：" + entry_url.get())
        file_path = filedialog.askopenfilename(title="选择音频文件")
        filename = os.path.basename(file_path)
        self.name = file_path
        print(self.name)
        self.content.set(filename)

    def localfile_convert(self):
        # 禁用网络转换按钮
        self.buttonOpenUrl.config(state="disabled")
        start_time = time.perf_counter()
        if not self.name:
            messagebox.showwarning(title="警告", message="请先选择文件后执行")
            # 恢复网络转换按钮
            self.buttonOpenUrl.config(state="normal")
            return
        self.progressBar["value"] = 0
        self.update()
        sampling_rate = "48000"
        if self.sampling_rate_ver.get() == 1:
            sampling_rate = "32000"
        temp_path = "TEMP\\"
        mkdir(temp_path)
        music_name = os.path.splitext(os.path.basename(self.name))[0]
        temp_music_name = str(round(time.time() * 1000))
        str_out = ['ffmpeg.exe', '-i', self.name, '-ar', sampling_rate, '-ac', '1', '-acodec', 'pcm_s16le',
                   '-hide_banner',
                   temp_path + temp_music_name + ".wav"]
        print(str_out)
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        process = subprocess.Popen(str_out, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   encoding="utf-8",
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
                self.progressBar["value"] = progress
                self.update()
        process.wait()
        if process.poll() == 0:
            infile_path = temp_path + temp_music_name + ".wav"
            outfile_path = "WAV\\" + music_name + ".wav"

            del_wavparm(infile_path, outfile_path)

            elapsed = (time.perf_counter() - start_time)
            print("耗时:%6.2f" % elapsed + "秒")
            self.content.set("耗时:%6.2f" % elapsed + "秒")
            del_file(temp_path)
            print("success:", process)
            # 设置终点
            self.progressBar["value"] = 115
        else:
            print("error:", process)
        # 恢复网络转换按钮
        self.buttonOpenUrl.config(state="normal")

    def open_browser(self, event):
        print(event)
        open_url = self.update_url.get()
        if open_url != "":
            webbrowser.open(open_url)

    def read_fun(self):
        pre_url = "https://blog.csdn.net/qq_41730930"
        try:
            read_data_url = "https://sourl.cn/GL53FH"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
            }
            res = requests.request("GET", read_data_url, headers=headers, allow_redirects=False)
            location_url = res.headers["Location"]

            response = requests.request("GET", location_url, headers=headers)
            response.encoding = "utf-8"

            response_code = response.status_code
            if response_code == 200:
                read_data = json.loads(response.text)
                if read_data is not None:
                    read_index = random.randint(0, len(read_data) - 1)
                    article_title = read_data[read_index][0]
                    if article_title is not None:
                        self.read_str.set("随机阅读：" + article_title)

                    article_url = read_data[read_index][1]
                    if article_url is not None:
                        self.read_url = pre_url + "/article/details/" + article_url
                    else:
                        self.read_url = pre_url
                else:
                    self.read_url = pre_url
            else:
                self.read_url = pre_url
        except Exception as e:
            print("网络未连接，请检查连接后重试")
            print(e)
            self.read_url = pre_url

    def read_page(self, event):
        print(event)
        if self.read_url != "":
            webbrowser.open(self.read_url)

    def show_help(self, event):
        print(event)
        self.update()
        # 获取主窗口的左上角坐标
        origin_x = self.winfo_x()
        origin_y = self.winfo_y()
        # 获取主窗口的宽、高
        origin_width = self.winfo_width()
        origin_height = self.winfo_height()
        # 设置窗口大小
        width = 300
        height = 169

        # 创建一个顶级弹窗
        helpTop = tk.Toplevel()
        helpTop.title("使用指南")
        helpTop.iconbitmap("logo.ico")
        helpTop.attributes("-alpha", 0.99)

        geometry_str = '%dx%d+%d+%d' % (
            width, height, origin_x + (origin_width - width) / 2, origin_y + (origin_height - height) / 2)
        helpTop.geometry(geometry_str)
        helpTop.resizable(width=False, height=False)
        helpTop.focus_set()

        help_str = "使用指南\n1.本地音频转换：打开选择本地文件，开始进行转换\n2.网络分享音频：支持唱鸭、全民K歌、唱吧、荔枝、喜马拉雅、斗歌、酷狗唱唱、猫爪弹唱、弹唱达人、爱唱、闪歌、VV音乐、爱听、酷狗音乐大字版、酷我K歌、全民K诗、天籁K歌、咪咕K歌、酷狗K歌"
        helpMessage = tk.Message(helpTop, text=help_str, justify="left", width=260)
        helpMessage.place(x=0, y=0, width=300, height=169)

    def update_fun(self):
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
            if self.version != latest_version:
                print(version_data["downUrl"])
                self.update_info.set(version_data["info"])
                self.update_url.set(version_data["downUrl"])
            else:
                self.update_info.set("已是最新版本:" + self.version)
                self.update_url.set(version_data["downUrl"])

            burying_point()
        except Exception as e:
            print("网络未连接，请检查连接后重试")
            print(e)
            self.update_info.set("已是最新版本:" + self.version)


if __name__ == '__main__':
    app = Application()
    app.mainloop()
