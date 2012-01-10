#!/bin/sh
#
# Albert Navas
# hisi46997513
# Script que instala els fitxers d'instalació a tmp i crea la base de dades

# Configuració dels logs
logs=`grep monser-navas /etc/rsyslog.conf`
logs=`echo $?`

# Si no existeixen
if  [ "$logs" = 1 ]; then
	echo "#monser-navas
local2.err                                              /var/log/error_monser.log
local3.info                                             /var/log/info_monser.log" >> /etc/rsyslog.conf
	echo "El sistema de logs ha sigut configurat"
else
	echo "El sistema de logs està configurat"
fi

# Si no existeix
if [ ! -f /etc/logrotate.d/rotar_logs ]; then
	
	touch /etc/logrotate.d/rotar_logs > /dev/null 2>&1
	chmod 755 /etc/logrotate.d/rotar_logs
	
	echo "/var/log/error_monser.log {
	daily
	rotate 90
	copytruncate
	compress
	notifempty
	missingok
	}
	/var/log/info_monser.log {
	daily
	rotate 90
	copytruncate
	compress
	notifempty
	missingok
	}" >> /etc/logrotate.d/rotar_logs
	
	/usr/sbin/logrotate -d -f /etc/logrotate.conf > /dev/null 2>&1
	
	echo "El sistema logrotate ha sigut configurat"
else
	echo "El sistema logrotate està configurat"
fi

# Reinici del servei postgres per aplicar la nova configuració de logs
echo "Reiniciant el servei de postgres..."
service postgresql restart > /dev/null 2>&1

# Comprovem que està ben configurat postgres per poder crear bases de dades
bd_postgres=`grep 'local   all         all                               trust' /var/lib/pgsql/data/pg_hba.conf`
bd_postgres=`echo $?`

if  [ "$bd_postgres" = 1 ]; then
	echo "Per poder instalar el programa ha de modificar el fitxer /var/lib/pgsql/data/pg_hba.conf
i afegir la linea 'local   all         all                               trust
després de 'local' is for Unix domain socket connections only"
# Si està bé, es creen els directoris i fitxers a /opt/monser-navas.
# També es crea un usuari, una base de dades i les taules
else
	echo "Copiant fitxers..."
	mkdir /opt > /dev/null 2>&1
	mkdir /opt/monser-navas > /dev/null 2>&1
	mkdir /opt/monser-navas/plantillas > /dev/null 2>&1
	chmod 755 /opt
	chmod 755 /opt/monser-navas
	chmod 755 /opt/monser-navas/plantillas
	
	cp -f install/monitor-client.py /opt/monser-navas/monitor-client.py
	cp -f install/monitor-servidor.py /opt/monser-navas/monitor-servidor.py
	cp -f install/monitor-reporter.py /opt/monser-navas/monitor-reporter.py
	cp -f install/styletable.css /opt/monser-navas/plantillas/styletable.css
	cp -f install/reglas.txt /opt/monser-navas/reglas.txt
	cp -f install/readme /opt/monser-navas/readme
	cp -f install/monser /etc/init.d/monser

	chmod 755 /opt/monser-navas/monitor-client.py
	chmod 755 /opt/monser-navas/monitor-servidor.py
	chmod 755 /opt/monser-navas/monitor-reporter.py
	chmod 755 /opt/monser-navas/plantillas/styletable.css
	chmod 755 /opt/monser-navas/reglas.txt
	chmod 755 /opt/monser-navas/readme
	chmod 755 /etc/init.d/monser
	
	echo "Instalant usuari de la base de dades..."
	psql -q -c "\i install/installbd.sql" template1 postgres > /dev/null 2>&1
	echo "Instalant la base de dades..."
	psql -q -c "\i install/installbd_createdb.sql" template1 usr_monitoritzar > /dev/null 2>&1
	echo "Instalant les taules de la base de dades..."
	psql -q -c "\i install/installbd_tables.sql" db_monitoritzar usr_monitoritzar > /dev/null 2>&1

	if [ -f /opt/monser-navas/monitor-client.py ] && [ -f /opt/monser-navas/monitor-servidor.py ] && [ -f /opt/monser-navas/monitor-reporter.py ] && [ -f /opt/monser-navas/plantillas/styletable.css ] && [ -f /opt/monser-navas/reglas.txt ] && [ -f /opt/monser-navas/readme ] && [ -f /etc/init.d/monser ]; then
		echo "El programa s'ha instalat correctament a /opt/monser-navas."
		echo "Executa service monser start o /opt/monser-navas/monitor-reporter.py"
	else
		echo "Error en la copia d'algun fitxer. Es possible que alguna funció del programa no vagi correctament."
	fi
fi
