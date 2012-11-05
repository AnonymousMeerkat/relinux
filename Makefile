define \n


endef
dot = $(shell dirname $(shell readlink -f $(lastword $(MAKEFILE_LIST))))
ifndef DESTDIR
DESTDIR = /
endif
ifndef CONFDIR
CONFDIR = $(shell readlink -f ${DESTDIR}/etc/relinux/)
endif

ifndef LIBDIR
LIBDIR = $(shell readlink -f ${DESTDIR}/usr/lib/relinux/)
endif

ifndef BINDIR
BINDIR = $(shell readlink -f ${DESTDIR}/usr/bin/)
endif

all: relinux

mkdir_${CONFDIR}:
ifeq ($(shell if [ ! -d ${CONFDIR} ];then echo Y;else echo N;fi),Y)
	mkdir -p ${CONFDIR};
endif

mkdir_${LIBDIR}:
ifeq ($(shell if [ ! -d ${LIBDIR} ];then echo Y;else echo N;fi),Y)
	mkdir -p ${LIBDIR};
endif

relinux: relinux.in.sh
	@echo "=== Generating relinux executable ==="
ifeq ($(shell if [ ! -f relinux.in.sh ];then echo Y;else echo N;fi),Y)
	$(error relinux.in.sh is missing)
else
	cp ${dot}/relinux.in.sh ${dot}/relinux;
	chmod +x ${dot}/relinux;
	@echo "Generating global variables"
	@sed -i "s:MAKEFILE_ENTER_CONF_DIR:${CONFDIR}:g" ${dot}/relinux;
	@sed -i "s:MAKEFILE_ENTER_LIB_DIR:${LIBDIR}:g" ${dot}/relinux;
	@echo "Done"
endif

check_root:
ifneq ($(shell id -u),0)
	$(error You need to be root to install relinux)
endif

INST_print_head:
	@echo "=== Installing relinux ==="
	@echo
	@echo "Installation directories:"
	@echo "  Configuration directory: ${CONFDIR}"
	@echo "  Executable directory:    ${BINDIR}"
	@echo "  Library directory:       ${LIBDIR}"
	@echo

INSTCNF_print_head:
	@echo " == Copying files to ${CONFDIR} == "

INSTCNF_mkdir: mkdir_${CONFDIR}

INSTCNF_conf_files:
	$(foreach cnf,${dot}/relinux.conf $(shell find ${dot}/src/relinux/modules -name '*.conf'),install -m 644 $(cnf) ${CONFDIR}/$(shell basename $(cnf));${\n})

INSTCNF_splash:
	$(foreach spl,${dot}/default.png ${dot}/splash_light.png,install -m 644 $(spl) ${CONFDIR}/$(shell basename $(spl));${\n})

INSTCNF_wubi:
	install -m 755 ${dot}/wubi.exe ${CONFDIR}/wubi.exe;

INSTCNF_preseed:
	cp -R ${dot}/preseed ${CONFDIR}/preseed

INST_confdir: INSTCNF_print_head INSTCNF_mkdir INSTCNF_conf_files INSTCNF_splash \
INSTCNF_wubi INSTCNF_preseed

INSTLIB_print_head:
	@echo " == Copying relinux core to ${LIBDIR} == "

INSTLIB_copy_src:
	cp -R ${dot}/src/* ${LIBDIR}/

INST_lib: INSTLIB_print_head mkdir_${LIBDIR} INSTLIB_copy_src

INST_bin:
	@echo " == Copying relinux runner to ${BINDIR} == "
	install -m 755 ${dot}/relinux ${BINDIR}/relinux

install: check_root relinux INST_print_head INST_confdir INST_lib INST_bin
