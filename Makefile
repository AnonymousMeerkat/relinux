define \n


endef
dot := $(shell dirname $(shell readlink -f $(lastword $(MAKEFILE_LIST))))
CONFDIR := ${DESTDIR}/etc/relinux/
LIBDIR := ${DESTDIR}/usr/lib/relinux/
BINDIR := ${DESTDIR}/usr/bin/
SHAREDIR := ${DESTDIR}/usr/share/
APPDIR := ${SHAREDIR}/applications
CC := gcc
BITS := $(shell dpkg-architecture -qDEB_BUILD_ARCH_BITS | tr '\n' ' ' | sed 's: ::g')


all: csrc/isatty${BITS}.so src/relinux/modules/osweaver/isatty${BITS}.so relinux

CLEAN_print_head:
	@echo === Cleaning ===

CLEAN_clean:
	$(foreach i,$(shell find ${dot} -type d | grep -v __pycache__ | grep -v /.git),cd ${i}; rm -rf *.pyc __pycache__;${\n})
	rm -f ${dot}/csrc/isatty*.so ${dot}/src/relinux/modules/osweaver/isatty*.so

clean: CLEAN_print_head CLEAN_clean

DISTCLEAN_print_head:
	@echo === Distcleaning ===

DISTCLEAN_clean:
	rm -f ${dot}/relinux
ifeq ($(shell if [ -d ${dot}/debian/relinux ];then echo Y;fi),Y)
	rm -rf ${dot}/debian/relinux
endif

distclean: DISTCLEAN_print_head CLEAN_clean DISTCLEAN_clean

check:
	@echo === Checking relinux executable ===
ifeq ($(shell ls ${dot}/relinux &>/dev/null && echo Y),)
	@echo "Relinux executable does not exist" >&2;
	@exit 1;
endif
ifeq ($(shell grep -e "MAKEFILE_ENTER_CONF_DIR" -e "MAKEFILE_ENTER_LIB_DIR" ${dot}/relinux &>/dev/null; echo $?),0)
	@echo "Relinux executable has not been properly generated" >&2;
	@exit 1;
endif
	@echo Done. No errors detected.
	@echo === Checking isatty.so ===
ifeq ($(shell ls src/relinux/modules/osweaver/isatty${BITS}.so &>/dev/null && echo Y),)
	@echo "src/relinux/modules/osweaver/isatty${BITS}.so does not exist" >&2;
	@exit 1;
endif
ifneq ($(shell ls src/relinux/modules/osweaver/isatty*.so 2>/dev/null | grep -v isatty${BITS}.so),)
	@echo "These files should not exist:";
	@ls src/relinux/modules/osweaver/isatty*.so 2>/dev/null | grep -v isatty${BITS}.so |\
awk '{print "  "$$0}';
	@exit 1;
endif
	@echo Done. No errors detected.

mkdir_${CONFDIR}:
ifeq ($(shell if [ ! -d ${CONFDIR} ];then echo Y;else echo N;fi),Y)
	mkdir -p ${CONFDIR};
endif

mkdir_${LIBDIR}:
ifeq ($(shell if [ ! -d ${LIBDIR} ];then echo Y;else echo N;fi),Y)
	mkdir -p ${LIBDIR};
endif

mkdir_${BINDIR}:
ifeq ($(shell if [ ! -d ${BINDIR} ];then echo Y;else echo N;fi),Y)
	mkdir -p ${BINDIR};
endif

mkdir_${SHAREDIR}:
ifeq ($(shell if [ ! -d ${SHAREDIR} ];then echo Y;else echo N;fi),Y)
	mkdir -p ${SHAREDIR};
endif

mkdir_${APPDIR}:
ifeq ($(shell if [ ! -d ${APPDIR} ];then echo Y;else echo N;fi),Y)
	mkdir -p ${APPDIR};
endif

csrc/isatty${BITS}.so: csrc/isatty.c 
	@echo "=== Generating isatty override library ==="
	${CC} -shared -fPIC -o csrc/isatty${BITS}.so csrc/isatty.c

src/relinux/modules/osweaver/isatty${BITS}.so: csrc/isatty${BITS}.so
	cp csrc/isatty${BITS}.so src/relinux/modules/osweaver/isatty${BITS}.so

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

INSTCNF_isolinux_cfg:
	install -m 755 ${dot}/isolinux.cfg ${CONFDIR}/isolinux.cfg

INST_confdir: INSTCNF_print_head INSTCNF_mkdir INSTCNF_conf_files INSTCNF_splash \
INSTCNF_wubi INSTCNF_preseed INSTCNF_isolinux_cfg

INSTLIB_print_head:
	@echo " == Copying relinux core to ${LIBDIR} == "

INSTLIB_copy_src:
	cp -R ${dot}/src/* ${LIBDIR}/

INST_lib: INSTLIB_print_head mkdir_${LIBDIR} INSTLIB_copy_src

INSTBIN_print_head:
	@echo " == Copying relinux runner to ${BINDIR} == "

INSTBIN_relinux:
	install -m 755 ${dot}/relinux ${BINDIR}/relinux

INST_bin: INSTBIN_print_head mkdir_${BINDIR} INSTBIN_relinux

INSTSHARE_print_head:
	@echo " == Copying shared files to ${SHAREDIR} == "

INSTSHARE_desktop:
	install -m 644 ${dot}/relinux.desktop ${APPDIR}/relinux.desktop

INST_share: INSTSHARE_print_head mkdir_${APPDIR} INSTSHARE_desktop

install: check_root relinux INST_print_head INST_confdir INST_lib INST_share INST_bin

.PHONY: all check_root clean distclean install
