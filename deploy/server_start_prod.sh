#!/bin/bash

#Copy all the prod config files
sudo rsync -avzC /home/ec2-user/projects/ikari/config/prod/ /etc/httpd/conf.d

#ikari-amigos
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_amigos
sudo mkdir /etc/httpd/logs/ikari-amigos
sudo touch /etc/httpd/logs/ikari-amigos/error_log
sudo touch /etc/httpd/logs/ikari-amigos/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-amigos

#ikari-appleaf
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_appleaf
sudo mkdir /etc/httpd/logs/ikari-appleaf
sudo touch /etc/httpd/logs/ikari-appleaf/error_log
sudo touch /etc/httpd/logs/ikari-appleaf/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-appleaf

#ikari-pi
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_pi
sudo mkdir /etc/httpd/logs/ikari-pi
sudo touch /etc/httpd/logs/ikari-pi/error_log
sudo touch /etc/httpd/logs/ikari-pi/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-pi

#ikari-asia
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_asia
sudo mkdir /etc/httpd/logs/ikari-asia
sudo touch /etc/httpd/logs/ikari-asia/error_log
sudo touch /etc/httpd/logs/ikari-asia/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-asia

#ikari-brsg
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_brsg
sudo mkdir /etc/httpd/logs/ikari-brsg
sudo touch /etc/httpd/logs/ikari-brsg/error_log
sudo touch /etc/httpd/logs/ikari-brsg/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-brsg

#ikari-cees
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_cees
sudo mkdir /etc/httpd/logs/ikari-cees
sudo touch /etc/httpd/logs/ikari-cees/error_log
sudo touch /etc/httpd/logs/ikari-cees/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-cees

#ikari-collabogate
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_collabogate
sudo mkdir /etc/httpd/logs/ikari-collabogate
sudo touch /etc/httpd/logs/ikari-collabogate/error_log
sudo touch /etc/httpd/logs/ikari-collabogate/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-collabogate

#ikari-concordia
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_concordia
sudo mkdir /etc/httpd/logs/ikari-concordia
sudo touch /etc/httpd/logs/ikari-concordia/error_log
sudo touch /etc/httpd/logs/ikari-concordia/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-concordia


#ikari-jlink
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_jlink
sudo mkdir /etc/httpd/logs/ikari-jlink
sudo touch /etc/httpd/logs/ikari-jlink/error_log
sudo touch /etc/httpd/logs/ikari-jlink/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-jlink

#ikari-crown
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_crown
sudo mkdir /etc/httpd/logs/ikari-crown
sudo touch /etc/httpd/logs/ikari-crown/error_log
sudo touch /etc/httpd/logs/ikari-crown/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-crown

#ikari-daisho
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_daisho
sudo mkdir /etc/httpd/logs/ikari-daisho
sudo touch /etc/httpd/logs/ikari-daisho/error_log
sudo touch /etc/httpd/logs/ikari-daisho/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-daisho

#ikari-eternal
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_eternal
sudo mkdir /etc/httpd/logs/ikari-eternal
sudo touch /etc/httpd/logs/ikari-eternal/error_log
sudo touch /etc/httpd/logs/ikari-eternal/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-eternal

#ikari-front
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_front
sudo mkdir /etc/httpd/logs/ikari-front
sudo touch /etc/httpd/logs/ikari-front/error_log
sudo touch /etc/httpd/logs/ikari-front/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-front

#ikari-fukushima
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_fukushima
sudo mkdir /etc/httpd/logs/ikari-fukushima
sudo touch /etc/httpd/logs/ikari-fukushima/error_log
sudo touch /etc/httpd/logs/ikari-fukushima/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-fukushima

#ikari-gevo
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_gevo
sudo mkdir /etc/httpd/logs/ikari-gevo
sudo touch /etc/httpd/logs/ikari-gevo/error_log
sudo touch /etc/httpd/logs/ikari-gevo/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-gevo

#ikari-globe
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_globe
sudo mkdir /etc/httpd/logs/ikari-globe
sudo touch /etc/httpd/logs/ikari-globe/error_log
sudo touch /etc/httpd/logs/ikari-globe/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-globe

#ikari-growth
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_growth
sudo mkdir /etc/httpd/logs/ikari-growth
sudo touch /etc/httpd/logs/ikari-growth/error_log
sudo touch /etc/httpd/logs/ikari-growth/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-growth

