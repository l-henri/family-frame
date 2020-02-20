sleep 10
DISPLAY=:0.0 XAUTHORITY=/home/pi/.Xauthority /usr/bin/feh -Z -x -F -Y -p -q -z -R 60 -D 15.0 /home/pi/Documents/family-frame/photos/pics/

# -Z zoom pictures full screen
# -x borderless zindows
# -F = Plein écran
# -Y cache le curseur
# -p preload, to avoid empty images
# -q Quiet, do nt report errors
# -z = Aleatoire
# -R = Reload, refresh when new pictures
# -D = Time delay between pictures