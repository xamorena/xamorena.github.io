
if __name__ == '__main__':
    from website.wsgi import application
    from flask_frozen import Freezer
    freezer = Freezer(application)

    @freezer.register_generator
    def site_home():
        yield "site.site_home", {}

    @freezer.register_generator
    def site_topic():
        for topic in ['help', 'about', 'terms', 'privacy']:
            yield "site.site_topic", {'topic': topic}

    @freezer.register_generator
    def site_topic_page():
        for page in ['webrtc']:
            yield "site.site_topic_page", {'topic': 'tutorials', 'name': page}

    freezer.freeze()
