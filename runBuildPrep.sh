#!/bin/sh
zypper ar -G http://download.buildservice.us.cray.com/dst:/master/SLE_15/dst:master.repo
zypper install -y cray-build-macros
