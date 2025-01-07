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

build()
{
with_blocksize=$1
echo "**********************************************************************************************************************" >> ../logfile
echo "**********************************************************************************************************************" >> ../logfile
echo ""

make clean 1>/dev/null 2>/dev/null
print_status_exit_on_error "make clean" $?
echo "make clean" >> ../logfile

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
                  --with-blocksize=$with_blocksize\
                  --with-llvm 1>/dev/null 2>/dev/null
print_status_exit_on_error "./configure" $?
echo "configure --with-blocksize=$with_blocksize" >> ../logfile

make -j 4 1>/dev/null 2>/dev/null
print_status_exit_on_error "make" $?
echo "make" >> ../logfile

make check 1>/dev/null 2>/dev/null
if [ ! $? -eq 0 ];
then
 printf "${red}%s${nrm}\t%s\n" "NO" "make check"
 printf "${yel}%s${nrm} ${red}%s${nrm}, ${yel}%s${nrm}\n" "make check" "FAILED" "stop build now."
 return 1
else
 printf "${grn}%s${nrm}\t%s\n" "OK" "make check"
fi
echo "make check" >> ../logfile

sudo make install 1>/dev/null 2>/dev/null
print_status_exit_on_error "make install" $?
echo "make install" >> ../logfile

# create directories && set permissions
echo "" >> ../logfile
echo "create directories && set permissions" >> ../logfile
rm -rf /mnt/db/data
rm -rf /mnt/db/log
mkdir -p /mnt/db/data
mkdir -p /mnt/db/log
chgrp -R db /mnt/db/data
chmod -R 750 /mnt/db/data # Permissions should be u=rwx (0700) or u=rwx,g=rx (0750)
chgrp -R db /mnt/db/log
chmod -R 750 /mnt/db/log  # Permissions should be u=rwx (0700) or u=rwx,g=rx (0750)

# initdb
initdb --auth=peer\
	   --pgdata=/mnt/db/data\
	   --locale=uk_UA.utf8\
	   --encoding=UTF8\
	   --allow-group-access\
	   --waldir=/mnt/db/log 1>/dev/null 2>/dev/null
print_status_exit_on_error "initdb" $?
echo "initdb" >> ../logfile

# copy server config. the server will start with config copied.
cp ../postgresql.conf /mnt/db/data/
print_status_exit_on_error "copy postgresql.conf" $?
echo "copy postgresql.conf" >> ../logfile

# start server
pg_ctl -D /mnt/db/data -l pg.log start 1>/dev/null 2>/dev/null
print_status_exit_on_error "start server" $?
echo "start server" >> ../logfile

# create yv database. this step enables a connection to server with yv account
createdb yv
print_status_exit_on_error "create db" $?
echo "create db" >> ../logfile

# init pgbench
pgbench -i -I dtgpf -s 100 1>/dev/null 2>/dev/null
print_status_exit_on_error "init pgbench" $?
echo "init pgbench" >> ../logfile

# run pgbench select-only, 10 connections, 8 threads, 1min
echo "---" >> logfile
pgbench -c 10 -j 8 -S -T 60 | tail -n 4 | head -n 4 >> logfile
print_status_exit_on_error "pgbench select-only" $?
echo "pgbench select-only" >> logfile
echo "---" >> logfile

# run pgbench select-update-insert, 10 connections, 8 threads, 1min
pgbench -c 10 -j 8 -T 60 | tail -n 4 | head -n 4 >> logfile
print_status_exit_on_error "select-update-insert" $?
echo "pgbench select-update-insert" >> logfile
echo "---" >> logfile

# stop server
stop_serv
echo "**********************************************************************************************************************" >> ../logfile
echo "**********************************************************************************************************************" >> ../logfile
echo "" >> ../logfile
sync
return 0
}

#################################################################################################################################################

rm logfile 1>/dev/null 2>/dev/null
touch logfile
mkdir -p build
cd build

N=0
for i in 8 16 32 64
do
 build "$i"
 if [ $? -eq 0 ];
 then
  N=$((N+1))
 fi
done

printf "${yel}%s${nrm}%s out of %s\n" "successful builds: " "$N" "4"