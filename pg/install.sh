#!/bin/sh

export PATH="$PATH:/usr/local/pgsql/bin/"

red="\e[1;31m"
grn="\e[1;32m"
yel="\e[1;33m"
blu="\e[1;34m"
mag="\e[1;35m"
cyn="\e[1;36m"
nrm="\e[0m"

print_status()
{
 msg="$1"
 res=$2
 if [ ! $res -eq 0 ]
 then
  printf "${red}%s${nrm}\t%s\n" "NO" "$msg"
 else
  printf "${grn}%s${nrm}\t%s\n" "OK" "$msg"
 fi
}

stop_serv()
{
 stat /usr/local/pgsql/bin/pg_ctl 1>/dev/null 2>/dev/null
 if [ $? -eq 0 ] && [ ! 'pg_ctl: no server running' = "$(pg_ctl -D /mnt/db/data/ status)" ];
 then
  pg_ctl -D /mnt/db/data/ stop 1>/dev/null 2>/dev/null
  echo "stop server" >> ../logfile
  print_status "stop server" $?
 fi
}

exit_on_error()
{
 if [ ! $1 -eq 0 ]
 then
  printf "${red}%s${nrm}\n" "exit now"
  stop_serv
  exit 0
 fi
}

print_status_exit_on_error()
{
 print_status "$1" $2
 exit_on_error $res
}

#################################################################################################################################################

cp_conf()
{
 # postgresql.conf
 cp ./postgresql.conf /mnt/db/data/
 print_status_exit_on_error "copy postgresql.conf" $?

 # config script for psql
 sudo mkdir -p /usr/local/pgsql/etc
 sudo chown -R yv /usr/local/pgsql/etc
 sudo chgrp -R db /usr/local/pgsql/etc
 cp ./psqlrc /usr/local/pgsql/etc
 print_status_exit_on_error "copy psqlrc to /usr/local/pgsql/etc" $?
 chown yv /usr/local/pgsql/etc/psqlrc
 chgrp db /usr/local/pgsql/etc/psqlrc

 # convenience script
 sudo cp ./pg_op.sh /usr/local/sbin/
 print_status_exit_on_error "copy pg_op convenience script to /usr/local/sbin/" $?
 sudo chown yv /usr/local/sbin/pg_op.sh
 sudo chgrp db /usr/local/sbin/pg_op.sh
 chmod 770 /usr/local/sbin/pg_op.sh
 return 0
}

build_install()
{
mkdir -p build
cd build

make clean 1>/dev/null 2>/dev/null
print_status_exit_on_error "make clean" $?

../postgresql-12.1/configure CC=clang\
                  CFLAGS="-march=native -O2"\
                  --with-perl\
                  PYTHON=python3\
                  --with-python\
                  --with-systemd\
                  --with-openssl\
                  --with-icu\
                  --with-pam\
                  --with-libxml\
                  --with-segsize=1\
                  --with-blocksize=8\
                  --with-llvm 1>/dev/null 2>/dev/null
print_status_exit_on_error "./configure" $?

make -j 4 1>/dev/null 2>/dev/null
print_status_exit_on_error "make" $?

make check 1>/dev/null 2>/dev/null
if [ ! $? -eq 0 ];
then
 printf "${red}%s${nrm}\t%s\n" "NO" "make check"
 printf "${yel}%s${nrm} ${red}%s${nrm}, ${yel}%s${nrm}\n" "make check" "FAILED" "stop script now."
 return 1
else
 printf "${grn}%s${nrm}\t%s\n" "OK" "make check"
fi

sudo make install 1>/dev/null 2>/dev/null
print_status_exit_on_error "make install" $?

rm -rf /mnt/db/data
rm -rf /mnt/db/log
mkdir -p /mnt/db/data
mkdir -p /mnt/db/log
chgrp -R db /mnt/db/data
chmod -R 750 /mnt/db/data # Permissions should be u=rwx (0700) or u=rwx,g=rx (0750)
chgrp -R db /mnt/db/log
chmod -R 750 /mnt/db/log  # Permissions should be u=rwx (0700) or u=rwx,g=rx (0750)

initdb --auth=peer\
	   --pgdata=/mnt/db/data\
	   --locale=uk_UA.utf8\
	   --encoding=UTF8\
	   --allow-group-access\
	   --waldir=/mnt/db/log 1>/dev/null 2>/dev/null
print_status_exit_on_error "initdb" $?

cp_conf

pg_ctl -D /mnt/db/data -l pg.log start 1>/dev/null 2>/dev/null
print_status_exit_on_error "start server" $?

createdb yv
print_status_exit_on_error "create db" $?

pgbench -i -I dtgpf -s 100 1>/dev/null 2>/dev/null
print_status_exit_on_error "init pgbench" $?

pgbench -c 10 -j 8 -S -T 60 | tail -n 4 | head -n 4
print_status_exit_on_error "pgbench select-only" $?

pgbench -c 10 -j 8 -T 60 | tail -n 4 | head -n 4
print_status_exit_on_error "select-update-insert" $?

stop_serv
sync
cd ..

return 0
}

install_utility_functions()
{
 cd func
 psql -f from_csv.plpy3
 psql -f from_excel.plpy3
 cd ..
}

cm="$1"

# LIST AVAIBLE COMMANDS
print_list()
{
 printf "\t%21.21s - %10.40s\n" "list"              "list the commands"
 printf "\t%21.21s - %10.40s\n" "[all]"             "install all"
 printf "\t%21.21s - %10.40s\n" "build_install"     "build posgres & install & copy config & run bench"
 printf "\t%21.21s - %10.40s\n" "config"            "copy config"
 printf "\t%21.21s - %10.40s\n" "util"              "install utility functions"
}

case $cm in
 ("list") printf "${yel}%s${nrm}\n" "avaible commands..."
  print_list
 ;;
 (x)
  build_install
 ;;
 ("") 
  build_install
 ;;
 ("config")
  cp_conf
 ;;
 ("util")
  install_utility_functions
 ;;
esac

exit 0