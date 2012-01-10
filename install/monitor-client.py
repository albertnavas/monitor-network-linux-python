#!/usr/bin/python
#-*- coding: utf-8 -*-

# Albert Navas Mallo
# hisi46997513

'''
Monclie

•	Acceptar la sol·licitud d’informació de monser, obtenir-la i transmetre-li-la.
'''

# Mòduls

from optparse import OptionParser
from subprocess import Popen, PIPE
import socket, sys, select, os, time, sys, signal
import syslog

# Funcions

# Funció per poder matar el programa amb una senyal
def kill(signum,frame):
	s.close()
	conn.close()
	sys.exit(0)
	
def cpu():
	# Estat de la cpu
	command = 'w | head -n1 | cut -d " " -f12,13,14'
	tubo = Popen(command, shell = True, stdout = PIPE, stderr = PIPE)
	cpu = tubo.stdout.read().rstrip()[:10]
	
	return cpu
	
def estats():
	# Memòria ram i swap
	estats=[]
	command = 'free | grep Mem'
	tubo = Popen(command, shell = True, stdout = PIPE, stderr = PIPE)
	estats.append(tubo.stdout.readline().rstrip())
	
	command = 'free | grep Swap'
	tubo = Popen(command, shell = True, stdout = PIPE, stderr = PIPE)
	estats.append(tubo.stdout.readline().rstrip())
	
	return estats

def usuaris():
	# Usuaris agrupats
	usuaris=[]
	command = 'who | cut -f1 -d " " | uniq -c'
	tubo = Popen(command, shell = True, stdout = PIPE, stderr = PIPE)
	usuaris = tubo.stdout.read().rstrip()
	
	return usuaris

def discs():
	# Informació sobre discs
	discs=[]
	command = 'df -hT | grep -v size'
	tubo = Popen(command, shell = True, stdout = PIPE, stderr = PIPE)
	for disc in tubo.stdout.readlines():
		discs.append(disc.rstrip())
	
	return discs

# Cos del programa

#Senyal perquè el server deixi de funcionar
signal.signal(signal.SIGUSR1, kill)

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50020              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()

data = conn.recv(1024)
while data:			
	#print data
	info = ''
	if data == 'nodata':
		s.close()
		sys.exit(0)
		
	reglas = data.split(' ')
	for regla in reglas:
		if regla == 'cpu':
			info = info + 'cpu\n'
			#print 'Estat de la cpu enviada'
			info = info + cpu() + '\n'
		elif regla == 'usuaris':
			info = info + 'usuario\n'
			#print 'Usuaris enviats'
			info = info + usuaris() + '\n'
		elif regla == 'discs':
			info = info + 'discs\n'
			#print 'Estat dels discs enviats'
			for disc in discs():
				info = info + disc + '\n'
		elif regla == 'RAM/swap':
			info = info + 'mem\n'
			#print 'Estat de la cpu enviada'
			info = info + estats()[0] + '\n'
			info = info + estats()[1] + '\n'
		info = info + '\n'
	conn.send(info)
	# S'envia un caràcter ASCII per informar del final del missatge
	conn.send(chr(4))

	s.close()
	conn.close()
	sys.exit(0)
