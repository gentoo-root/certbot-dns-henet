# Maintainer: Maxim Mikityanskiy <maxtram95@gmail.com>

_pkgname=certbot-dns-henet
pkgname=$_pkgname-git
pkgver=r1.bf519ca
pkgrel=1
pkgdesc="he.net DNS Authenticator plugin for Certbot"
arch=('any')
license=('MIT')
url="https://bitbucket.org/qt-max/$_pkgname"
depends=('certbot' 'python-acme' 'python-beautifulsoup4' 'python-requests'
         'python-setuptools' 'python-zope-interface')
makedepends=('git')
source=("$_pkgname::git+https://bitbucket.org/qt-max/$_pkgname.git")

pkgver() {
  cd "$srcdir/$pkgname"
  printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

build() {
  cd "$srcdir/$pkgname"
  python setup.py build
}

check() {
  cd "$srcdir/$pkgname"
  python setup.py test
}

package() {
  cd "$srcdir/$pkgname"
  python setup.py install --root="$pkgdir"
}
