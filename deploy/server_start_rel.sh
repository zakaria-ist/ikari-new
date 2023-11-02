#!/bin/bash

#Copy all the test config files
sudo rsync -avzC /home/ec2-user/projects/ikari/config/rel/ /etc/httpd/conf.d


#ikari-amigos
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_amigos
sudo mkdir /etc/httpd/logs/ikari-amigos
sudo touch /etc/httpd/logs/ikari-amigos/error_log
sudo touch /etc/httpd/logs/ikari-amigos/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-amigos

#ikari-appleaf
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_appleaf
sudo mkdir /etc/httpd/logs/ikari-appleaf
sudo touch /etc/httpd/logs/ikari-appleaf/error_log
sudo touch /etc/httpd/logs/ikari-appleaf/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-appleaf

#ikari-appleaf
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_pi
sudo mkdir /etc/httpd/logs/ikari-pi
sudo touch /etc/httpd/logs/ikari-pi/error_log
sudo touch /etc/httpd/logs/ikari-pi/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-pi

#ikari-asia
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_asia
sudo mkdir /etc/httpd/logs/ikari-asia
sudo touch /etc/httpd/logs/ikari-asia/error_log
sudo touch /etc/httpd/logs/ikari-asia/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-asia

#ikari-brsg
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_brsg
sudo mkdir /etc/httpd/logs/ikari-brsg
sudo touch /etc/httpd/logs/ikari-brsg/error_log
sudo touch /etc/httpd/logs/ikari-brsg/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-brsg

#ikari-jlink
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_jlink
sudo mkdir /etc/httpd/logs/ikari-jlink
sudo touch /etc/httpd/logs/ikari-jlink/error_log
sudo touch /etc/httpd/logs/ikari-jlink/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-jlink

#ikari-cees
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_cees
sudo mkdir /etc/httpd/logs/ikari-cees
sudo touch /etc/httpd/logs/ikari-cees/error_log
sudo touch /etc/httpd/logs/ikari-cees/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-cees

#ikari-collabogate
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_collabogate
sudo mkdir /etc/httpd/logs/ikari-collabogate
sudo touch /etc/httpd/logs/ikari-collabogate/error_log
sudo touch /etc/httpd/logs/ikari-collabogate/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-collabogate
=
#ikari-concordia
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_concordia
sudo mkdir /etc/httpd/logs/ikari-concordia
sudo touch /etc/httpd/logs/ikari-concordia/error_log
sudo touch /etc/httpd/logs/ikari-concordia/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-concordia

#ikari-crown
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_crown
sudo mkdir /etc/httpd/logs/ikari-crown
sudo touch /etc/httpd/logs/ikari-crown/error_log
sudo touch /etc/httpd/logs/ikari-crown/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-crown

#ikari-daisho
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_daisho
sudo mkdir /etc/httpd/logs/ikari-daisho
sudo touch /etc/httpd/logs/ikari-daisho/error_log
sudo touch /etc/httpd/logs/ikari-daisho/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-daisho

#ikari-demo
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_demo
sudo mkdir /etc/httpd/logs/ikari-demo
sudo touch /etc/httpd/logs/ikari-demo/error_log
sudo touch /etc/httpd/logs/ikari-demo/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-demo

#ikari-developer
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_developer
sudo mkdir /etc/httpd/logs/ikari-developer
sudo touch /etc/httpd/logs/ikari-developer/error_log
sudo touch /etc/httpd/logs/ikari-developer/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-developer

#ikari-eternal
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_eternal
sudo mkdir /etc/httpd/logs/ikari-eternal
sudo touch /etc/httpd/logs/ikari-eternal/error_log
sudo touch /etc/httpd/logs/ikari-eternal/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-eternal

#ikari-front
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_front
sudo mkdir /etc/httpd/logs/ikari-front
sudo touch /etc/httpd/logs/ikari-front/error_log
sudo touch /etc/httpd/logs/ikari-front/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-front

#ikari-fukushima
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_fukushima
sudo mkdir /etc/httpd/logs/ikari-fukushima
sudo touch /etc/httpd/logs/ikari-fukushima/error_log
sudo touch /etc/httpd/logs/ikari-fukushima/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-fukushima

#ikari-gevo
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_gevo
sudo mkdir /etc/httpd/logs/ikari-gevo
sudo touch /etc/httpd/logs/ikari-gevo/error_log
sudo touch /etc/httpd/logs/ikari-gevo/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-gevo

#ikari-globe
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_globe
sudo mkdir /etc/httpd/logs/ikari-globe
sudo touch /etc/httpd/logs/ikari-globe/error_log
sudo touch /etc/httpd/logs/ikari-globe/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-globe

