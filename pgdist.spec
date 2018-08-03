Name: pgdist
Summary: Distribute PotgreSQL functions, tables, etc...
Version: VERSION
Release: %{dist}.01
License: proprietary
Group: Applications/Databases

Source:         pgdist-%{version}.tar

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Requires: python-psycopg2
Requires: python-argparse


%description

%prep

%setup

%build


%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/share/pgdist/install
mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/libexec/pgdist/
mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/libexec/pgdist/dev
mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/libexec/pgdist/mng
mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/bin/

install -m 755 src/pgdist.py ${RPM_BUILD_ROOT}/usr/libexec/pgdist/
install -m 655 src/dev/* ${RPM_BUILD_ROOT}/usr/libexec/pgdist/dev/
install -m 655 src/mng/* ${RPM_BUILD_ROOT}/usr/libexec/pgdist/mng/

ln -s /usr/libexec/pgdist/pgdist.py ${RPM_BUILD_ROOT}/usr/bin/pgdist

%files
%attr(755,root,root)                      /usr/bin/pgdist
%attr(755,root,root)                      /usr/libexec/pgdist/*.p*
%attr(644,root,root)                      /usr/libexec/pgdist/*/*.p*
%dir %attr(0755,root,root)                /usr/share/pgdist/install

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%changelog
* Mon Jul 23 2018 Marian Krucina <marian.krucina@linuxbox.cz> - 1.0.0
- first rpm
