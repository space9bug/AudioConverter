# AudioConverter
嗖音HOME(原名：Soul录音格式转换器)

# 版本发布
V3.1.0 更名为嗖音HOME，重构代码（界面与逻辑分离），修复反馈信息出现空行的问题，减小安装包体积（在线加载组件）
https://474b.com/file/20114131-440602208

V3.0.1 界面版首次发布
https://474b.com/file/20114131-414434508

V3.0 增加gui可视化界面，使用python语言实现

V2.1 提升了音质
https://474b.com/file/20114131-399684744

V2.0 解决了文件头信息（使用ffmpeg转换的音频文件头会默认增加扩展信息）导致音频开头出现杂音的问题
https://474b.com/file/20114131-373000858

V1.0 首次发布
https://474b.com/file/20114131-373000097

# 使用方法

## 构建环境
- python 3.7.7
- pyinstaller 3.6
- 第三方库依赖：requests

## 使用pyinstaller进行构建
构建命令：pyinstaller -D -w -i logo.ico AudioConverter.py

在build目录中，添加以下文件，即可运行

7z.dll

7z.exe

aria2c.exe

WAV(空文件夹)

logo.ico

# 反馈信息api
- 钉钉机器人文档：https://ding-doc.dingtalk.com/doc#/serverapi2/krgddi
- 与你机器人文档：http://www.uneed.com/openapi/pages/index.html#/chatbot/intro

# 文件资源
logo.ico https://www.easyicon.net/1225972-music_icon.html

7-Zip https://www.7-zip.org/

aria2c.exe https://aria2.github.io/

ffmpeg.exe https://ffmpeg.zeranoe.com/builds/

# 使用声明
仅供个人录制音频转换使用