#ikari-growth
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_growth
sudo mkdir /etc/httpd/logs/ikari-growth
sudo touch /etc/httpd/logs/ikari-growth/error_log
sudo touch /etc/httpd/logs/ikari-growth/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-growth

#ikari-hk
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_hk
sudo mkdir /etc/httpd/logs/ikari-hk
sudo touch /etc/httpd/logs/ikari-hk/error_log
sudo touch /etc/httpd/logs/ikari-hk/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-hk


#ikari-inventis
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_inventis
sudo mkdir /etc/httpd/logs/ikari-inventis
sudo touch /etc/httpd/logs/ikari-inventis/error_log
sudo touch /etc/httpd/logs/ikari-inventis/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-inventis

#ikari-izumo
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_izumo
sudo mkdir /etc/httpd/logs/ikari-izumo
sudo touch /etc/httpd/logs/ikari-izumo/error_log
sudo touch /etc/httpd/logs/ikari-izumo/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-izumo

#ikari-jwba
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_jwba
sudo mkdir /etc/httpd/logs/ikari-jwba
sudo touch /etc/httpd/logs/ikari-jwba/error_log
sudo touch /etc/httpd/logs/ikari-jwba/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-jwba

#ikari-jwbh
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_jwbh
sudo mkdir /etc/httpd/logs/ikari-jwbh
sudo touch /etc/httpd/logs/ikari-jwbh/error_log
sudo touch /etc/httpd/logs/ikari-jwbh/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-jwbh

#ikari-kck
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_kck
sudo mkdir /etc/httpd/logs/ikari-kck
sudo touch /etc/httpd/logs/ikari-kck/error_log
sudo touch /etc/httpd/logs/ikari-kck/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-kck

#ikari-kento
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_kento
sudo mkdir /etc/httpd/logs/ikari-kento
sudo touch /etc/httpd/logs/ikari-kento/error_log
sudo touch /etc/httpd/logs/ikari-kento/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-kento

#ikari-lapeche
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_lapeche
sudo mkdir /etc/httpd/logs/ikari-lapeche
sudo touch /etc/httpd/logs/ikari-lapeche/error_log
sudo touch /etc/httpd/logs/ikari-lapeche/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-lapeche

#ikari-lively
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_lively
sudo mkdir /etc/httpd/logs/ikari-lively
sudo touch /etc/httpd/logs/ikari-lively/error_log
sudo touch /etc/httpd/logs/ikari-lively/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-lively

#ikari-mediamix
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_mediamix
sudo mkdir /etc/httpd/logs/ikari-mediamix
sudo touch /etc/httpd/logs/ikari-mediamix/error_log
sudo touch /etc/httpd/logs/ikari-mediamix/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-mediamix

#ikari-mirapro
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_mirapro
sudo mkdir /etc/httpd/logs/ikari-mirapro
sudo touch /etc/httpd/logs/ikari-mirapro/error_log
sudo touch /etc/httpd/logs/ikari-mirapro/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-mirapro

#ikari-msj
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_msj
sudo mkdir /etc/httpd/logs/ikari-msj
sudo touch /etc/httpd/logs/ikari-msj/error_log
sudo touch /etc/httpd/logs/ikari-msj/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-msj

#ikari-muto
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_muto
sudo mkdir /etc/httpd/logs/ikari-muto
sudo touch /etc/httpd/logs/ikari-muto/error_log
sudo touch /etc/httpd/logs/ikari-muto/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-muto

#ikari-nitto
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_nitto
sudo mkdir /etc/httpd/logs/ikari-nitto
sudo touch /etc/httpd/logs/ikari-nitto/error_log
sudo touch /etc/httpd/logs/ikari-nitto/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-nitto

#ikari-npk
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_npk
sudo mkdir /etc/httpd/logs/ikari-npk
sudo touch /etc/httpd/logs/ikari-npk/error_log
sudo touch /etc/httpd/logs/ikari-npk/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-npk

#ikari-numajiri
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_numajiri
sudo mkdir /etc/httpd/logs/ikari-numajiri
sudo touch /etc/httpd/logs/ikari-numajiri/error_log
sudo touch /etc/httpd/logs/ikari-numajiri/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-numajiri

#ikari-ohtani
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_ohtani
sudo mkdir /etc/httpd/logs/ikari-ohtani
sudo touch /etc/httpd/logs/ikari-ohtani/error_log
sudo touch /etc/httpd/logs/ikari-ohtani/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-ohtani