#ikari-hk
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_hk
sudo mkdir /etc/httpd/logs/ikari-hk
sudo touch /etc/httpd/logs/ikari-hk/error_log
sudo touch /etc/httpd/logs/ikari-hk/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-hk


#ikari-inventis
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_inventis
sudo mkdir /etc/httpd/logs/ikari-inventis
sudo touch /etc/httpd/logs/ikari-inventis/error_log
sudo touch /etc/httpd/logs/ikari-inventis/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-inventis

#ikari-izumo
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_izumo
sudo mkdir /etc/httpd/logs/ikari-izumo
sudo touch /etc/httpd/logs/ikari-izumo/error_log
sudo touch /etc/httpd/logs/ikari-izumo/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-izumo

#ikari-jwba
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_jwba
sudo mkdir /etc/httpd/logs/ikari-jwba
sudo touch /etc/httpd/logs/ikari-jwba/error_log
sudo touch /etc/httpd/logs/ikari-jwba/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-jwba

#ikari-jwbh
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_jwbh
sudo mkdir /etc/httpd/logs/ikari-jwbh
sudo touch /etc/httpd/logs/ikari-jwbh/error_log
sudo touch /etc/httpd/logs/ikari-jwbh/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-jwbh

#ikari-kck
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_kck
sudo mkdir /etc/httpd/logs/ikari-kck
sudo touch /etc/httpd/logs/ikari-kck/error_log
sudo touch /etc/httpd/logs/ikari-kck/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-kck

#ikari-kento
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_kento
sudo mkdir /etc/httpd/logs/ikari-kento
sudo touch /etc/httpd/logs/ikari-kento/error_log
sudo touch /etc/httpd/logs/ikari-kento/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-kento

#ikari-lapeche
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_lapeche
sudo mkdir /etc/httpd/logs/ikari-lapeche
sudo touch /etc/httpd/logs/ikari-lapeche/error_log
sudo touch /etc/httpd/logs/ikari-lapeche/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-lapeche

#ikari-lively
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_lively
sudo mkdir /etc/httpd/logs/ikari-lively
sudo touch /etc/httpd/logs/ikari-lively/error_log
sudo touch /etc/httpd/logs/ikari-lively/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-lively

#ikari-mediamix
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_mediamix
sudo mkdir /etc/httpd/logs/ikari-mediamix
sudo touch /etc/httpd/logs/ikari-mediamix/error_log
sudo touch /etc/httpd/logs/ikari-mediamix/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-mediamix

#ikari-mirapro
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_mirapro
sudo mkdir /etc/httpd/logs/ikari-mirapro
sudo touch /etc/httpd/logs/ikari-mirapro/error_log
sudo touch /etc/httpd/logs/ikari-mirapro/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-mirapro

#ikari-msj
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_msj
sudo mkdir /etc/httpd/logs/ikari-msj
sudo touch /etc/httpd/logs/ikari-msj/error_log
sudo touch /etc/httpd/logs/ikari-msj/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-msj

#ikari-muto
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_muto
sudo mkdir /etc/httpd/logs/ikari-muto
sudo touch /etc/httpd/logs/ikari-muto/error_log
sudo touch /etc/httpd/logs/ikari-muto/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-muto

#ikari-nitto
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_nitto
sudo mkdir /etc/httpd/logs/ikari-nitto
sudo touch /etc/httpd/logs/ikari-nitto/error_log
sudo touch /etc/httpd/logs/ikari-nitto/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-nitto

#ikari-nitto
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_nittoold
sudo mkdir /etc/httpd/logs/ikari-nitto-old
sudo touch /etc/httpd/logs/ikari-nitto-old/error_log
sudo touch /etc/httpd/logs/ikari-nitto-old/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-nitto-old

#ikari-npk
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_npk
sudo mkdir /etc/httpd/logs/ikari-npk
sudo touch /etc/httpd/logs/ikari-npk/error_log
sudo touch /etc/httpd/logs/ikari-npk/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-npk

#ikari-numajiri
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_numajiri
sudo mkdir /etc/httpd/logs/ikari-numajiri
sudo touch /etc/httpd/logs/ikari-numajiri/error_log
sudo touch /etc/httpd/logs/ikari-numajiri/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-numajiri

#ikari-ohtani
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_ohtani
sudo mkdir /etc/httpd/logs/ikari-ohtani
sudo touch /etc/httpd/logs/ikari-ohtani/error_log
sudo touch /etc/httpd/logs/ikari-ohtani/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-ohtani

