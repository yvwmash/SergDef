#!/bin/sh

cm="$1"

# LIST AVAIBLE COMMANDS
print_list()
{
 printf "\t%21.21s - %10.40s\n" "list"              "list this commands"
 printf "\t%21.21s - %10.40s\n" "start"             "start server"
 printf "\t%21.21s - %10.40s\n" "stop"              "stop server"
 printf "\t%21.21s - %10.40s\n" "status"            "print status of the server"
}

case $cm in
 ("list") printf "${yel}%s${nrm}\n" "avaible commands..."
      print_list
 ;;
 (x)  print_list
 ;;
 ("") print_list
 ;;
 ("start")
  pg_ctl -D /mnt/db/data/ start
 ;;
 ("stop")
  pg_ctl -D /mnt/db/data/ stop
 ;;
 ("status")
  pg_ctl -D /mnt/db/data/ status
 ;;
esac

exit 0