Certbot authenticator for Hurricane Electric free DNS service (dns.he.net)
==========================================================================

This plugin allows [certbot](https://github.com/certbot/certbot) to verify domains hosted at [dns.he.net](https://dns.he.net/) automatically using [DNS-01](https://docs.certifytheweb.com/docs/dns-validation.html) validation. During the validation process, it adds a TXT record for the domain and removes it automatically after the validation passes.

Usage
-----

Store the dns.he.net credentials (replace USERNAME and PASSWORD by your actual credentials):

    install -m 700 -d /etc/letsencrypt/dns-credentials
    install -m 600 -T /dev/null /etc/letsencrypt/dns-credentials/henet
    cat > /etc/letsencrypt/dns-credentials/henet << "EOF"
    certbot_dns_henet:dns_henet_username=USERNAME
    certbot_dns_henet:dns_henet_password=PASSWORD
    EOF

Generate a new wildcard certificate:

    certbot certonly \
        --authenticator certbot-dns-henet:dns-henet \
        --certbot-dns-henet:dns-henet-credentials /etc/letsencrypt/dns-credentials/henet \
        --domain '*.example.com' --domain 'example.com' \
        --must-staple

Renew the certificates:

    certbot renew

Frequently Asked Questions
--------------------------

### Why do I need to provide the password to my he.net account?

At the moment, dns.he.net doesn't have an API for creating and removing TXT records. The only way to do it is to use web interface, and this script imitates user actions on the website. Don't worry, the script doesn't steal your credentials. It only sends the password to the dns.he.net website. You can check it by yourself: the script is less than 200 lines of code.

### Does your script parse HTML? Will it break suddenly if the website design changes?

Yes. Unfortunately, there is no better way yet, as dns.he.net doesn't have the necessary API. Luckily, the design of dns.he.net hasn't been changed for quite a long time, so there is hope that this script will work for some period of time. Anyway, it's better than nothing.

### How do I install this plugin?

If you are on Archlinux, use the PKGBUILD shipped in this repository. Check out [this Arch Wiki page](https://wiki.archlinux.org/index.php/makepkg#Usage) for the details about installing from PKGBUILD.

For other distributions and operating systems, you should be able to install this plugin using setup.py, just as any Python module. Using the package manager is preferred: many package managers offer some simple mechanism for creating packages based on setup.py. However, if you wish to install it manually (or if you need some reference installations commands for creating a package), run the following commands:

    python setup.py build
    python setup.py test
    python setup.py install
