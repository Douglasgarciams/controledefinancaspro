[app]

title = ControledefinançasPRO

package.name = financeiro
package.domain = com.flet

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,txt

source.exclude_dirs = .git,.github,.venv,venv,__pycache__,bin,.buildozer,backups

version = 1.0.0

requirements = python3,kivy==2.3.1,kivymd==1.2.0,plyer,pyjnius

orientation = portrait

fullscreen = 0

# Ative somente quando estes arquivos existirem:
# icon.filename = assets/icon.png
# presplash.filename = assets/splash.png

android.api = 36

android.minapi = 24

android.ndk_api = 24

android.ndk = 27c

android.permissions = INTERNET,POST_NOTIFICATIONS

android.archs = arm64-v8a

android.accept_sdk_license = True

android.debug_artifact = apk

android.release_artifact = aab

android.private_storage = True

android.allow_backup = False

p4a.branch = develop

[buildozer]

log_level = 2

warn_on_root = 0