#ikari-pkan
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_pkan
sudo mkdir /etc/httpd/logs/ikari-pkan
sudo touch /etc/httpd/logs/ikari-pkan/error_log
sudo touch /etc/httpd/logs/ikari-pkan/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-pkan

#ikari-pkanold
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_pkanold
sudo mkdir /etc/httpd/logs/ikari-pkanold
sudo touch /etc/httpd/logs/ikari-pkanold/error_log
sudo touch /etc/httpd/logs/ikari-pkanold/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-pkanold

#ikari-sanko
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_sanko
sudo mkdir /etc/httpd/logs/ikari-sanko
sudo touch /etc/httpd/logs/ikari-sanko/error_log
sudo touch /etc/httpd/logs/ikari-sanko/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-sanko

#ikari-sential
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_sential
sudo mkdir /etc/httpd/logs/ikari-sential
sudo touch /etc/httpd/logs/ikari-sential/error_log
sudo touch /etc/httpd/logs/ikari-sential/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-sential

#ikari-sgk
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_sgk
sudo mkdir /etc/httpd/logs/ikari-sgk
sudo touch /etc/httpd/logs/ikari-sgk/error_log
sudo touch /etc/httpd/logs/ikari-sgk/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-sgk

#ikari-sideway
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_sideway
sudo mkdir /etc/httpd/logs/ikari-sideway
sudo touch /etc/httpd/logs/ikari-sideway/error_log
sudo touch /etc/httpd/logs/ikari-sideway/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-sideway

#ikari-star
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_star
sudo mkdir /etc/httpd/logs/ikari-star
sudo touch /etc/httpd/logs/ikari-star/error_log
sudo touch /etc/httpd/logs/ikari-star/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-star

#ikari-sun
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_sun
sudo mkdir /etc/httpd/logs/ikari-sun
sudo touch /etc/httpd/logs/ikari-sun/error_log
sudo touch /etc/httpd/logs/ikari-sun/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-sun

#ikari-suntecks
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_suntecks
sudo mkdir /etc/httpd/logs/ikari-suntecks
sudo touch /etc/httpd/logs/ikari-suntecks/error_log
sudo touch /etc/httpd/logs/ikari-suntecks/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-suntecks


#ikari-taga
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_taga
sudo mkdir /etc/httpd/logs/ikari-taga
sudo touch /etc/httpd/logs/ikari-taga/error_log
sudo touch /etc/httpd/logs/ikari-taga/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-taga

#ikari-tier
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_tier
sudo mkdir /etc/httpd/logs/ikari-tier
sudo touch /etc/httpd/logs/ikari-tier/error_log
sudo touch /etc/httpd/logs/ikari-tier/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-tier

#ikari-tmg
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_tmg
sudo mkdir /etc/httpd/logs/ikari-tmg
sudo touch /etc/httpd/logs/ikari-tmg/error_log
sudo touch /etc/httpd/logs/ikari-tmg/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-tmg

#ikari-venture
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_venture
sudo mkdir /etc/httpd/logs/ikari-venture
sudo touch /etc/httpd/logs/ikari-venture/error_log
sudo touch /etc/httpd/logs/ikari-venture/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-venture

#ikari-verano
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_verano
sudo mkdir /etc/httpd/logs/ikari-verano
sudo touch /etc/httpd/logs/ikari-verano/error_log
sudo touch /etc/httpd/logs/ikari-verano/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-verano

#ikari-victory
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_victory
sudo mkdir /etc/httpd/logs/ikari-victory
sudo touch /etc/httpd/logs/ikari-victory/error_log
sudo touch /etc/httpd/logs/ikari-victory/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-victory

#ikari-vlof
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_vlof
sudo mkdir /etc/httpd/logs/ikari-vlof
sudo touch /etc/httpd/logs/ikari-vlof/error_log
sudo touch /etc/httpd/logs/ikari-vlof/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-vlof

#ikari-wdh
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_wdh
sudo mkdir /etc/httpd/logs/ikari-wdh
sudo touch /etc/httpd/logs/ikari-wdh/error_log
sudo touch /etc/httpd/logs/ikari-wdh/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-wdh

#ikari-ikari
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_prod_ikari
sudo mkdir /etc/httpd/logs/ikari-ikari
sudo touch /etc/httpd/logs/ikari-ikari/error_log
sudo touch /etc/httpd/logs/ikari-ikari/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-ikari

sudo service httpd restart
