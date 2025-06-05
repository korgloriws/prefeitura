
set -e


apt-get update && apt-get install -y locales


sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen


locale-gen pt_BR.UTF-8


update-locale LANG=pt_BR.UTF-8
