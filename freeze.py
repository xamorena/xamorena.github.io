
if __name__ == '__main__':
    from website.wsgi import application
    from flask_frozen import Freezer
    freezer = Freezer(application)
    freezer.freeze()