#ikari-pkan
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_pkan
sudo mkdir /etc/httpd/logs/ikari-pkan
sudo touch /etc/httpd/logs/ikari-pkan/error_log
sudo touch /etc/httpd/logs/ikari-pkan/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-pkan

#ikari-release
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_release
sudo mkdir /etc/httpd/logs/ikari-release
sudo touch /etc/httpd/logs/ikari-release/error_log
sudo touch /etc/httpd/logs/ikari-release/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-release

#ikari-sanko
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_sanko
sudo mkdir /etc/httpd/logs/ikari-sanko
sudo touch /etc/httpd/logs/ikari-sanko/error_log
sudo touch /etc/httpd/logs/ikari-sanko/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-sanko

#ikari-sential
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_sential
sudo mkdir /etc/httpd/logs/ikari-sential
sudo touch /etc/httpd/logs/ikari-sential/error_log
sudo touch /etc/httpd/logs/ikari-sential/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-sential

#ikari-sgk
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_sgk
sudo mkdir /etc/httpd/logs/ikari-sgk
sudo touch /etc/httpd/logs/ikari-sgk/error_log
sudo touch /etc/httpd/logs/ikari-sgk/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-sgk

#ikari-sideway
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_sideway
sudo mkdir /etc/httpd/logs/ikari-sideway
sudo touch /etc/httpd/logs/ikari-sideway/error_log
sudo touch /etc/httpd/logs/ikari-sideway/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-sideway

#ikari-star
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_star
sudo mkdir /etc/httpd/logs/ikari-star
sudo touch /etc/httpd/logs/ikari-star/error_log
sudo touch /etc/httpd/logs/ikari-star/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-star

#ikari-sun
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_sun
sudo mkdir /etc/httpd/logs/ikari-sun
sudo touch /etc/httpd/logs/ikari-sun/error_log
sudo touch /etc/httpd/logs/ikari-sun/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-sun

#ikari-suntecks
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_suntecks
sudo mkdir /etc/httpd/logs/ikari-suntecks
sudo touch /etc/httpd/logs/ikari-suntecks/error_log
sudo touch /etc/httpd/logs/ikari-suntecks/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-suntecks

#ikari-taga
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_taga
sudo mkdir /etc/httpd/logs/ikari-taga
sudo touch /etc/httpd/logs/ikari-taga/error_log
sudo touch /etc/httpd/logs/ikari-taga/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-taga

#ikari-tier
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_tier
sudo mkdir /etc/httpd/logs/ikari-tier
sudo touch /etc/httpd/logs/ikari-tier/error_log
sudo touch /etc/httpd/logs/ikari-tier/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-tier

#ikari-tmg
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_tmg
sudo mkdir /etc/httpd/logs/ikari-tmg
sudo touch /etc/httpd/logs/ikari-tmg/error_log
sudo touch /etc/httpd/logs/ikari-tmg/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-tmg

#ikari-venture
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_venture
sudo mkdir /etc/httpd/logs/ikari-venture
sudo touch /etc/httpd/logs/ikari-venture/error_log
sudo touch /etc/httpd/logs/ikari-venture/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-venture

#ikari-verano
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_verano
sudo mkdir /etc/httpd/logs/ikari-verano
sudo touch /etc/httpd/logs/ikari-verano/error_log
sudo touch /etc/httpd/logs/ikari-verano/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-verano

#ikari-victory
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_victory
sudo mkdir /etc/httpd/logs/ikari-victory
sudo touch /etc/httpd/logs/ikari-victory/error_log
sudo touch /etc/httpd/logs/ikari-victory/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-victory

#ikari-vlof
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_vlof
sudo mkdir /etc/httpd/logs/ikari-vlof
sudo touch /etc/httpd/logs/ikari-vlof/error_log
sudo touch /etc/httpd/logs/ikari-vlof/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-vlof

#ikari-wdh
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_wdh
sudo mkdir /etc/httpd/logs/ikari-wdh
sudo touch /etc/httpd/logs/ikari-wdh/error_log
sudo touch /etc/httpd/logs/ikari-wdh/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-wdh

#ikari-ikari
/home/ec2-user/projects/ikari/venv/bin/python3.4 /home/ec2-user/projects/ikari/src/ikari/manage.py migrate --settings ikari.settings_rel_ikari
sudo mkdir /etc/httpd/logs/ikari-ikari
sudo touch /etc/httpd/logs/ikari-ikari/error_log
sudo touch /etc/httpd/logs/ikari-ikari/access_log
sudo chmod 777 -R /etc/httpd/logs/ikari-ikari

sudo service httpd restart
