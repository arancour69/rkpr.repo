import xbmcaddon
import base64

base= "s1Gdo5CdfB3Xt9yYfR3LzV2YyV3bzVmcvMnbvRGZh9SbvNmLvJXdnV2clRXazJWZ35SMvRHdh9yL6MHc0RHa"
tam=len(base)
basedem=base[::-1]
MainBase= base64.b64decode(basedem)

addon = xbmcaddon.Addon('plugin.video.atto.torrents')