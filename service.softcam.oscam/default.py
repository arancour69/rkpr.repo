#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os
import sys
import ast
import json
import xbmc
import shutil
import urllib2
import xbmcgui
import commands
import xbmcaddon

_Addon_ = xbmcaddon.Addon()
_AddonPath_ = xbmc.translatePath(_Addon_.getAddonInfo("path"))
_UserData_ = xbmc.translatePath(_Addon_.getAddonInfo("profile"))

BASE_RESOURCE_PATH = os.path.join(_AddonPath_, "resources")
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))

import oscam.database as database
import pyxbmct.addonwindow as pyxbmct

# Debug VS2010
#import ptvsd
#ptvsd.enable_attach(secret = 'pwd')
#ptvsd.wait_for_attach()

class abrir_url(object):
	def __init__(self, url, close=True, proxy=None, post=None, mobile=False, referer=None, cookie=None, output='',
				 timeout='10'):
		if not proxy == None:
			proxy_handler = urllib2.ProxyHandler({'http': '%s' % (proxy)})
			opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
			opener = urllib2.install_opener(opener)
		if output == 'cookie' or not close == True:
			import cookielib

			cookie_handler = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
			opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
			opener = urllib2.install_opener(opener)
		if not post == None:
			request = urllib2.Request(url, post)
		else:
			request = urllib2.Request(url, None)
		if mobile == True:
			request.add_header('User-Agent',
							   'Mozilla/5.0 (iPhone; CPU; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
		else:
			request.add_header('User-Agent',
							   'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36')
		if not referer == None:
			request.add_header('Referer', referer)
		if not cookie == None:
			request.add_header('cookie', cookie)
		response = urllib2.urlopen(request, timeout=int(timeout))
		if output == 'cookie':
			result = str(response.headers.get('Set-Cookie'))
		elif output == 'geturl':
			result = response.geturl()
		else:
			result = response.read()
		if close == True:
			response.close()
		self.result = result

class OSCamKS(pyxbmct.AddonDialogWindow):
    def __init__(self, title="Ativar KS - Servidor Gratuito", nid=None, onid=None):
        super(OSCamKS, self).__init__(title)
        self.NID = nid
        self.ONID = onid
        self.setGeometry(600, 350, 7, 3)
        self.set_controls()
        self.load_settings()
        self.connect_controls()
        self.set_navigation()

    def set_controls(self):
        self.LocID = None
        self.Erro = None
        try:
            self.ObterIP("wlan0")
            self.MACAdress = self.ObterMACAddress("wlan0").replace(":", "")
        except:
            self.ObterIP("eth0")
            self.MACAdress = self.ObterMACAddress("eth0").replace(":", "")

        self.Serial = _Addon_.getSetting(id="Serial")
        self.Gravar = False
        self.Usuario = None
        self.Senha = None
        self.URL = None
        self.Porta = None
        self.DataDE = None
        self.DataATE = None
        self.Selecionado = False
        self.URL = "https://atto.tv/actx4ks.php?%s"
        self.lblCID_SUP = pyxbmct.Label("Cidades Suportadas", textColor="0xFFFFFF00")
        self.placeControl(self.lblCID_SUP, 0, 1, 1, 0)
        self.lstCidades = pyxbmct.List(_imageWidth=26)
        self.placeControl(self.lstCidades, 1, 0, rowspan=6, columnspan=3)
        self.btnAtivar = pyxbmct.Button("Ativar", textColor="0xFFFF0000")
        self.placeControl(self.btnAtivar, 6, 1)

    def connect_controls(self):
        self.connect(self.lstCidades, self.lstCheckUncheck)
        self.connect(215, self.btnAtivar_Click)
        self.connect(self.btnAtivar, self.btnAtivar_Click)
        self.connect(pyxbmct.ACTION_NAV_BACK, self.Sair)

    def set_navigation(self):
        self.lstCidades.controlUp(self.btnAtivar)
        self.lstCidades.controlDown(self.btnAtivar)
        self.btnAtivar.setNavigation(self.lstCidades, self.lstCidades, self.btnAtivar, self.btnAtivar)
        if self.lstCidades.size():
            self.setFocus(self.lstCidades)
        else:
            self.setFocus(self.btnAtivar)

    def load_settings(self):
        try:
            Cidades = json.loads(abrir_url(self.URL % "getloc=true").result)
            for cidade in Cidades["state_city"]:
                li = xbmcgui.ListItem("{0} - ({1})".format(cidade["city_name"].encode("utf8"), cidade["state_abbreviation"]), "unchecked", os.path.join(_AddonPath_, "resources", "images", "Unchecked.png"))
                li.setProperty("Path", "?state_id=>{0}&location_id=>{1}".format(cidade["state_id"], cidade["location_id"]))
                self.lstCidades.addItem(li)

            if not self.lstCidades.size():
                self.Erro = True
                self.Aviso("Servidor KS", "Não foi possível obter a lista de cidades!", xbmcgui.NOTIFICATION_ERROR)
        except:
            self.Erro = True
            self.Aviso("Servidor KS", "Não foi possível obter a lista de cidades!", xbmcgui.NOTIFICATION_ERROR)

    def lstCheckUncheck(self):
        if self.Erro:
            self.Aviso("Servidor KS", "Erro interno, saia e entre novamente na tela!", xbmcgui.NOTIFICATION_ERROR)
            return
        li = self.lstCidades.getSelectedItem()
        param = self.ObterParametros(li.getProperty("Path"))

        if self.Selecionado:
            if li.getLabel2() == "checked":
                li.setIconImage(os.path.join(_AddonPath_, "resources", "images", "Unchecked.png"))
                li.setLabel2("unchecked")
                self.Selecionado = False
            else:
                self.Aviso("Aviso", "Você já possui uma cidade selecionada!", xbmcgui.NOTIFICATION_WARNING)
        else:
            self.ONID = int(param["state_id"]) # Remover DEPOIS
            if self.NID in [1, 2, 3, 6, 13] and self.ONID in [1, 2, 3, 6]:
				self.Aviso("Aviso", "Esta cidade já possui IKS Gratuito!", xbmcgui.NOTIFICATION_INFO)
            else:
                li.setIconImage(os.path.join(_AddonPath_, "resources", "images", "Checked.png"))
                li.setLabel2("checked")
                self.Selecionado = True
                self.LocID = param["location_id"]

    def btnAtivar_Click(self):
        if self.Erro:
            self.Aviso("Servidor KS", "Erro interno, saia e entre novamente na tela!", xbmcgui.NOTIFICATION_ERROR)
            return
        if not self.Selecionado:
            self.Aviso("Servidor KS", "Selecione a sua cidade e tente novamente!", xbmcgui.NOTIFICATION_INFO)
            return

        if self.Serial:
            self.Serial = xbmcgui.Dialog().input("Digite o serial do seu aparelho:", self.Serial, type=xbmcgui.INPUT_ALPHANUM).upper()
        else:
            self.Serial = xbmcgui.Dialog().input("Digite o serial do seu aparelho:", type=xbmcgui.INPUT_ALPHANUM).upper()

        if not self.Serial:
            self.Aviso("Servidor KS", "Digite o serial do aparelho localizado embaixo do mesmo!", xbmcgui.NOTIFICATION_WARNING)
            return
        elif not (len(self.Serial) == 9 or len(self.Serial) == 12):
            self.Aviso("Servidor KS", "Serial inválido. O Serial deve conter 9 ou 12 digitos!", xbmcgui.NOTIFICATION_WARNING)
            return

        self.Aviso("Servidor KS", "Obtendo dados, por favor aguarde ...", xbmcgui.NOTIFICATION_INFO)
        try:
            sRetorno = abrir_url(self.URL % "sn={0}{1}&nid={2}&onid={3}&locid={4}".format(self.MACAdress, self.Serial, self.NID, self.ONID, self.LocID)).result
            retorno = json.loads(sRetorno)

            if sRetorno.startswith("{\"errorMessage"):
                self.Aviso("{0} ({1})".format(retorno["errorMessage"]["line2"].encode("utf8") if type(retorno["errorMessage"]["line2"]) is unicode else retorno["errorMessage"]["line2"], retorno["errorMessage"]["line1"]), retorno["errorMessage"]["line3"].encode("utf8"), xbmcgui.NOTIFICATION_ERROR)
            elif sRetorno.startswith("{\"successMessage"):
                from datetime import datetime
                self.Usuario = retorno["successMessage"]["userName"]
                self.Senha = retorno["successMessage"]["userPassword"]
                self.URL = retorno["successMessage"]["urlAddress"]
                self.Porta = retorno["successMessage"]["urlPortNumber"]
                self.DataDE = datetime.strptime(retorno["successMessage"]["activeFromDate"], '%Y%m%d').strftime('%d/%m/%Y')
                self.DataATE = datetime.strptime(retorno["successMessage"]["validUntilDate"], '%Y%m%d').strftime('%d/%m/%Y')
                self.Gravar = True
                self.Aviso("Servidor KS", "Ativado com sucesso até dia {0}".format(self.DataATE), xbmcgui.NOTIFICATION_INFO)
                self.Sair()
        except:
            self.Aviso("Servidor KS", "Não foi possivel contactar o servidor, tente novamente.", xbmcgui.NOTIFICATION_ERROR)
            pass

    def Aviso(self, Titulo, Mensagem, Icone=""):
        xbmcgui.Dialog().notification(Titulo, Mensagem, Icone)

    def ObterIP(self, ifname):
        import socket
        import fcntl
        import struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])

    def ObterMACAddress(self, ifname):
        import socket
        import fcntl
        import struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

    def ObterParametros(self, path):
        param = []
        paramstring = path
        if len(paramstring) >= 2:
            params = path
            cleanedparams = params.replace('?', '')
            if (params[len(params) - 1] == '/'):
                params = params[0:len(params) - 2]
            pairsofparams = cleanedparams.split('&')
            param = {}
            for i in range(len(pairsofparams)):
                splitparams = {}
                splitparams = pairsofparams[i].split('=>')
                if (len(splitparams)) == 2:
                    param[splitparams[0]] = splitparams[1]
        
        return param

    def Sair(self):
        super(OSCamKS, self).close()

