initdb () {
  if [ ! -n "$1" ]
  then
    echo "Usage: $0 [username] [password] [dbname]"
    return
  fi
  mysql -uroot -e "CREATE USER $1 IDENTIFIED BY '$2'"
  mysql -uroot -e "CREATE DATABASE $3 CHARACTER SET utf8"
  mysql -uroot -e "GRANT ALL ON $3.* TO $1@localhost IDENTIFIED BY '$2'"
}
initdb ikari_db ikari_db ikari_db
