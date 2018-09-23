import logging
import re
import requests
import zope.interface

from bs4 import BeautifulSoup
from certbot import interfaces
from certbot.errors import PluginError
from certbot.plugins import dns_common


_logger = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """
    DNS Authenticator for he.net DNS

    This Authenticator parses the HTML pages of the he.net website and sends
    form data in order to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using he.net DNS for DNS).'

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=60)
        add(
            'credentials',
            help='Path to an INI file with the dns.he.net credentials.',
        )

    def more_info(self):
        return self.description

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'dns.he.net credentials INI file',
            {
                'username': 'dns.he.net username',
                'password': 'dns.he.net password',
            },
        )
        raise NotImplemented()

    def _perform(self, domain, validation_name, validation):
        self._client.add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._client.del_txt_record(domain, validation_name, validation)

    @property
    def _client(self):
        return _HeNetClient(
            username=self.credentials.conf('username'),
            password=self.credentials.conf('password'),
        )


class _HeNetClient:
    BASE_URL = 'https://dns.he.net/'
    ZONE_ONCLICK_REGEX = re.compile('^delete_dom')
    RECORD_ONCLICK_REGEX = re.compile("deleteRecord\\('([0-9]+)',")

    def __init__(self, username, password):
        self.session = requests.Session()

        # Set the necessary cookies (CGISESSID).
        self._get()

        # Log in.
        self._post({
            'username': username,
            'password': password,
        })

    def add_txt_record(self, domain, record_name, record_content):
        zone_id = self._find_zone_id_for_domain(domain)
        self._post({
            'account': '',
            'menu': 'edit_zone',
            'Type': 'TXT',
            'hosted_dns_zoneid': zone_id,
            'hosted_dns_recordid': '',
            'hosted_dns_editzone': '1',
            'Priority': '',
            'Name': record_name,
            'Content': record_content,
            'TTL': '300',
            'hosted_dns_editrecord': 'Submit',
        })

    def del_txt_record(self, domain, record_name, record_content):
        zone_id = self._find_zone_id_for_domain(domain)
        record_id = self._find_record_id(zone_id, record_name)
        response = self._post({
            'menu': 'edit_zone',
            'hosted_dns_zoneid': zone_id,
            'hosted_dns_recordid': record_id,
            'hosted_dns_editzone': '1',
            'hosted_dns_delrecord': '1',
            'hosted_dns_delconfirm': 'delete',
        })
        html = BeautifulSoup(response.content)
        elements = html.find_all('div', attrs={
            'id': 'dns_status',
        })
        if len(elements) == 0:
            raise PluginError('Unable to find status message (id="dns_status")')
        if len(elements) > 1:
            raise PluginError('Multiple elements have id="dns_status"')
        success = elements[0].string == 'Successfully removed record.'
        if not success:
            _logger.error(f'Failed to remove the Record with id={record_id}.')

    def _get(self, query=None):
        response = self.session.get(self.BASE_URL, params=query)
        response.raise_for_status()
        return response

    def _post(self, data):
        response = self.session.post(self.BASE_URL, data=data)
        response.raise_for_status()
        return response

    def _find_zone_id(self, zone):
        response = self._get()
        html = BeautifulSoup(response.content)
        elements = html.find_all('img', attrs={
            'alt': 'delete',
            'onclick' : self.ZONE_ONCLICK_REGEX,
            'name': zone,
        })
        if len(elements) == 0:
            raise KeyError('Unable to find Zone ID')
        if len(elements) > 1:
            raise PluginError('Multiple elements match the given Zone')
        zone_id = elements[0]['value']
        _logger.debug(f'Found Zone ID: {zone_id} (zone={zone}).')
        return zone_id

    def _find_record_id(self, zone_id, record_name):
        response = self._get({
            'hosted_dns_zoneid': zone_id,
            'menu': 'edit_zone',
            'hosted_dns_editzone': '',
        })
        html = BeautifulSoup(response.content)
        elements = html.find_all('td', attrs={
            'class': 'dns_delete',
            'onclick': re.compile(f"deleteRecord\\('[0-9]+','{record_name}'"),
        })
        if len(elements) == 0:
            raise PluginError('Unable to find TXT Record ID')
        if len(elements) > 0:
            raise PluginError('Multiple elements match the given TXT Record')
        record_id = self.RECORD_ONCLICK_REGEX.search(elements[0]['onclick']).group(1)
        _logger.debug(f'Found Record ID: {record_id} (zone={zone}, record_name={record_name}).')
        return record_id

    def _find_zone_id_for_domain(self, domain):
        domain_parts = domain.split('.')
        for i in range(len(domain_parts) - 1):
            zone = '.'.join(domain_parts[i:])
            _logger.debug(f'Trying Zone {zone}')
            try:
                zone_id = self._find_zone_id(zone)
            except KeyError:
                pass
            return zone_id
        raise PluginError('Unable to find Zone ID')