class OSCamReader(pyxbmct.AddonDialogWindow):
    def __init__(self, title="Cadastrar Servidor", dados=None):
        super(OSCamReader, self).__init__(title)
        self.setGeometry(600, 350, 7, 3)
        self.set_controls()
        self.connect_controls()
        self.set_navigation()
        self.Gravar=False

        if dados:
            self.txtURL.setText(dados["URL"])
            self.txtPorta.setText(dados["Porta"])
            self.txtUsuario.setText(dados["Usuario"])
            self.txtSenha.setText(dados["Senha"])
            self.txtDESKey.setText(dados["DESKey"])

    def set_controls(self):
        self.lblURL = pyxbmct.Label("URL:", textColor="0xFF00FF00")
        self.placeControl(self.lblURL, 0, 0)
        self.txtURL = pyxbmct.Edit("URL")
        self.placeControl(self.txtURL, 1, 0, 1, 2)
        self.lblPorta = pyxbmct.Label("Porta:", textColor="0xFF00FF00")
        self.placeControl(self.lblPorta, 0, 2)
        self.txtPorta = pyxbmct.Edit("Porta")
        self.placeControl(self.txtPorta, 1, 2)
        self.lblUsuario = pyxbmct.Label("Usuario:", textColor="0xFF00FF00")
        self.placeControl(self.lblUsuario, 2, 0)
        self.txtUsuario = pyxbmct.Edit("Usuario")
        self.placeControl(self.txtUsuario, 3, 0)
        self.lblSenha = pyxbmct.Label("Senha:", textColor="0xFF00FF00")
        self.placeControl(self.lblSenha, 2, 1)
        self.txtSenha = pyxbmct.Edit("Senha", isPassword=True)
        self.placeControl(self.txtSenha, 3, 1)
        self.lblDESKey = pyxbmct.Label("DES Key:", textColor="0xFF00FF00")
        self.placeControl(self.lblDESKey, 4, 0)
        self.txtDESKey = pyxbmct.Edit("DES Key")
        self.placeControl(self.txtDESKey, 5, 0, 1, 3)
        self.txtDESKey.setText('0102030405060708091011121314')
        self.btnSalvar = pyxbmct.Button("Salvar", textColor="0xFFFF0000")
        self.placeControl(self.btnSalvar, 6, 1)
        self.btnCancelar = pyxbmct.Button("Cancelar", textColor="0xFF008000")
        self.placeControl(self.btnCancelar, 6, 2)

    def connect_controls(self):
        self.connect(215, self.btnSalvar_Click)
        self.connect(self.btnSalvar, self.btnSalvar_Click)
        self.connect(216, self.btnCancelar_Click)
        self.connect(pyxbmct.ACTION_NAV_BACK, self.btnCancelar_Click)
        self.connect(self.btnCancelar, self.btnCancelar_Click)
        self.setFocus(self.btnCancelar)  

    def set_navigation(self):
        self.txtURL.setNavigation(self.btnSalvar, self.txtUsuario, self.txtPorta, self.txtPorta)
        self.txtPorta.setNavigation(self.btnSalvar, self.txtUsuario, self.txtURL, self.txtURL)
        self.txtUsuario.setNavigation(self.txtURL, self.txtDESKey, self.txtSenha, self.txtSenha)
        self.txtSenha.setNavigation(self.txtURL, self.txtDESKey, self.txtUsuario, self.txtUsuario)
        self.txtDESKey.setNavigation(self.txtUsuario, self.btnSalvar, self.txtDESKey, self.txtDESKey)
        self.btnSalvar.setNavigation(self.txtDESKey, self.txtURL, self.btnCancelar, self.btnCancelar)
        self.btnCancelar.setNavigation(self.txtDESKey, self.txtURL, self.btnSalvar, self.btnSalvar)

    def btnSalvar_Click(self):
        if not self.txtURL.getText() and not self.txtURL.getText().strip():
            xbmcgui.Dialog().notification("URL", "Campo vazio!", xbmcgui.NOTIFICATION_WARNING)
            return
        if not self.txtPorta.getText() and not self.txtPorta.getText().strip():
            xbmcgui.Dialog().notification("Porta", "Campo vazio!", xbmcgui.NOTIFICATION_WARNING)
            return
        if not self.txtPorta.getText().isdigit():
            xbmcgui.Dialog().notification("Porta", "O valor precisa ser numérico!", xbmcgui.NOTIFICATION_WARNING)
            return
        if not self.txtUsuario.getText() and not self.txtUsuario.getText().strip():
            xbmcgui.Dialog().notification("Usuario", "Campo vazio!", xbmcgui.NOTIFICATION_WARNING)
            return
        if not self.txtSenha.getText() and not self.txtSenha.getText().strip():
            xbmcgui.Dialog().notification("Senha", "Campo vazio!", xbmcgui.NOTIFICATION_WARNING)
            return
        if not self.txtDESKey.getText() and not self.txtDESKey.getText().strip():
            xbmcgui.Dialog().notification("DES Key", "Campo vazio!", xbmcgui.NOTIFICATION_WARNING)
            return
        if not len(self.txtDESKey.getText()) == 28:
            xbmcgui.Dialog().notification("DES Key", "O valor precisa ter 28 caracteres!", xbmcgui.NOTIFICATION_WARNING)
            return
        self.Gravar=True
        super(OSCamReader, self).close()

    def btnCancelar_Click(self):
        super(OSCamReader, self).close()

