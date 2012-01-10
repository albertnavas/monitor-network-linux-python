#!/usr/bin/python
#-*- coding: utf-8 -*-

# Albert Navas Mallo
# hisi46997513

'''
Monser

• Detectar quins ordinadors estan funcionant a la xarxa mantenint l’historial de quan s’engeguen i quan s’apaguen.

• Detectar si moncli està activat a l’ordinador remot i, si cal, instal·lar-lo i activar-lo.
  
• Sol·licitar a moncli les dades d’ús del sistema.

• Guardar aquesta informació per a l’ús posterior. Un procés auxiliar pot, per
  exemple, alimentar una base de dades amb aquesta informació.
  
• Aturar el servidor (monser) actiu a petició de l’usuari.
'''
import socket, sys, select, os, time, sys, signal, paramiko, syslog, pg, datetime
from subprocess import Popen,  PIPE
from optparse import OptionParser

#Funciones

# Funció que surt del programa	
def kill(signum,frame):
	#print 'Sortir'
	s.close()
	sys.exit(0)

# Funció que rellegeix el fitxer de regles.txt
def rellegir(signum,frame):
	#print 'Rellegit el fitxer de regles'
	global strreglas
	strreglas = reglas_client(reglas())
	return

def nmap(ip):
	# Agafem totes les ips de la xarxa que es troben actives i les guardem en una llista
	while True:
		command= "nmap -sP -n %s | grep %s* | cut -f 5 -d ' '" %(ip,ip[0:9])
		tubo = Popen(command, shell = True, stdout = PIPE, stderr = PIPE)
		d_ips = {}
		ips=[]
		for linia in tubo.stdout.readlines():
			ip=linia.strip()
			ips.append(ip)

		return ips

def reglas():
	# Obtenim les regles del fitxer i les posem en un diccionari
	reglas={}
	try:
		fitxer = open(FILE, 'r')
	except:
		syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es pot obrir el fitxer de regles')

	for linia in fitxer:
		valors = linia.strip().split(' = ')
		reglas[valors[0]]= valors[1]
	fitxer.close()
	
	return reglas
	
def reglas_client(reglas):
	# Agafem el diccionari de les regles que hagin estat especificades amb un "si"
	# i les posem en una string per enviarla al client
	envreglas = []
	strreglas = ''
	
	if reglas['cpu'] == 'si':
		envreglas.append('cpu')
	if reglas['usuaris'] == 'si':
		envreglas.append('usuaris')
	if reglas['RAM/swap'] == 'si':
		envreglas.append('RAM/swap')
	if reglas['discs'] == 'si':
		envreglas.append('discs')
	
	strreglas = ' '.join(envreglas)
	
	return strreglas

def tractar_dades(dataok):
	# Tractem les dades rebudes del client per tal de posaro tot en llistes
	# Per poder diferenciar cada cosa correctament
	ll_cpu = []
	ll_discs = []
	ll_swap = ''
	ll_usuario = []
	ll_ram = ''
	ll_total = []
	liniaok = ''
	cpu = False
	usuario = False
	mem = False
	discs = False
	swap = False
	
	for linia in dataok.split('\n'):
		if linia == 'cpu':
			cpu = True
			usuario = False
			mem = False
			discs = False
			swap = False
		if linia == 'usuario':
			usuario = True
			cpu = False
			mem = False
			discs = False
			swap = False
			contusu = 0
		if linia == 'mem':
			mem = True
			cpu = False
			usuario = False
			discs = False
			swap = False
		if linia == 'discs':
			discs = True
			cpu = False
			usuario = False
			mem = False
			swap = False
			contdiscs = 0
		elif swap == True:
			ll_swap = linia.strip()
			swap = False
		elif cpu == True:
			if linia != '' and linia != 'cpu':
				ll_cpu = linia.strip().split(', ')
		elif usuario == True:
			if linia != '' and linia != 'usuario':
				ll_usuario.append(linia.strip())
		elif mem == True:
			if linia != '' and linia != 'mem':
				ll_ram = linia.strip()
				swap = True
		elif discs == True:
			if linia != '' and linia != 'discs':
				ll_discs.append(linia.strip())
				
	if ll_swap != '':
		ll_swap = ll_swap.split(' ')
		ll_swap = filter(None, ll_swap)
		del ll_swap[0]
	else:
		ll_swap = False
		
	ll_total.append(ll_swap)
	ll_total.append(ll_cpu)
	ll_total.append(ll_usuario)

	if ll_ram != '':
		ll_ram = ll_ram.split(' ')
		ll_ram = filter(None, ll_ram)
		del ll_ram[0]
	else:
		ll_ram = False
		
	ll_total.append(ll_ram)

	if ll_discs:
		del ll_discs[0]
		lls_discs = []
		
		for element in ll_discs:
			ll_disc = []
			ll_disc = element.split(' ')
			ll_disc = filter(None, ll_disc)
			lls_discs.append(ll_disc)
	else:
		lls_discs = [False]
	
	ll_total.append(lls_discs)
		
	return ll_total

