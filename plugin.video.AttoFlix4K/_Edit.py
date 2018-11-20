import xbmcaddon
import base64

base= "=wWb0hmLl52Tf5WafxGbB9Fcf12LzV2YyV3bzVmcvMnbvRGZh9SbvNmLvJXdnV2clRXazJWZ35SMvRHdh9yL6MHc0RHa"
tam=len(base)
basedem=base[::-1]
MainBase= base64.b64decode(basedem)

addon = xbmcaddon.Addon('plugin.video.AttoFlix4K')