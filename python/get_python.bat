c:
mkdir C:\mbplugin\python
cd C:\mbplugin\python

@REM ������� � ����������� � C:\mbplugin\python:https://www.python.org/ftp/python/3.8.3/python-3.8.3-embed-win32.zip
curl -LOk https://www.python.org/ftp/python/3.8.3/python-3.8.3-embed-win32.zip
7z x python-3.8.3-embed-win32.zip

@REM ������� https://bootstrap.pypa.io/get-pip.py � C:\mbplugin\python
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

@REM �������� C:\mbplugin\python ��������� 
python get-pip.py

@REM � ����� C:\mbplugin\python\python38._pth ���������������� (������ #) import site
python -c "d=open('python38._pth').read();open('python38._pth','w').write(d.replace('#import site','import site'))"

@REM �������� C:\mbplugin\python ��������� 
python -m pip install requests pillow beautifulsoup4 pyodbc pyreadline

@REM � ��������� �� ����� ��������� ���������� �� ��������� tkinter ������ ���������� �� �������������� python
@rem https://stackoverflow.com/questions/37710205/python-embeddable-zip-install-tkinter