def insertar_dades(ip, ll_cpu, ll_usuario, ll_ram, ll_swap, lls_discs):
	# Insertem les dades a la base de dades a partir de les llistes generades anteriorment
	if ll_cpu:
		try:
			connexio.query("""insert into cpu (id_pc, valor1, valor2, timereg, dayreg) values ('%s', '%s', '%s', '%s', '%s')""" % (ip, ll_cpu[0], ll_cpu[1], now[1], now[0]))
		except:
			syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es poden afegir a la base de dades les dades de la ip "%s"' % (ip))
	if ll_usuario:
		for usuari in ll_usuario:
			try:
				connexio.query("""insert into usuaris (id_pc, usuari, timereg, dayreg) values ('%s', '%s', '%s', '%s')""" % (ip, usuari, now[1], now[0]))
			except:
				syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es poden afegir a la base de dades les dades de la ip "%s"' % (ip))
	if ll_ram != False:
		try:
			connexio.query("""insert into ram (id_pc, total, used, free, shared, buffers, cached, timereg, dayreg) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" % (ip, ll_ram[0], ll_ram[1], ll_ram[2], ll_ram[3], ll_ram[4], ll_ram[5], now[1], now[0]))
		except:
			syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es poden afegir a la base de dades les dades de la ip "%s"' % (ip))
	
	if ll_swap != False:
		try:
			connexio.query("""insert into swap (id_pc, total, used, free, timereg, dayreg) values ('%s', '%s', '%s', '%s', '%s', '%s')""" % (ip, ll_swap[0], ll_swap[1], ll_swap[2], now[1], now[0]))
		except:
			syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es poden afegir a la base de dades les dades de la ip "%s"' % (ip))
	
	if lls_discs[0] != False:
		for ll_disc_inf in lls_discs:
			try:
				connexio.query("""insert into discs (id_pc, s_fitxers, size, used_disc, avail, used, mount, timereg, dayreg) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" % (ip, ll_disc_inf[0], ll_disc_inf[1], ll_disc_inf[2], ll_disc_inf[3], ll_disc_inf[4], ll_disc_inf[5], now[1], now[0]))
			except:
				syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es poden afegir a la base de dades les dades de la ip "%s"' % (ip))
	

# Definició d'arguments i opcions

usage='Usage: Reinstalar [-r] Ruta reglas [-f]'
parser = OptionParser(usage)
parser.add_option('-r', '--reinstall', dest='reinstall', default='no')
parser.add_option('-f', '--file', dest ='config', default='/opt/monser-navas/reglas.txt', help='Ruta del fitxer de configuracio')
(options, args) = parser.parse_args()

FILE = options.config
REINSTALL = options.reinstall
		
# Cos del programa

#Crear PID en /var/run/monser.pid
try:	
	f = open("/var/run/monser.pid","w")
	PID = os.getpid()
	f.write(str(PID))
	f.close()
except:
	syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, "No s'ha pogut escriure en el fitxer de PID")
	sys.exit(1)

# Gardem les regles i les ips de nmap executant les funcions corresponents
reglas2 = reglas()
xarxa = reglas2['nmap']
interval = float(reglas2['interval'])
ips = nmap(xarxa)
noreglas = False
strreglas = reglas_client(reglas())

# Si reb aquesta senyal, sortirà del programa
signal.signal(signal.SIGUSR1, kill)
# Si fem Conrl + C segueix la seva execució
signal.signal(signal.SIGINT, signal.SIG_IGN)
# Si reb aquest senyal rellegirà el fitxer de reglas.txt
signal.signal(signal.SIGHUP, rellegir)

