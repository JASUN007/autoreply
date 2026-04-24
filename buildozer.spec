[app]
title = 微信自动回复
package.name = wxreply
package.domain = com.wx.reply
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,xlsx
version = 1.0

requirements = python3,kivy,pandas,openpyxl
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BIND_ACCESSIBILITY_SERVICE,FOREGROUND_SERVICE
android.api = 33
android.ndk = 25b
android.archs = arm64-v8a
orientation = portrait
