#!/usr/bin/python
#-*- coding: utf-8 -*-

# Albert Navas Mallo
# hisi46997513

'''
Monrep

• Rotar els fitxers de les dades si cal i si això no s’ha realitzat abans.

• Generar els informes sol·licitats per l’usuari.
'''

# Mòduls

import sys, os, sys, signal, pg, datetime
from optparse import OptionParser

# Funcions

def exist_taula(dades, DADA):
	# Funció per saber si una taula existeix
	for existeix in dades:
		if DADA == existeix:
			return True
	return False
	sys.exit(0)
	
def crear_plantilla(info, taula):
	# Funció que crea la plantilla segons la informació que rebuda
	capcos = cap(taula)
	html = '<!DOCTYPE html \n PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ca" lang="ca">\n\t<head>\n\t\t<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n\t\t<LINK rel=stylesheet type="text/css" href="styletable.css">\n\t\t<title>' + taula + '</title>\n\t</head>\n<body>\n\t<table border=1>\n' + capcos + '\n'
				
	for objects in info:
		taula = '\t\t<tr><td>'
		for element in objects:
			taula = taula + str(element) + '<td>'
		taula = taula[:-4]
		html = html + taula + '</td>\n'
	html = html + '\t</table>\n</body>\n</html>'
	return html

def crear_plantilla_multiple(PC, BEGIN, END):
	# Funció que crea plantilles de totes les taules
	html = '<!DOCTYPE html \n PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ca" lang="ca">\n\t<head>\n\t\t<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n\t\t<LINK rel=stylesheet type="text/css" href="styletable.css">\n\t\t<title>Totes les dades</title>\n\t</head>\n<body>\n'
	for dada in dades:
		capcos = cap(dada)
		html = html + '\t<table border=1>\n' + capcos + '\n'
		# Si exixteix un PC, generarà la plantilla de totes les taules per aquest pc
		if PC != '':
			if BEGIN[0] != '' and END[0] != '':
				info = connexio.query("select * from %s where id_pc = '%s' and dayreg <= '%s' and '%s' <= dayreg and timereg <= '%s' and '%s' <= timereg" % (dada, PC_ip, END[0], BEGIN[0], END[1], BEGIN[1])).getresult()
			else:
				info = connexio.query("select * from %s where id_pc = '%s'" % (dada, PC)).getresult()
		else:
			if BEGIN[0] != '' and END[0] != '':
				info = connexio.query("select * from %s where dayreg <= '%s' and '%s' <= dayreg and timereg <= '%s' and '%s' <= timereg" % (dada, END[0], BEGIN[0], END[1], BEGIN[1])).getresult()
			else:
				info = connexio.query("select * from %s" % (dada)).getresult()

		for objects in info:
			taula = '\t\t<tr><td>'
			for element in objects:
				taula = taula + str(element) + '</td><td>'
			taula = taula[:-4]
			html = html + taula + '</tr>\n'
		html = html + '\t</table><br/>\n'
	html = html + '</body>\n</html>'
	return html

def generar(html, nom_plantilla):
	# Funció que genera el fitxer de la plantilla a partir de tot el codi html
	nom_plantilla = nom_plantilla + '.html'
	try:
		now = str(datetime.datetime.today())[:-7].split(' ')
		nom_plantilla = nom_plantilla + '_' + now[0] + '_' + now[1]
		plantilla = open(nom_plantilla, 'w')
		plantilla.write(html)
		ordre = 'chmod 755 ' + nom_plantilla
		os.system(ordre)
	except:
		return 0
	
	return 1
	
def cap(titol):
	# Funció que determina la capçelera de la taula segons les dades demanades
	capcos = '\t\t<tr><th>'
				
	if titol == 'discs':
		for cap in discs:
			capcos = capcos + cap + '</th><th>'
	elif titol == 'pcs':
		for cap in pcs:
			capcos = capcos + cap + '</th><th>'
	elif titol == 'ram':
		for cap in ram:
			capcos = capcos + cap + '</th><th>'
	elif titol == 'swap':
		for cap in swap:
			capcos = capcos + cap + '</th><th>'
	elif titol == 'usuaris':
		for cap in usuaris:
			capcos = capcos + cap + '</th><th>'
	elif titol == 'cpu':
		for cap in cpu:
			capcos = capcos + cap + '</th><th>'
	
	capcos = capcos[:-4] + '</tr>'
	
	return capcos


# Definició d'arguments i opcions

usage= './monrep.py [-b moment_inicial] [-e moment_final] -d [dades_a_consultar] -p [pcs a consultar]'
parser = OptionParser(usage)
parser.add_option('-b', '--begin', dest='begin', default='', help="Format 'aaaa-mm-dd hh:mm:ss'")
parser.add_option('-e', '--end', dest='end', default='', help="Format 'aaaa-mm-dd hh:mm:ss'")
parser.add_option('-d', '--dada', dest ='dada', default='', help='Dades a consultar separades per espais')
parser.add_option('-p', '--pc', dest='pc', default='', help='Numero pcs a consultar separats per espais')
(options, args) = parser.parse_args()

BEGIN = options.begin.split(' ')
END = options.end.split(' ')
DADA = options.dada
PC = options.pc

