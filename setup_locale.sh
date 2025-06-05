#!/bin/bash

# Instalar o locale pt_BR.UTF-8
apt-get update
apt-get install -y locales
locale-gen pt_BR.UTF-8
update-locale LANG=pt_BR.UTF-8

# Configurar o locale para o usuário atual
export LANG=pt_BR.UTF-8
export LC_ALL=pt_BR.UTF-8
