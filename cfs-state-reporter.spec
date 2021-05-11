# Copyright 2020-2021 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# (MIT License)
Name: cfs-state-reporter
License: MIT
Summary: A system service which reports the configuration level of a given node
Group: System/Management
Version: %(cat .version)
Release: %(echo ${BUILD_METADATA})
Source: %{name}-%{version}.tar.bz2
Vendor: Cray Inc.
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}
Requires: python3-base
Requires: python3-requests
Requires: systemd
Requires: cfs-trust
Requires: cray-auth-utils

%define _systemdsvcdir /usr/lib/systemd/system

%description
Provides a systemd service and associated library that reports the
configuration status of a running system during system startup.

%{!?python3_sitelib: %define python3_sitelib %(/usr/bin/python3 -c
"from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%prep
%setup -q

%build
/usr/bin/python3 setup.py build

%install
rm -rf $RPM_BUILD_ROOT
/usr/bin/python3 setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}%{_systemdsvcdir}
cp etc/cfs-state-reporter.service $RPM_BUILD_ROOT/%{_systemdsvcdir}/cfs-state-reporter.service
chmod +x $RPM_BUILD_ROOT/%{python3_sitelib}/cfs/status_reporter/__main__.py

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{python3_sitelib}/*
%dir %{_systemdsvcdir}
%{_systemdsvcdir}/cfs-state-reporter.service

%pre
%if 0%{?suse_version}
%service_add_pre cfs-state-reporter.service
%endif

%post
ln -f /usr/bin/spire-agent /usr/bin/cfs-state-reporter-spire-agent
%if 0%{?suse_version}
%service_add_post cfs-state-reporter.service
%else
%systemd_post cfs-state-reporter.service
%endif

%preun
%if 0%{?suse_version}
%service_del_preun cfs-state-reporter.service
%else
%systemd_preun cfs-state-reporter.service
%endif

%postun
if [ $1 -eq 0 ];then
  rm -f /usr/bin/cfs-state-reporter-spire-agent
fi
%if 0%{?suse_version}
%service_del_postun cfs-state-reporter.service
%else
%systemd_postun_with_restart cfs-state-reporter.service
%endif
