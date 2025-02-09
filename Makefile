#
# MIT License
#
# (C) Copyright 2019-2025 Hewlett Packard Enterprise Development LP
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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# If you wish to perform a local build, you will need to clone or copy the contents of the
# cms-meta-tools repo to ./cms_meta_tools

NAME ?= cfs-state-reporter
GENERIC_RPM_SOURCE_TAR ?= cfs-state-reporter-source.tar
RPM_OUTPUT_RELDIR ?= dist/rpmbuild
PIP_INSTALL_ARGS ?= --trusted-host arti.hpc.amslabs.hpecorp.net --trusted-host artifactory.algol60.net --index-url https://arti.hpc.amslabs.hpecorp.net:443/artifactory/api/pypi/pypi-remote/simple --extra-index-url http://artifactory.algol60.net/artifactory/csm-python-modules/simple --extra-index-url https://pypi.org/simple --no-cache -c constraints.txt
PY_VERSION ?= 3.6
RPM_ARCH ?= x86_64

SPEC_FILE ?= ${NAME}.spec

PYTHON_BIN := python$(PY_VERSION)
PY_BIN ?= /usr/bin/$(PYTHON_BIN)

PYLINT_VENV ?= pylint-$(PY_VERSION)
PYLINT_VENV_PYBIN ?= $(PYLINT_VENV)/bin/python3

runbuildprep:
		./cms_meta_tools/scripts/runBuildPrep.sh

lint:
		./cms_meta_tools/scripts/runLint.sh

pre_clean:
		rm -rf dist

python_rpms_prepare:
		tar \
			--exclude '.git*' \
			--exclude './.tmp.*' \
			--exclude ./build \
			--exclude ./cms_meta_tools \
			--exclude ./dist \
            --exclude '$(RPM_OUTPUT_RELDIR)' \
			--exclude '$(GENERIC_RPM_SOURCE_TAR)' \
			--exclude './pylint-*' \
			-cvf '$(GENERIC_RPM_SOURCE_TAR)' .

python_rpm_build:
		PY_VERSION='$(PY_VERSION)' \
		PIP_INSTALL_ARGS='$(PIP_INSTALL_ARGS)' \
		./cms_meta_tools/resources/build_rpm_v2.sh \
			--arch '$(RPM_ARCH)' \
			'$(RPM_OUTPUT_RELDIR)' '$(GENERIC_RPM_SOURCE_TAR)' '$(SPEC_FILE)'

pymod_build:
		$(PY_BIN) --version
		$(PY_BIN) -m pip install --upgrade --user $(PIP_INSTALL_ARGS) pip build setuptools wheel
		$(PY_BIN) -m pip list --format freeze
		$(PY_BIN) -m build --wheel
		cp ./dist/cfs*.whl .

pymod_pylint_setup:
		$(PY_BIN) --version
		$(PY_BIN) -m venv $(PYLINT_VENV)
		$(PYLINT_VENV_PYBIN) -m pip install --upgrade $(PIP_INSTALL_ARGS) pip
		$(PYLINT_VENV_PYBIN) -m pip install --disable-pip-version-check $(PIP_INSTALL_ARGS) pylint cfs*.whl
		$(PYLINT_VENV_PYBIN) -m pip list --format freeze

pymod_pylint_errors:
		$(PYLINT_VENV_PYBIN) -m pylint --errors-only cfs

pymod_pylint_full:
		$(PYLINT_VENV_PYBIN) -m pylint --fail-under 6.5 cfs
