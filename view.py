from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from urllib import request as req
from pyquery import PyQuery as pq
import pickle as p
import os

app = Flask(__name__)

bootstrap = Bootstrap(app)
moment = Moment(app)

printerDictionary= {'physical':{'ip':'','statu':'','cartridge':''}}
printeraddressFile= 'IPaddress.data'
if os.path.exists(printeraddressFile):
    f= open(printeraddressFile,'rb')
    printerDictionary= p.load(f)
else:
    f= open(printeraddressFile,'wb')
    p.dump(printerDictionary,f)
    f.close()

class printer:
    def __init__(self,physical,ip= 'None',statu='None',cartridge='None'):
        printerDictionary[physical]= {'ip':ip,'statu':statu,'cartridge':cartridge}

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/index', methods=['GET', 'POST'])
def index():
    form = request.form['menu']
    if form=='1':
        return render_template('addprinter.html')
    if form=='2':
        return render_template('delprinter.html')
    if form=='3':
        return redirect(url_for('display'))
    if form=='4':
        return redirect(url_for('cartridge'))
    return render_template('index.html',name=form)

@app.route('/', methods=['GET', 'POST'])
def menu():
    return render_template('index.html')

@app.route('/addprinter', methods=['GET', 'POST'])
def addprinter():
    addphysical = request.form['physical']
    addip = request.form['ip']
    printer(addphysical, addip)
    f = open(printeraddressFile, 'wb')
    p.dump(printerDictionary, f)
    f.close()
    return redirect(url_for('menu'))

@app.route('/delprinter', methods=['GET', 'POST'])
def delprinter():
    delphysical = request.form['delphysical']
    if delphysical in printerDictionary:
        del printerDictionary[delphysical]
        f = open(printeraddressFile, 'wb')
        p.dump(printerDictionary, f)
        f.close()
        return redirect(url_for('menu'))
    else:
        noprinter='没有这个打印机'
        return render_template('index.html', name=noprinter)

@app.route('/display', methods=['GET', 'POST'])
def display():
    for physical in printerDictionary:
        url = 'http://%s/hp/device/this.LCDispatcher' % (printerDictionary[physical]['ip'])
        response = req.urlopen(url)
        printer = response.read()
        doc = pq(printer)
        data = doc('body')
        for body in data.items():
            stat = body('div').eq(30).text()
            printerDictionary[physical]['statu'] = stat
    prlist=[]
    for physical in printerDictionary:
        prlist.append('物理名：%s,IP：%s,状态：%s <br/>' % (physical, printerDictionary[physical]['ip'], printerDictionary[physical]['statu']))
    return render_template('display.html', name=prlist)

@app.route('/cartridge', methods=['GET', 'POST'])
def cartridge():
    for physical in printerDictionary:
        url = 'http://%s/hp/device/this.LCDispatcher' % (printerDictionary[physical]['ip'])
        response = req.urlopen(url)
        printer = response.read()
        doc = pq(printer)
        data = doc('body')
        for body in data.items():
            cartridge = body('div').eq(35).text()
            #move = dict.fromkeys((ord(c) for c in u"\xa0\n\t"))
            trans = "  ".join(cartridge.split())
            #trans = cartridge.translate(move)
            printerDictionary[physical]['cartridge'] = trans
    prlist = []
    for physical in printerDictionary:
        prlist.append('物理名：%s,墨盒状态：%s <br/>' % (physical, printerDictionary[physical]['cartridge']))
    return render_template('display.html', name=prlist)
