import os
import shutil
from contextlib import closing
from ftplib import FTP
from urllib import request

from fbcrawler.settings.settings_maneger import project_settings


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class FTPManager(Borg):
    """
    Manage main functions related with Ftb:
    connection, save functions, delete, close, load, files to save data
    """
    def __init__(self):
        super().__init__()
        try:
            if not hasattr(self, '_ftp'):
                self._ftp = self.__connect()
            self._ftp.voidcmd("NOOP")
        except:
            self._ftp = self.__connect()

    @staticmethod
    def __connect():
        ftp = FTP()
        ftp.set_debuglevel(1)
        ftp.connect(project_settings.FTP_SERVER_ADDRESS, project_settings.FTP_SERVER_PORT)
        ftp.login(project_settings.FTP_SERVER_USERNAME, '')
        return ftp

    def list_files(self, ftp_directory: str):
        self._ftp.cwd(ftp_directory)
        files = self._ftp.nlst()
        self._ftp.cwd('/')
        return files

    def save(self, ftp_directory: str, file_path: str):
        fp = open(file_path, 'rb')
        self._ftp.cwd(ftp_directory)
        self._ftp.storbinary('STOR %s' % os.path.basename(file_path), fp, 1024)
        fp.close()
        self._ftp.cwd('/')

    @staticmethod
    def load(ftp_directory: str, ftp_file_name: str, target_file_path: str):
        ftp_file_path = f'ftp://{project_settings.FTP_SERVER_USERNAME}:@{project_settings.FTP_SERVER_ADDRESS}/{ftp_directory}/{ftp_file_name}'
        with closing(request.urlopen(ftp_file_path)) as r:
            with open(target_file_path, 'wb') as f:
                shutil.copyfileobj(r, f)

    def delete(self, ftp_directory: str, ftp_file_name: str):
        self._ftp.cwd(ftp_directory)
        self._ftp.delete(ftp_file_name)
        self._ftp.cwd('/')

    def close(self):
        self._ftp.close()