#ips = ['192.168.0.81','192.168.0.82','192.168.0.80']
# Provem la conexió a la base de dades
try:
	connexio = pg.connect(dbname='db_monitoritzar', host='localhost', port=5432, user='usr_monitoritzar')
	
	while True:
		# Per cada ip obtinguda en la llista del nmap de pcs encesos
		for ip in ips:
			#print ip
			now = str(datetime.datetime.today())[:-7].split(' ')
			timeout = 0
			instalat = True
			rebut = False
			salida = False
			reinstalar = False
			# Opcio per reinstalar el client als pcs remots
			if REINSTALL == 'yes':
				reinstalar = True
			# Començem un bucle que: 1. Conecta per ssh amb la ip remota i instala el programa si no hi es
			# 2. Es conecta amb el pc remot mitjançant un socket i li transmet les regles
			# 3. Rep la informació solicitada per les regles i la introdueix a la base de dades
			while 1:
				if timeout == 2:
						# Afegim el pc apagat a la base de dades
						try:
							connexio.query("""insert into pcs (id_pc, estat, timereg, dayreg) values ('%s', '%s', '%s', '%s')""" % (ip, 'down', now[1], now[0]))
						except:
							syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es poden afegir a la base de dades el pc de la ip "%s"' % (ip))
	
						break
				if reinstalar == False:				
					try:
						#ip = '192.168.0.82'
						# Conexió per ssh amb el modul paramiko
						ssh = paramiko.SSHClient()
						ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
						ssh.connect(ip, username='root', password='jupiter')
						stdin, stdout, stderr = ssh.exec_command("updatedb")
						stdout.readline()
						stdin, stdout, stderr = ssh.exec_command("locate /opt/monser-client-navas/monitor-client.py")
						salida = stdout.readline()
						# Comprovem si el programa ja es troba instalat i si es així l'executem
						if salida != '':
							# Inicia el client a l'ordinador remot
							stdin, stdout, stderr = ssh.exec_command("python /opt/monser-client-navas/monitor-client.py")
						# Sistema de logs	
						syslog.syslog(syslog.LOG_LOCAL3 | syslog.LOG_INFO, 'Conectat amb la ip "%s"' % (ip)) 
						salida = True
					
					except:
						syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es pot executar el servei a la ip "%s"' % (ip))
						salida = False
						
				# Si no s'ha trobat el programa o si no s'ha pogut conectar amb el socket s'instalarà
				if salida == False or instalat == False:

					timeout = timeout + 1
					# Si s'ha escollit l'opcio reinstalar
					'''if reinstalar == True:
						#print 'Es reinstalara el programa.'
					else:
						#print 'El servei no esta instalat'
					#print 'Instalant el servei'''
					try:
						# Es conecta per ssh per crear el directori i copia per sftp el programa
						ssh = paramiko.SSHClient()
						ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
						ssh.connect(ip, username='root', password='jupiter')
						stdin, stdout, stderr = ssh.exec_command("mkdir /opt/monser-client-navas")
						stdin, stdout, stderr = ssh.exec_command("chmod 744 /opt/monitoritzar")
						ftp = ssh.open_sftp()
						ftp.put('/opt/monser-navas/monitor-client.py', '/opt/monser-client-navas/monitor-client.py')
						ftp.close()
						stdin, stdout, stderr = ssh.exec_command("chmod 744 /opt/monser-client-navas/monitor-client.py")
						instalat = True
						reinstalar = False
						ssh.close()
						#print 'Programa instalat'

					except:
						#print 'No ha pogut instalar-se el programa'
						syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es possible instalar el programa a la ip "%s"' % (ip))
							
				else:
					# Si no hi ha fitxer de reglas
					if noreglas == True:
						#print 'No has especificat cap regla al fitxer indicat.'
						break
					#print 'Servei iniciat a la ip ' + ip
					time.sleep(1)
					try:
						# Comença la conexió amb el socket
						HOST = ip    # The remote host
						PORT = 50020  # The same port as used by the server
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					
						s.connect((HOST, PORT))
						info = True
						dataok = ''
						while 1:
							if info == True:
								# Si no tenim regles informem al client amb la cadena 'nodata'
								if strreglas == '':
									s.send('nodata')
									s.close()
									noreglas = True
									break
								else:
									# Enviem les regles al client
									s.send(strreglas)
									info = False
							
							data = s.recv(1024)
							while data:#Siempre que haya data!!
								dataok = dataok + data
								if data[-1] == chr(4):#Si toba a la cadena de text el EOT en ascii PARA!
									#print data[0:-1]
									break
								data = s.recv(1024)
							dataok = dataok[:-2]
							s.close()
							#print 'Data rebuda'
							rebut = True
							# Afegim el pc engegat a la base de dades
							try:
								connexio.query("""insert into pcs (id_pc, estat, timereg, dayreg) values ('%s', '%s', '%s', '%s')""" % (ip, 'up', now[1], now[0]))
							except:
								syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es poden afegir a la base de dades el pc de la ip "%s"' % (ip))
	
							break
					except:
						syslog.syslog(syslog.LOG_LOCAL2 | syslog.LOG_ERR, 'No es possible conectar amb el socket a la ip "%s"' % (ip))
						#print 'No es possible conectar amb el socket'
						instalat = False
							
					if rebut == True:
						# Si hem rebut dades executem les funcions per tractarles i insertarles a la base de dades	
						ll_total = tractar_dades(dataok)
						insertar_dades(ip, ll_total[1], ll_total[2], ll_total[3], ll_total[0], ll_total[4])
						s.close()
						break
					s.close()
		time.sleep(interval)
except IOError:
		sys.stderr.write("ERROR a la connexió\n")
		sys.exit(1)
