#!/usr/bin/python3
# -*- coding:utf-8 -*-
from app import app
from flask import render_template, redirect, request, session, flash, redirect, url_for
import requests, json

aiguilleur = "http://192.168.43.61:8000"#serveur de dispatching des requêtes
#groupe de variable pour la réactualisation des salons
received = False
listRooms = []
last_listRooms = []
is_first = False
tailleDiff = 0
reponseRooms = []#objet de type requests.get

#groupe de variable pour la réactualisation des messages
received2 = False
listRooms2 = []
last_listRooms2 = []
tailleDiff2 = 0
reponseRooms2 = []#objet de type requests.get

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		#inscription dans le chatroom via webService
		session['pseudo'] = request.form['pseudo']
		session['newRooms'] = []
		session['newRooms2'] = []
		print(session['pseudo'])
		res = requests.get(aiguilleur+'/subscribe?login='+str(session['pseudo']))
		login = json.loads(res.text)
		print(login['response'])
		if login['response'] != "login exist":	
			return redirect('/chatroom')
		else:
			flash(u'Ce login entré existe déja. Veuillez le changer SVP')
			return render_template('login.html')

	return render_template('login.html')

@app.route('/chatroom')
def chatRoom():
	if 'pseudo' in session:
		return render_template('chatRoom.html')

	return redirect('/index')

@app.route('/disconnect')
def logout():
	global last_listRooms
	global last_listRooms2
	global tailleDiff
	global tailleDiff2
	global is_first
	global is_first2
	res = requests.post(aiguilleur+'/unSubscribe?login='+str(session['pseudo']))
	print(res.text)
	last_listRooms = []
	last_listRooms2 = []
	tailleDiff = 0
	tailleDiff2 = 0
	is_first = False
	is_first2 = False

	session.pop('pseudo', None)
	session.pop('salon', None)
	return redirect('/')

@app.route('/chatroom/<room>')
def enterRoom(room):
	if 'pseudo' not in session:
		return redirect('/index')
	print(room)
	session['salon'] = room
	session['newRooms2'] = []
	session['last_listRooms2'] = []
	session['is_first2'] = False
	res = requests.get(aiguilleur+'/getMessagesSalon?login='+str(session['pseudo'])+"&salon="+str(session['salon']))
	print(res.url)

	return res.text

@app.route('/chatroom/addroom')
def addRoom():
	if 'pseudo' not in session:
		return redirect('/index')
	"""Ajout de salon de discussion"""
	new_salon = request.args.get('salon');
	print(new_salon)
	#params = {'login': session['pseudo'], 'nomSalon': new_salon}
	res = requests.post(aiguilleur+str('/addSalon?login=')+str(session['pseudo'])+str('&nomSalon=')+str(new_salon))# envoi de requête à l'aiguilleur
	print(res.url)
	return res.text


@app.route('/chatroom/sendmsg')
def sendMsg():
	if 'pseudo' not in session:
		return redirect('/index')
	message = request.args.get('message')
	salon = request.args.get('salon')
	print(message)
	res = requests.post(aiguilleur+str('/sendMessage?login=')+str(session['pseudo'])+str("&nomSalon=")+str(session['salon'])+str("&message=")+str(message))
	print(res.url)
	return res.text

@app.route('/chatroom/rcvmsg/')
def rcvMsg():
	if 'pseudo' not in session:
		return redirect('/index')
	global tailleDiff2
	global last_listRooms2
	global received2
	session['newRooms2'] = []

	#Si aucun salon n'a été choisi au paravant
	if 'salon' not in session:
		return json.dumps([])
	try:
		reponseRooms2 = requests.get(aiguilleur+str('/getMessagesSalon?login=')+str(session['pseudo'])+"&salon="+session['salon'])
		listRooms2 = reponseRooms2.json()
		print(listRooms2)
		received2 = True
		if session['is_first2']==False:
			last_listRooms2 = list(listRooms2)
		print(reponseRooms2.url)
	except:
		received2 = False
	finally:
		if received2:
			print("In received messages")
			if session['is_first2']:
				if len(last_listRooms2)!=len(listRooms2):
					tailleDiff2 = len(listRooms2)-len(last_listRooms2)
					for i in range(len(listRooms2)):
						if listRooms2[i] not in last_listRooms2:
							session['newRooms2'].append(listRooms2[i])
					last_listRooms2 = list(listRooms2)
				else:
					last_listRooms2 = list(listRooms2)
					session['newRooms2'] = []#le cas où il n'y a pas de nouveaux messages
			else:
				session['newRooms2'] = list(listRooms2)
				last_listRooms2 = list(listRooms2)
				session['is_first2'] = True

		return json.dumps(session['newRooms2'])


@app.route('/chatroom/rcvroom')
def rcvGroup():
	if 'pseudo' not in session:
		return redirect('/index')
	global tailleDiff
	global last_listRooms
	global is_first
	global received
	session['newRooms'] = []
	try:
		reponseRooms = requests.get(aiguilleur+str('/getRooms'))
		listRooms = reponseRooms.json()
		received = True
		if is_first==False:
			last_listRooms = list(listRooms)
		
	except:
		received = False
	finally:
		#récuperer les salons fraichement ajoutés
		if received:
			if is_first:
				if len(last_listRooms)!=len(listRooms):
					tailleDiff = len(listRooms)-len(last_listRooms)
					#body .......
					for i in range(len(listRooms)):
						if listRooms[i] not in last_listRooms:
							session['newRooms'].append(listRooms[i])
					last_listRooms = list(listRooms)
				else:
					last_listRooms = list(listRooms)
					session['newRooms'] = []#le cas où aucun nouveau salon n'est ajouté
			else:
				session['newRooms'] = list(listRooms)
				last_listRooms = list(listRooms)
				is_first = True

		return json.dumps(session['newRooms'])

@app.route('/chatroom/reload')
def reload():
	if 'pseudo' not in session:
		return redirect('/index')
	reponseRooms = requests.get(aiguilleur+str('/getRooms'))
	listRooms = reponseRooms.json()
	return json.dumps(listRooms)
