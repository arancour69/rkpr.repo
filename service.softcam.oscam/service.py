#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os
import signal
import subprocess
import sys
import json
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import random
import sqlite3
import urllib2
import datetime
import shutil
from xml.dom import minidom
from traceback import print_exc
from time import gmtime, strftime
from xbmc import Monitor

_Addon_ = xbmcaddon.Addon()
_AddonPath_ = xbmc.translatePath(_Addon_.getAddonInfo("path"))
_UserData_ = xbmc.translatePath(_Addon_.getAddonInfo("profile"))

BASE_RESOURCE_PATH = os.path.join(_AddonPath_, "resources")
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))

import oscam.database as database

class OSCamService(Monitor):
    def __init__(self, *args, **kwargs):
        Monitor.__init__(self)
        self.IniciarServico=False
        self.Servico=None
        self.VerificandoArquivos()
        self.CarregandoConfiguracoes()

    def VerificandoArquivos(self):
        self.Log("Definindo permissões ...")
        subprocess.Popen(["busybox", "chmod", "+x", "oscam"], stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
        self.Log("Verificando pastas ...")

        if not os.path.exists(os.path.join(_UserData_, "config")):
            self.CopyDirectory(os.path.join(BASE_RESOURCE_PATH, "default_config"), os.path.join(_UserData_, "config"))
        
        if not _Addon_.getSetting(id="LOG_PADRAO") == "true":
            if not _Addon_.getSetting(id="LOG_PASTA"):
				self.Aviso("Pasta de Log", "Pasta não definida, usando padrão.", xbmcgui.NOTIFICATION_WARNING)
        if not os.path.exists(os.path.join(_UserData_, "log")):
            os.makedirs(os.path.join(_UserData_, "log"))

    def CarregandoConfiguracoes(self):			
        self.Log("Verificando servidores cadastrados ...")
        if not os.path.exists(os.path.join(_UserData_, "database")) or not os.path.exists(os.path.join(os.path.join(_UserData_, "database"), "Settings.db")):
            self.CopyDirectory(os.path.join(BASE_RESOURCE_PATH, "database"), os.path.join(_UserData_, "database"));
        if _Addon_.getSetting(id="WEB_STATUS") == "true":
            self.Servidores = []
        self.BD = database.BD()
        Readers = self.BD.ObterArrayReaders()

        if len(Readers) > 0:
            f = open(os.path.join(_UserData_, "config/oscam.server"), "w")
            for rowid, URL, Porta, Usuario, Senha, DESKey, Status in Readers:
                if Status == "checked":
                    self.IniciarServico=True
                    if _Addon_.getSetting(id="WEB_STATUS") == "true":
                        self.Servidores.append(["Servidor_%s" % rowid, "Servidor %s não configurado ou pausado." % rowid])
                f.write("[reader]\n")
                f.write("enable                        = %s\n" % (str(1) if Status == "checked" else str(0)))
                f.write("label                         = Servidor_%s\n" % rowid)
                f.write("protocol                      = newcamd\n")
                f.write("device                        = %s,%s\n" % (URL, Porta))
                f.write("key                           = %s\n" % DESKey)
                f.write("user                          = %s\n" % Usuario)
                f.write("password                      = %s\n" % Senha)
                f.write("connectoninit                 = 1\n")
                f.write("caid                          = 1802,1861\n")
                f.write("group                         = 1\n")
                self.Log("[reader]\n")
                self.Log("enable                        = %s\n" % (str(1) if Status == "checked" else str(0)))
                self.Log("label                         = Servidor_%s\n" % rowid)
                self.Log("protocol                      = newcamd\n")
                self.Log("device                        = %s,%s\n" % (URL, Porta))
                self.Log("key                           = %s\n" % DESKey)
                self.Log("user                          = %s\n" % Usuario)
                self.Log("password                      = %s\n" % Senha)
                self.Log("connectoninit                 = 1\n")
                self.Log("caid                          = 1802,1861\n")
                self.Log("group                         = 1\n")
            f.close()

        if self.IniciarServico:
            f = open(os.path.join(_UserData_, "config/oscam.conf"), "w")
            pasta_log = os.path.join(_UserData_, "log") + "/"
            if not _Addon_.getSetting(id="LOG_PADRAO") == "true" and _Addon_.getSetting(id="LOG_PASTA"):
                pasta_log = _Addon_.getSetting(id="LOG_PASTA")
            self.Log("Pasta de Log: %s" % pasta_log)
            f.write("[global]\n")
            f.write("nice                          = -1\n")
            f.write("WaitForCards                  = 0\n")
            f.write("usrfile                       = %soscamuser.log\n" % pasta_log)
            f.write("logfile                       = %soscam.log\n" % pasta_log)
            f.write("cwlogdir                      = %scw\n" % pasta_log)
            f.write("\n")
            f.write("[radegast]\n")
            f.write("port                          = 9990\n")
            f.write("allowed                       = 127.0.0.1\n")
            f.write("user                          = local\n")
            if _Addon_.getSetting(id="WEB_STATUS") == "true":
                f.write("\n")
                f.write("[webif]\n")
                f.write("httpuser                      = %s\n" % _Addon_.getSetting(id="WEB_USER"))
                f.write("httppwd                       = %s\n" % _Addon_.getSetting(id="WEB_PWD"))
                f.write("httpport                      = %s\n" % str(_Addon_.getSetting(id="WEB_PORT")))
                f.write("httpallowed                   = 0.0.0.0-255.255.255.255\n")
            else:
                self.Aviso("Acesso WEB (DESATIVADO)", "Você não ira receber avisos de status do Servidor Pago.", xbmcgui.NOTIFICATION_WARNING)
            f.close()
    
    def Log(self, txt):
        if _Addon_.getSetting(id="DEBUG") == "true":
            message = "%s: %s" % (_Addon_.getAddonInfo("name"), txt.encode("utf8")) # txt.encode("ascii", "ignore"))
            xbmc.log(msg=message, level=xbmc.LOGDEBUG)
            
    def IniciarMonitor(self):
        if not self.IniciarServico:
            return
        try:
            if not self.Servico:
                self.Servico = subprocess.Popen([os.path.join(BASE_RESOURCE_PATH, "bin/oscam"), "-c", os.path.join(_UserData_, "config")], stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
            xbmc.sleep(1000)
            if not self.Servico.poll() == None:
                self.Servico = subprocess.Popen([os.path.join(BASE_RESOURCE_PATH, "bin/oscam"), "-c", os.path.join(_UserData_, "config")], stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
            if _Addon_.getSetting(id="WEB_STATUS") == "true" and self.IniciarServico and self.Servico and self.Servico.poll() == None:
                for i, Servidor in enumerate(self.Servidores):
                    if self.IniciarServico and self.Servico and self.Servico.poll() == None:
						xbmc.sleep(1000)
						StatusAtual = self.OSCamStatusCS(Servidor[0])
						if not Servidor[1] == StatusAtual:
							self.Servidores[i][1] = StatusAtual
							self.Log(StatusAtual)
							if StatusAtual.__contains__("conectado"):
								self.Aviso("Aviso", StatusAtual, xbmcgui.NOTIFICATION_INFO)
							else:
								self.Aviso("Aviso", StatusAtual, xbmcgui.NOTIFICATION_WARNING)
        except:
            pass

    def onSettingsChanged(self):
        self.Sair()
        self.CarregandoConfiguracoes()

    def Aviso(self, Titulo, Mensagem, Icone=_Addon_.getAddonInfo('icon')):
        if _Addon_.getSetting(id="AVISO_CS") == "true":
			xbmcgui.Dialog().notification(Titulo, Mensagem, Icone)

    def Sair(self):
        self.IniciarServico=False
        if self.Servico:
            self.Servico.kill()
            xbmc.sleep(1000)
            subprocess.Popen(["busybox", "killall", "-9", "oscam"], stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
            xbmc.sleep(1000)
        self.Servico = None
                
    def OSCamStatusCS(self, svr):
        URL      = ("http://127.0.0.1:%s/oscamapi.html?part=status" % str(_Addon_.getSetting(id="WEB_PORT")))
        Realm    = "Forbidden"
        Username = _Addon_.getSetting(id="WEB_USER")
        Password = _Addon_.getSetting(id="WEB_PWD")

        authhandler = urllib2.HTTPDigestAuthHandler()
        authhandler.add_password(Realm, URL, Username, Password)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)

        try:
            xml = urllib2.urlopen(URL)
            dom = minidom.parseString(xml.read())

            nListStatus = dom.getElementsByTagName("status")
            for nStatus in nListStatus:
                for nClient in nStatus.getElementsByTagName("client"):
                    if nClient.getAttribute("name") == svr:
                        sValor = nClient.getElementsByTagName("connection")[0].firstChild.nodeValue
                        if sValor == "OK":
                            return "%s conectado." % svr.replace("_", " ")
                        elif sValor == "CONNECTED":
                            return "%s conectado." % svr.replace("_", " ")
                        elif sValor == "UNKNOWN":
                            return "%s: Verifique os dados cadastrados." % svr.replace("_", " ")
                        else:
                            return "%s com status (%s) não cadastrado." % (svr.replace("_", " "), sValor)
        except:
            pass
        return "%s não configurado ou pausado." % svr.replace("_", " ")

    def CopyDirectory(self, src, dest):
        try:
            shutil.copytree(src, dest)
        except shutil.Error as e:
            self.Log("Diretório não copiado. Erro: %s" % e)
            pass
        except OSError as e:
            self.Log("Diretório não copiado. Erro: %s" % e)
            pass

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")
    Servico = OSCamService()
    while not Servico.waitForAbort(2):
        if Servico.IniciarServico:
            Servico.IniciarMonitor()
    Servico.Sair()