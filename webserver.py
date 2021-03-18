from flask import Flask
from flask import render_template, url_for, request, flash, redirect
import sqlite3
import transferserver
import chatserver
import _thread
import threading
import multiprocessing


app = Flask(__name__)
app.secret_key = "supersecretkey"


all_processes = []

def createTableData():

    items = []

    conn = sqlite3.connect('serversdatabase.db')
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM servers')
        conn.commit()
    except:
        cur.execute("CREATE TABLE servers(name TEXT, type TEXT, port TEXT, status TEXT)")
        conn.commit()


    liste = cur.fetchall()

    for i in liste:
        templist = ['name', 'type', 'port', 'status']
        tempdict = {}

        cpt = 0
        for j in i:
            tempdict[templist[cpt]] = j
            cpt += 1

        items.append(tempdict)

    cur.close()
    conn.close()

    return items



def bootAllServers():

    global all_processes

    items = []

    conn = sqlite3.connect('serversdatabase.db')
    cur = conn.cursor()


    cur.execute('SELECT * FROM servers')
    conn.commit()

    liste = cur.fetchall()

    for i in liste:
        templist = []
        cpt = 0
        for j in i:
            templist.append(j)
            cpt += 1
        items.append(templist)


    cur.close()
    conn.close()

    for row in items:
        
        if row[3] == "Up":
        
            process = multiprocessing.Process(target=startOneServ, args=(row[0], row[1], row[2]))
            process.start()
            all_processes.append([process, row[0]])
           




@app.route("/backend/addServer", methods=['POST'])
def addServer():


    namevar = request.form['name']
    typevar = request.form['type']
    portvar = request.form['port']
    statusvar = "Down"

    conn = sqlite3.connect('serversdatabase.db')
    cur = conn.cursor()

    data = (namevar, typevar, portvar, statusvar)

    cur.execute("INSERT INTO servers(name, type, port, status) VALUES(?, ?, ?, ?)", data)

    conn.commit()

    cur.close()
    conn.close()

    flash("Server added.")

    headers = ["Server's name", "Server's type", 'Port', 'Status']

    return redirect(url_for('index'))
    return render_template('index.html', headers=headers, objects=createTableData())



@app.route("/backend/deleteServer", methods=['POST'])
def deleteServer():

    namevar = request.form['name']
    typevar = request.form['type']
    portvar = request.form['port']

    conn = sqlite3.connect('serversdatabase.db')
    cur = conn.cursor()

    data = (namevar, typevar, portvar)

    cur.execute('SELECT * FROM servers WHERE name = ? AND type = ? AND port = ?', data)
    conn.commit()

    liste = cur.fetchall()

    if len(liste) > 0:

        cur.execute('DELETE FROM servers WHERE name = ? AND type = ? AND port = ?', data)
        flash("Server deleted.")
        conn.commit()

    else:
        flash("Error. Please check and retry server's information.")

    headers = ["Server's name", "Server's type", 'Port', 'Status']


    return redirect(url_for('index'))
    return render_template('index.html', headers=headers, objects=createTableData())


def startOneServ(name, type, port):

    if type == "File transfer":
    
        x = name
        vars()[x] = name

        name = transferserver.Server(int(port))
        print(x + " started.")
        name.start()

        statusvar = "Up"

        conn = sqlite3.connect('serversdatabase.db')
        cur = conn.cursor()

        data = (statusvar, x, type, port)

        cur.execute('UPDATE servers SET status = ? WHERE name = ? AND type = ? AND port = ?', data)
        conn.commit()
        
    elif type == "Chat":
        
        x = name
        vars()[x] = name

        name = chatserver.listening_serv(int(port))

        print(x + " started.")

        name.run()

        statusvar = "Up"

        conn = sqlite3.connect('serversdatabase.db')
        cur = conn.cursor()

        data = (statusvar, x, type, port)

        cur.execute('UPDATE servers SET status = ? WHERE name = ? AND type = ? AND port = ?', data)
        conn.commit()


@app.route("/backend/startServer", methods=['POST'])
def startServer():
    
    global all_processes

    namevar = request.form['name']
    typevar = request.form['type']
    portvar = request.form['port']

    statusvar = "Up"

    conn = sqlite3.connect('serversdatabase.db')
    cur = conn.cursor()

    data = (statusvar, namevar, typevar, portvar)

    cur.execute('UPDATE servers SET status = ? WHERE name = ? AND type = ? AND port = ?', data)
    conn.commit()

    process = multiprocessing.Process(target=startOneServ, args=(namevar, typevar, portvar))
    process.start()
    all_processes.append([process, namevar])


    print(namevar + " started.")

    headers = ["Server's name", "Server's type", 'Port', 'Status']

    return redirect(url_for('index'))
    return render_template('index.html', headers=headers, objects=createTableData())


@app.route("/backend/stopServer", methods=['POST'])
def stopServer():
    
    global all_processes

    namevar = request.form['name']
    typevar = request.form['type']
    portvar = request.form['port']

    statusvar = "Down"

    conn = sqlite3.connect('serversdatabase.db')
    cur = conn.cursor()

    data = (statusvar, namevar, typevar, portvar)

    cur.execute('UPDATE servers SET status = ? WHERE name = ? AND type = ? AND port = ?', data)
    conn.commit()

    for proc in range(0, len(all_processes)):
        if all_processes[proc][1] == namevar:
            all_processes[proc][0].terminate()
            all_processes.pop(proc)

    headers = ["Server's name", "Server's type", 'Port', 'Status']

    return redirect(url_for('index'))
    return render_template('index.html', headers=headers, objects=createTableData())



@app.route("/backend/stopAllServers", methods=['POST'])
def stopAllServers():
    
    global all_processes


    statusvar = "Down"

    conn = sqlite3.connect('serversdatabase.db')
    cur = conn.cursor()
    
    data = (statusvar,)

    cur.execute('UPDATE servers SET status = ?', data)
    conn.commit()

    for proc in range(0, len(all_processes)):
        all_processes[proc][0].terminate()
        all_processes.pop(proc)

    headers = ["Server's name", "Server's type", 'Port', 'Status']

    return redirect(url_for('index'))
    return render_template('index.html', headers=headers, objects=createTableData())

@app.route('/')
def index():

    headers = ["Server's name", "Server's type", 'Port', 'Status']

    return render_template('index.html', headers=headers, objects=createTableData())



if __name__ == '__main__':

    boot = threading.Thread(target=bootAllServers)
    boot.start()

    app.run(debug=True)
