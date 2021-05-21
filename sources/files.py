from enum import Enum
import configparser

_SSSD_CONF = "/etc/sssd/sssd.conf"
_DEFAULT_LOG_PREFIX = "/var/log/sssd/sssd_"
_DEFAULT_NSS_LOG = _DEFAULT_LOG_PREFIX + "nss.log"
_DEFAULT_PAM_LOG = _DEFAULT_LOG_PREFIX + "pam.log"


class Reader:
    class Component(Enum):
        NSS = 1   # NSS Responder
        PAM = 2   # PAM Responder
        BE = 3    # Backend

    def __init__(self):
        self.log_files = []
        self.domains = self.read_domain_config()

    def __iter__(self):
        for files in self.log_files:
            try:
                with open(files) as file:
                    for line in file:
                        yield line
            except FileNotFoundError as err:
                print("Could not find domain log file, skipping")
                print(err)
                continue

    def read_domain_config(self):
        config = configparser.ConfigParser()
        sssd_conf = config.read(_SSSD_CONF)
        if sssd_conf:
            domains = config.get('sssd', 'domains')
            return [x.strip() for x in domains.split(',')]
        else:
            print("Unable to read: " + _SSSD_CONF)
            return []

    def set_component(self, component):
        self.log_files = []
        if component == self.Component.NSS:
            self.log_files.append(_DEFAULT_NSS_LOG)
        elif component == self.Component.PAM:
            self.log_files.append(_DEFAULT_PAM_LOG)
        elif component == self.Component.BE:
            if not self.domains:
                raise IOError
            ## error: No domains found?
            for dom in self.domains:
                be_log = _DEFAULT_LOG_PREFIX + dom + ".log"
                self.log_files.append(be_log)