class OSCamManager(pyxbmct.AddonDialogWindow):
    def __init__(self, title=""):
        super(OSCamManager, self).__init__(title)
        self.setGeometry(800, 450, 9, 4)
        if not os.path.exists(os.path.join(_UserData_, "database")) or not os.path.exists(os.path.join(os.path.join(_UserData_, "database"), "Settings.db")):
            self.CopyDirectory(os.path.join(BASE_RESOURCE_PATH, "database"), os.path.join(_UserData_, "database"));
        self.set_controls()
        self.connect_controls()
        self.set_navigation()
        self.load_settings()

    def set_controls(self):
        self.NID = None
        self.ONID = None
        self.Editar = False
        self.Excluir = False
        self.BD = database.BD()
        self.lblSVR_CAD = pyxbmct.Label("Servidores Cadastrados:", textColor="0xFF00FF00")
        self.placeControl(self.lblSVR_CAD, 0, 0, 1, 0)
        if os.path.exists("/dev/extcmd"):
            self.rbIKS = pyxbmct.RadioButton("Servidor IKS:", textColor="0xFF00FF00", focusedColor="0xFF00FF00")
            self.placeControl(self.rbIKS, 0, 3)
        else:
            self.rbIKS = None
        self.lstServidores = pyxbmct.List(_imageWidth=26)
        self.placeControl(self.lstServidores, 1, 0, rowspan=8, columnspan=4)
        self.btnCadastrar = pyxbmct.Button("Cadastrar", textColor="0xFFFF0000")
        self.placeControl(self.btnCadastrar, 8, 0)
        self.btnEditar = pyxbmct.Button("Editar", textColor="0xFF008000")
        self.placeControl(self.btnEditar, 8, 1)
        self.btnExcluir = pyxbmct.Button("Excluir", textColor="0xFFFFFF00")
        self.placeControl(self.btnExcluir, 8, 2)
        if self.ExecutarCMD("getprop ro.product.brand") == "ATTO" and (self.ExecutarCMD("getprop ro.product.model") == "iSmart" or self.ExecutarCMD("getprop ro.product.model") == "Pixel"):
            self.btnAtivarKS = pyxbmct.Button("Ativar KS", textColor="0xFF0000FF")
            self.placeControl(self.btnAtivarKS, 8, 3)
        else:
            self.btnAtivarKS = None

    def connect_controls(self):
        self.connect(117, self.AbrirConfiguracoes) # Abre configuracoes do Add-on
        self.connect(self.lstServidores, self.lstCheckUncheck)
        self.connect(215, self.btnCadastrar_Click)
        self.connect(self.btnCadastrar, self.btnCadastrar_Click)
        self.connect(216, self.btnEditar_Click)
        self.connect(self.btnEditar, self.btnEditar_Click)
        self.connect(217, self.btnExcluir_Click)
        self.connect(self.btnExcluir, self.btnExcluir_Click)
        if self.btnAtivarKS:
            self.connect(218, self.btnAtivarKS_Click)
            self.connect(self.btnAtivarKS, self.btnAtivarKS_Click)
        if self.rbIKS:
            self.connect(self.rbIKS, self.rbIKS_Update)
        self.connect(pyxbmct.ACTION_NAV_BACK, self.Sair)

    def set_navigation(self):
        if self.rbIKS:
            self.rbIKS.controlUp(self.lstServidores)
            self.rbIKS.controlDown(self.lstServidores)
        self.lstServidores.controlUp(self.rbIKS if self.rbIKS else self.btnCadastrar)
        self.lstServidores.controlDown(self.btnCadastrar)
        self.btnCadastrar.setNavigation(self.lstServidores, self.rbIKS if self.rbIKS else self.lstServidores, self.btnAtivarKS if self.btnAtivarKS else self.btnExcluir, self.btnEditar)
        self.btnEditar.setNavigation(self.lstServidores, self.rbIKS if self.rbIKS else self.lstServidores, self.btnCadastrar, self.btnExcluir)
        self.btnExcluir.setNavigation(self.lstServidores, self.rbIKS if self.rbIKS else self.lstServidores, self.btnEditar, self.btnAtivarKS if self.btnAtivarKS else self.btnCadastrar)
        if self.btnAtivarKS:
            self.btnAtivarKS.setNavigation(self.lstServidores, self.rbIKS if self.rbIKS else self.lstServidores, self.btnExcluir, self.btnCadastrar)
        if self.lstServidores.size():
            self.setFocus(self.lstServidores)
        else:
            self.setFocus(self.btnCadastrar)

    def load_settings(self):
        if self.rbIKS:
            self.rbIKS.setSelected(bool(self.BD.ObterSetting("ServidorIKS", True)))
            self.rbIKS_Update(Update=False)
        self.lstServidores.addItems(self.BD.ObterListReaders())

    def lstCheckUncheck(self):
        li = self.lstServidores.getSelectedItem()
        param = self.ObterParametros(li.getProperty("Path"))

        if self.Editar:
            self.Editar=False
            if len(param["Usuario"]) > 16:
                self.Aviso("Aviso", "Você não pode editar os dados do Servidor KS!", xbmcgui.NOTIFICATION_INFO)
                return
            dialog = OSCamReader(dados=param)
            dialog.doModal()

            if dialog.Gravar:
                self.BD.AtualizarReader(param["rowid"], dialog.txtURL.getText(), dialog.txtPorta.getText(), dialog.txtUsuario.getText(), dialog.txtSenha.getText(), dialog.txtDESKey.getText())
                li.setLabel("Servidor {0} (URL: {1} Usuário: {2})".format(param["rowid"], dialog.txtURL.getText(), dialog.txtUsuario.getText()))
                li.setProperty("Path", "?rowid=>{0}&URL=>{1}&Porta=>{2}&Usuario=>{3}&Senha=>{4}&DESKey=>{5}".format(param["rowid"], dialog.txtURL.getText(), dialog.txtPorta.getText(), dialog.txtUsuario.getText(), dialog.txtSenha.getText(), dialog.txtDESKey.getText()))
                self.Aviso(dialog.txtURL.getText(), "Atualizado com sucesso.", xbmcgui.NOTIFICATION_INFO)
            del dialog
        elif self.Excluir:
            self.Excluir=False
            if len(param["Usuario"]) > 16:
                dialog = xbmcgui.Dialog()
                ret = dialog.yesno("Excluir Servidor KS", "Deseja realmente excluir este servidor?")
                if not ret:
                    return
                else:
                    self.BD.ServidorKS = False
            self.BD.ExcluirReader(param["rowid"])
            self.lstServidores.removeItem(self.lstServidores.getSelectedPosition())
            self.Aviso("Servidor", "Excluido com sucesso.", xbmcgui.NOTIFICATION_INFO)
        else:
            if li.getLabel2() == "checked":
                li.setIconImage(os.path.join(_AddonPath_, "resources", "images", "Unchecked.png"))
                li.setLabel2("unchecked")
            else:
                li.setIconImage(os.path.join(_AddonPath_, "resources", "images", "Checked.png"))
                li.setLabel2("checked")
            self.BD.AtualizarReaderStatus(param["rowid"], li.getLabel2());

        _Addon_.setSetting(id="Contador", value=str(int(_Addon_.getSetting("Contador")) + 1))

    def btnCadastrar_Click(self):
        self.Editar=False
        self.Excluir=False
        dialog = OSCamReader()
        dialog.doModal()

        if dialog.Gravar:
            RowID = self.BD.InserirReader(dialog.txtURL.getText(), dialog.txtPorta.getText(), dialog.txtUsuario.getText(), dialog.txtSenha.getText(), dialog.txtDESKey.getText())
            if RowID:
                li = xbmcgui.ListItem("Servidor {0} (URL: {1} Usuário: {2})".format(RowID, dialog.txtURL.getText(), dialog.txtUsuario.getText()), 'checked', os.path.join(_AddonPath_, "resources", "images", "Checked.png"))
                li.setProperty("Path", "?rowid=>{0}&URL=>{1}&Porta=>{2}&Usuario=>{3}&Senha=>{4}&DESKey=>{5}".format(RowID, dialog.txtURL.getText(), dialog.txtPorta.getText(), dialog.txtUsuario.getText(), dialog.txtSenha.getText(), dialog.txtDESKey.getText()))
                self.lstServidores.addItem(li)
                _Addon_.setSetting(id="Contador", value=str(int(_Addon_.getSetting("Contador")) + 1))
        del dialog

    def btnEditar_Click(self):
        if not self.Editar:
            if self.lstServidores.size() > 0:
                self.Editar=True
                self.Excluir=False
                self.Aviso("Aviso", "Selecione um item na lista para editar!", xbmcgui.NOTIFICATION_INFO)
            else:
                self.Aviso("Aviso", "Não existem items na lista!", xbmcgui.NOTIFICATION_WARNING)
        else:
            self.Editar=False
            self.Aviso("Aviso", "Editar desativado!", xbmcgui.NOTIFICATION_INFO)

    def btnExcluir_Click(self):
        if not self.Excluir:
            if self.lstServidores.size() > 0:
                self.Editar=False
                self.Excluir=True
                self.Aviso("Aviso", "Selecione o item na lista para excluir!", xbmcgui.NOTIFICATION_INFO)
            else:
                self.Aviso("Aviso", "Não existem items na lista!", xbmcgui.NOTIFICATION_WARNING)
        else:
            self.Excluir=False
            self.Aviso("Aviso", "Excluir desativado!", xbmcgui.NOTIFICATION_INFO)

    def btnAtivarKS_Click(self):
        self.Editar=False
        self.Excluir=False

        if os.path.exists("/data/chandata/info/nid.xml"):
			dados=None
			with open ("/data/chandata/info/nid.xml", "r") as myfile:
				dados = myfile.read().replace('\n', '')
			self.NID = int(dados[dados.index("<nid>") + 5:dados.index("</nid>")])
			self.ONID = int(dados[dados.index("<onid>") + 6:dados.index("</onid>")])
			
        if self.BD.ServidorKS:
            self.Aviso("Aviso", "Você já possui o Servidor KS ativo na lista!", xbmcgui.NOTIFICATION_INFO)
            return
        elif not self.NID or not self.ONID:
            xbmc.executebuiltin('ActivateWindow(10626)')
            self.Aviso("Aviso", "Efetue a busca de canais antes de utilizar esta opção.", xbmcgui.NOTIFICATION_INFO)
            return
        #elif self.NID in [1, 2, 3, 6, 13] and self.ONID in [1, 2, 3, 6]: # Descomentar DEPOIS
        #    self.Aviso("Aviso", "Esta cidade já possui IKS Gratuito!", xbmcgui.NOTIFICATION_INFO)
        #    return
        self.Aviso("Aviso", "Aguarde a tela aparecer!", xbmcgui.NOTIFICATION_INFO)
        dialog = OSCamKS(nid=self.NID, onid=self.ONID)
        dialog.doModal()
        if dialog.Gravar:
            RowID = self.BD.InserirReader(dialog.URL, dialog.Porta, dialog.Usuario, dialog.Senha, "0102030405060708091011121314")
            if RowID:
                li = xbmcgui.ListItem("Servidor {0} (URL: {1} Usuário: {2})".format(RowID, dialog.URL, "KS válido até: {0}".format(dialog.DataATE)), 'checked', os.path.join(_AddonPath_, "resources", "images", "Checked.png"))
                li.setProperty("Path", "?rowid=>{0}&URL=>{1}&Porta=>{2}&Usuario=>{3}&Senha=>{4}&DESKey=>{5}".format(RowID, dialog.URL, dialog.Porta, dialog.Usuario, dialog.Senha, "0102030405060708091011121314"))
                self.lstServidores.addItem(li)
                self.BD.ServidorKS = True
                _Addon_.setSetting(id="KSValidATE", value=str(dialog.DataATE))
                _Addon_.setSetting(id="Serial", value=str(dialog.Serial))
                _Addon_.setSetting(id="Contador", value=str(int(_Addon_.getSetting("Contador")) + 1))
        del dialog

    def rbIKS_Update(self, Update=True):
        f = open("/dev/extcmd", "ab+")
        if self.rbIKS.isSelected():
            f.write("isvr:enable=1\n")
            self.rbIKS.setLabel('Servidor IKS: On')
        else:
            f.write("isvr:enable=0\n")
            self.rbIKS.setLabel('Servidor IKS: Off')
        f.close()
        if Update:
            self.BD.AtualizarSetting("ServidorIKS", self.rbIKS.isSelected())

    def AbrirConfiguracoes(self):
        xbmc.executebuiltin('Addon.OpenSettings(service.softcam.oscam)')

    def Aviso(self, Titulo, Mensagem, Icone=""):
        xbmcgui.Dialog().notification(Titulo, Mensagem, Icone)

    def ExecutarCMD(self, cmd):
        return commands.getoutput(cmd)
		
    def ObterParametros(self, path):
        param = []
        paramstring = path
        if len(paramstring) >= 2:
            params = path
            cleanedparams = params.replace('?', '')
            if (params[len(params) - 1] == '/'):
                params = params[0:len(params) - 2]
            pairsofparams = cleanedparams.split('&')
            param = {}
            for i in range(len(pairsofparams)):
                splitparams = {}
                splitparams = pairsofparams[i].split("=>")
                if (len(splitparams)) == 2:
                    param[splitparams[0]] = splitparams[1]
        
        return param

    def CopyDirectory(self, src, dest):
        try:
            shutil.copytree(src, dest)
        except shutil.Error as e:
            pass
        except OSError as e:
            pass

    def Sair(self):
        super(OSCamManager, self).close()

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")
    dialog = OSCamManager(_Addon_.getAddonInfo("name"))
    dialog.doModal()
    del dialog #You need to delete your instance when it is no longer needed
    #because underlying xbmcgui classes are not grabage-collected.
