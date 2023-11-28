import os


def set_conf():
    name = "settings.py"
    folder = os.path.dirname(__file__)
    gen = os.walk(folder)
    dirpath, dirnames, filenames = next(gen)
    for subdir in dirnames:
        if subdir not in ['accounts', 'carts', 'category', 'orders', 'store'] and name in os.listdir(subdir):
            folder = subdir
            break
    
    with open(os.path.join(folder, name), 'a') as conf:
        conf.write(addition)

    os.rename(os.path.join('greatkart', 'static'), os.path.join(folder, 'static'))
    os.replace(os.path.join('greatkart', 'urls.py'), os.path.join(folder, 'urls.py'))

    if os.path.exists(__file__):
        os.remove(__file__)






addition = """
INSTALLED_APPS += [
    'category.apps.CategoryConfig', 
    'accounts.apps.AccountsConfig', 
    'store.apps.StoreConfig', 
    'carts.apps.CartsConfig', 
    'orders.apps.OrdersConfig', 
]

TEMPLATES[0]['DIRS'].append('templates')

TEMPLATES[0]['OPTIONS']['context_processors'].extend(['category.context_processors.menu_links',  'carts.context_processors.counter'])

AUTH_USER_MODEL = 'accounts.Account'

STATIC_ROOT = BASE_DIR / 'static'

STATICFILES_DIRS = [
    Path(__file__).resolve().parent.name + '/static', 
]

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.ERROR: "danger", }

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "tmp/app-messages"
"""




if __name__ == "__main__":
    set_conf()
