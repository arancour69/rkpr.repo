# -*- coding: utf-8 -*-
#------------------------------------------------------------
# http://www.youtube.com/user/gsfvideos
#------------------------------------------------------------
# Licença: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Baseado no código do addon youtube
#------------------------------------------------------------

import os
import sys
import time
import plugintools
import xbmc,xbmcaddon
from addon.common.addon import Addon

addonID = 'plugin.video.BaladaSertaneja'
addon = Addon(addonID, sys.argv)
local = xbmcaddon.Addon(id=addonID)
#icon = local.getAddonInfo('icon')
icon = local.getAddonInfo('icon')
icon2 = "http://brenocds.net/wp-content/uploads/2014/09/Top-Sertanejo-2014.jpg"
icon3 = "https://yt3.ggpht.com/-AIuD4fUE--I/AAAAAAAAAAI/AAAAAAAAAAA/PoYUFnQFjpM/s900-c-k-no-mo-rj-c0xffffff/photo.jpg"
icon4 = "https://yt3.ggpht.com/-L0Evw6cY0U8/AAAAAAAAAAI/AAAAAAAAAAA/qzub6Pczbag/s900-c-k-no-mo-rj-c0xffffff/photo.jpg"
icon5 = "https://3.bp.blogspot.com/-HfP219fw5M8/VvVJIq6qKBI/AAAAAAAAI5c/doel_IpyG5ouKjPoyP_c2woQXFK-_yQfQ/s1600/Mulheres%2BDo%2BSertanejo%2B2016%2B-%2BXANDAO%2BDOWNLOAD.jpg"
icon6 = "https://i.ytimg.com/vi/NoZ7EsVoNF0/sddefault.jpg"
icon7 = "https://i.ytimg.com/vi/DtlvUQvdyoE/hqdefault.jpg"
icon8 = "http://brenocds.net/wp-content/uploads/2016/02/Sertanejo-Universit%C3%A1rio-2016-1.jpg"
icon9 = "https://i.ytimg.com/vi/9I7rTVwVlWk/maxresdefault.jpg"
icon10 = "https://www.lojadosomautomotivo.com.br/media/wysiwyg/botoesmusicas/sertanejo_modao.jpg"
icon11 = "http://jornalouvidor.com.br/public/img/uploaded_m/site_ouvidor_0-2015-09-25-05-51-00_MzYxMzY1NDg0.jpg"
icon12 = "https://i.ytimg.com/vi/by4wfrPEgQs/hqdefault.jpg"
icon13 = "http://blog.lojadosomautomotivo.com.br/wp-content/uploads/capajulhocetto.jpg"
icon14 = "https://i.ytimg.com/vi/gPxGK5wdrFA/hqdefault.jpg"
addonfolder = local.getAddonInfo('path')
resfolder = addonfolder + '/resources/'
entryurl=resfolder+"entrada.mp4"
YOUTUBE_CHANNEL_ID = "playlist/PLcsMX-TwGym5L6xT0lq-GINS1Td4lV9EZ"
YOUTUBE_CHANNEL_ID2 = "playlist/PLnHx97mX3_eQTjQzyaZGow0fddTNrE0MY"
YOUTUBE_CHANNEL_ID3 = "playlist/PLpc4Ek6CmNFUFPsnyMmNn3erZWUJU09ia"
YOUTUBE_CHANNEL_ID4 = "playlist/PLpc4Ek6CmNFVoGjvHYuZokghHHtuZZoYL"
YOUTUBE_CHANNEL_ID5 = "channel/UCMI_PyqvkI4kQhH-bau37wg"
YOUTUBE_CHANNEL_ID6 = "playlist/PLAEq5ujOZ71oMpipE1fAf5EeDYNnvjcve"
YOUTUBE_CHANNEL_ID7 = "playlist/PL6_E1Va4YJ_uvfKxixk4R7VkQDsgQQ4iK"
YOUTUBE_CHANNEL_ID8 = "playlist/PL6_E1Va4YJ_tiD7o_CkjnhTA8JVBB3szX"
YOUTUBE_CHANNEL_ID9 = "playlist/PL2xxb1HYnEobNlb3vwjhmbGBffX1VpyBz"
YOUTUBE_CHANNEL_ID10 = "playlist/PL5D23892C80A2293B"
YOUTUBE_CHANNEL_ID11 = "playlist/PL721FF7BCD77A7362"
YOUTUBE_CHANNEL_ID12 = "playlist/PLZ5j7_H_S7A0WlXmnQ8i7jJgjWKGHIj4G"
YOUTUBE_CHANNEL_ID13 = "playlist/PLDdAfEWHrSau_RwfIY6hnp_FAYIX694Eu"
# Ponto de Entrada
def run():
	# Pega Parâmetros
	params = plugintools.get_params()
	
	if params.get("action") is None:
		xbmc.Player().play(entryurl)
		
		while xbmc.Player().isPlaying():
			time.sleep(1)

		main_list(params)
	else:
		action = params.get("action")
		exec action+"(params)"

	plugintools.close_item_list()

# Menu Principal
def main_list(params):
	plugintools.log("BaladaSertaneja.main_list "+repr(params))
	
	plugintools.log("BaladaSertaneja.run")
	
	#plugintools.direct_play(str(entryurl))

plugintools.add_item(
		title = "DVDS TOP SERTANEJO",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID+"/",
		thumbnail = icon2,
		folder = True )
		
plugintools.add_item(
		title = "PORTAL SERTANEJANDO",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID2+"/",
		thumbnail = icon3,
		folder = True )

plugintools.add_item(
		title = "ESQUENTA SERTANEJO ",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID3+"/",
		thumbnail = icon4,
		folder = True )		

plugintools.add_item(
		title = "MULHERES DO SERTANEJO 2016",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID4+"/",
		thumbnail = icon5,
		folder = True )		
plugintools.add_item(
		title = "VEVO TOP 100 SERTANEJO - 2016",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID6+"/",
		thumbnail = icon7,
		folder = True )	
		
plugintools.add_item(
		title = "SERTANEJO UNIVERSITARIO",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID7+"/",
		thumbnail = icon8,
		folder = True )	
plugintools.add_item(
		title = "LANCAMENTO SERTANEJO UNIVERSITARIO",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID8+"/",
		thumbnail = icon9,
		folder = True )	
plugintools.add_item(
		title = "MODAO SERTANEJO",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID13+"/",
		thumbnail = icon14,
		folder = True )	
		
plugintools.add_item(
		title = "SERTANEJO ANTIGO",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID12+"/",
		thumbnail = icon13,
		folder = True )	
		
plugintools.add_item(
		title = "FLASH BACK SERTANEJO",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID5+"/",
		thumbnail = icon6,
		folder = True )
plugintools.add_item(
		title = "SERTANEJO APAIXONADO(ANTIGAS)",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID9+"/",
		thumbnail = icon10,
		folder = True )
plugintools.add_item(
		title = "SERTANEJO RAIZ",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID10+"/",
		thumbnail = icon11,
		folder = True )		
plugintools.add_item(
		title = "MODA DE VIOLA",
		url = "plugin://plugin.video.youtube/"+YOUTUBE_CHANNEL_ID11+"/",
		thumbnail = icon12,
		folder = True )			
run()