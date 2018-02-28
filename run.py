#coding=utf-8
#!/usr/bin/python
from view import app  #somewhere 表示的包含Flask的实例，如app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)