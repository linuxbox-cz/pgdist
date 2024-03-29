Name: pgdist
Summary: Distribute PotgreSQL functions, tables, etc...
Version: VERSION
Release: %{dist}.01
License: proprietary
Group: Applications/Databases

Source:         pgdist-%{version}.tar

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Requires: python3-psycopg2

%define __python python3

%description

%prep

%setup

%build


%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/share/pgdist/install
mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/share/man/man1
mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/libexec/pgdist/
mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/libexec/pgdist/dev
mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/libexec/pgdist/mng
mkdir -p -m 755 ${RPM_BUILD_ROOT}/usr/bin/
mkdir -p -m 755 ${RPM_BUILD_ROOT}/etc/

install -m 755 src/pgdist.py ${RPM_BUILD_ROOT}/usr/libexec/pgdist/
install -m 655 src/dev/* ${RPM_BUILD_ROOT}/usr/libexec/pgdist/dev/
install -m 655 src/mng/* ${RPM_BUILD_ROOT}/usr/libexec/pgdist/mng/
install -m 655 etc/* ${RPM_BUILD_ROOT}/etc/
install -m 644 doc/man/pgdist.1 ${RPM_BUILD_ROOT}/usr/share/man/man1/
gzip -f ${RPM_BUILD_ROOT}/usr/share/man/man1/pgdist.1

ln -s /usr/libexec/pgdist/pgdist.py ${RPM_BUILD_ROOT}/usr/bin/pgdist

%files
%attr(644,root,root)                      /usr/share/man/man1/pgdist.1.gz
%attr(755,root,root)                      /usr/bin/pgdist
%attr(755,root,root)                      /usr/libexec/pgdist/*.p*
%attr(644,root,root)                      /usr/libexec/pgdist/*/*.p*
%dir %attr(0755,root,root)                /usr/share/pgdist/install
%attr(644,root,root) %config(noreplace)   /etc/pgdist.conf

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%changelog
* Tue Mar 19 2024 Marian Krucina <marian.krucina@linuxbox.cz> - 1.2403.0.0 - %{dist}.01
- version 1.2403.0.0

* Thu Feb 01 2024 Marian Krucina <marian.krucina@linuxbox.cz> - 1.2401.0.2 - %{dist}.01
- version 1.2401.0.2

* Wed Jan 31 2024 Marian Krucina <marian.krucina@linuxbox.cz> - 1.2401.0.1 - %{dist}.01
- version 1.2401.0.1

* Wed Jan 24 2024 Marian Krucina <marian.krucina@linuxbox.cz> - 1.2401.0.0 - %{dist}.01
- version 1.2401.0.0
