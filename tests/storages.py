from django.core.files.storage import FileSystemStorage


class LocalDataLakeStorage(FileSystemStorage):

    def __init__(self):
        super().__init__(location='/tmp')