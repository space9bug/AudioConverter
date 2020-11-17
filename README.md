# AudioConverter
嗖音HOME(原名：Soul录音格式转换器)

# 版本发布
最新版下载链接：https://sourl.cn/DeKdhs

V3.2.1 增加ffmpeg-win64、钉钉群机器人和飞书群机器人

V3.2.0 适配macOS平台，并使用线程执行转换过程

V3.1.1 增加随机文章阅读和埋点统计，并支持更多网络分享音频

V3.1.0 更名为嗖音HOME，重构代码（界面与逻辑分离），修复反馈信息出现空行的问题，减小安装包体积（在线加载组件）

V3.0.1 界面版首次发布

V3.0 增加gui可视化界面，使用python语言实现

V2.1 提升了音质

V2.0 解决了文件头信息（使用ffmpeg转换的音频文件头会默认增加扩展信息）导致音频开头出现杂音的问题

V1.0 首次发布

# 使用方法

## 构建环境
- python 3.9.0
- pyinstaller 4.0
- 第三方库依赖：requests

## 使用pyinstaller进行构建
构建命令：pyinstaller -D -w -i logo.ico AudioConverter.py Amusic.py

在dist/AudioConverter目录中，添加以下文件，即可运行

7z.dll

7z.exe

aria2c.exe

logo.ico

# 反馈信息api
- 钉钉机器人文档：https://ding-doc.dingtalk.com/doc#/serverapi2/krgddi
- 与你机器人文档：http://www.uneed.com/openapi/pages/index.html#/chatbot/intro
- 飞书机器人文档：https://www.feishu.cn/hc/zh-CN/articles/360024984973-%E6%9C%BA%E5%99%A8%E4%BA%BA-%E5%A6%82%E4%BD%95%E5%9C%A8%E7%BE%A4%E8%81%8A%E4%B8%AD%E4%BD%BF%E7%94%A8%E6%9C%BA%E5%99%A8%E4%BA%BA-#source=section
- 企业微信机器人文档：https://work.weixin.qq.com/api/doc/90000/90136/91770

# 文件资源
logo.ico https://www.easyicon.net/1225972-music_icon.html

7-Zip https://www.7-zip.org/

aria2c.exe https://aria2.github.io/

ffmpeg.exe https://ffmpeg.zeranoe.com/builds/

# 使用声明
仅供个人录制音频转换使用
