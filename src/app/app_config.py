from xmlrpc.client import boolean


class AppConfig:
    def __init__(self, subsite_separate_storage: boolean, content_format: str):
        self.subsite_separate_storage = subsite_separate_storage
        self.content_format = content_format