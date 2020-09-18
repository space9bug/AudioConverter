pip install pyinstaller -i "https://pypi.tuna.tsinghua.edu.cn/simple"

pip install requests -i "https://pypi.tuna.tsinghua.edu.cn/simple"

pyinstaller -D -w -i "resources\logo.ico" AudioConverter.py Amusic.py --add-data "resources\7z.dll;." --add-data "resources\7z.exe;." --add-data "resources\aria2c.exe;." --add-data "resources\logo.ico;."

cd Inno Setup 6
iscc "..\setup.iss"