# Llistes de les capçaleres
dades = ['pcs', 'ram', 'swap', 'cpu', 'discs', 'usuaris']
pcs = ['id_pc', 'ip', 'estat', 'Data', 'Hora']
discs = ['id_pc', 'ip', 's.fitxers', 'size', 'used disc', 'avail', 'used', 'mount', 'Data', 'Hora']
ram = ['id_pc', 'ip', 'total', 'used', 'free', 'shared', 'buffers', 'cached', 'Data', 'Hora']
swap = ['id_pc', 'ip', 'total', 'used', 'free', 'Data', 'Hora']
usuaris = ['id_pc', 'ip', 'usuari' , 'Data', 'Hora']
cpu = ['id_pc', 'ip', 'valor1' , 'valor2', 'Data', 'Hora']


# Cos del programa

try:
	# Connexió a la base de dades
	connexio = pg.connect(dbname='db_monitoritzar', host='localhost', port=5432, user='usr_monitoritzar')
	DADES = DADA.split(' ')
	PCs = PC.split(' ')
	
	# Per a cada taula que hem especificat a l'opcio -d genera una plantilla
	for taula in DADES:
		# Per cada PC que hem especificat a l'opcio -p genera una plantilla
		for PC in PCs:
			nom_plantilla = '/opt/monser-navas/plantillas/plantilla_'
			try:
				if PC != '':
					int(PC)
			except:
				print 'El Pc ha de ser un numero.'
				sys.exit(1)
				
			# Si NO hi han les opcions -b, -e o -d
			if BEGIN[0] == '' or END[0] == '' or taula == '':
				# Si NO hi ha l'opció -d
				if taula == '':
					# Genera una plantilla de totes les taules, si existeix l'opció -p mostrarà totes les taules del pc demanat
					if PC != '':
						nom_plantilla = nom_plantilla + 'pc' + PC + '_' + 'all'
						PC_ip = '192.168.0.' + str(int(PC) + 40)
					else:
						nom_plantilla = nom_plantilla + 'all'
						PC_ip = ''
					# Li passem el PC a la funció
					if generar(crear_plantilla_multiple(PC_ip, BEGIN, END), nom_plantilla):
						print 'Plantilla general generada correctament amb el nom ' + nom_plantilla[29:]
				else:
					# Comprova que existeixi la taula de la opció -d
					if exist_taula(dades, taula):
						# Si s'ha especificat l'opció -p
						if PC != '':
							# Genera una plantilla de la taula i del pc concret demanats
							nom_plantilla = nom_plantilla + 'pc' + PC + '_' + taula
							PC_ip = '192.168.0.' + str(int(PC) + 40)

							info = connexio.query("select * from %s where id_pc = '%s'" % (taula, PC_ip)).getresult()
							
							if generar(crear_plantilla(info, taula), nom_plantilla):
								print 'Plantilla de ' + taula + ' del pc' + PC + ' generada correctament amb el nom ' + nom_plantilla[29:]
						# Si NO s'ha especificat l¡opció -p
						else:
							# Genera una plantilla de la taula demanada
							nom_plantilla = nom_plantilla + taula
							info = connexio.query("select * from %s" % (taula)).getresult()
							
							if generar(crear_plantilla(info, taula), nom_plantilla):
								print 'Plantilla de ' + taula + ' generada correctament amb el nom ' + nom_plantilla[29:]
					else:
						print 'No existeix la taula ' + taula + '.'
			# Si hi han les opcions -b, -e i -d
			else:
				# Comprova que existeixi la taula de la opció -d
				if exist_taula(dades, taula):
					# Si s'ha especificat l'opció -p
					if PC != '':
						# Genera una plantilla de la taula, l'interval de temps i del pc concret demanats
						nom_plantilla = nom_plantilla + 'pc' + PC + '_' + taula + '_datahora'
						PC_ip = '192.168.0.' + str(int(PC) + 40)

						info = connexio.query("select * from %s where id_pc = '%s' and dayreg <= '%s' and '%s' <= dayreg and timereg <= '%s' and '%s' <= timereg" % (taula, PC_ip, END[0], BEGIN[0], END[1], BEGIN[1])).getresult()
						if generar(crear_plantilla(info, taula), nom_plantilla):
							print 'Plantilla de ' + taula + ' del pc' + PC + ' generada correctament amb el nom ' + nom_plantilla[29:]
					# Si NO s'ha especificat l'opció -p						
					else:
						# Genera una plantilla de la taula i l'interval de temps demanats
						nom_plantilla = nom_plantilla + taula + '_datahora'
						info = connexio.query("select * from %s where dayreg <= '%s' and '%s' <= dayreg and timereg <= '%s' and '%s' <= timereg" % (taula, END[0], BEGIN[0], END[1], BEGIN[1])).getresult()
						
						if generar(crear_plantilla(info, taula), nom_plantilla):
							print 'Plantilla de ' + taula + ' generada correctament amb el nom ' + nom_plantilla[29:]
				else:
					print 'No existeix aquesta taula ' + taula + '.'

except IOError:
		sys.stderr.write("ERROR a la connexió\n")
		sys.exit(1)
