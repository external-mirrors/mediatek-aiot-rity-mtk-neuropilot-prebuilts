
LIBDIR ?= "/usr/lib64"
SBINDIR ?= "/usr/sbin"
DATADIR ?= "/usr/share"
INCLUDEDIR ?= "/usr/include"
ETCDIR ?= "/etc"
PWD ?= ""
LIBS=/usr/lib64/*

ifndef HW_SETTINGS_INSTALL
$(warning HW_SETTINGS_INSTALL is undefined, prefer no hw settings to be installed)
HW_SETTINGS_INSTALL = 0
endif

all:

install:
	install -d $(INCLUDEDIR)
	install -d $(INCLUDEDIR)/neuron
	install -d $(INCLUDEDIR)/neuron/api
	install ${PWD}/usr/include/neuron/api/*.h $(INCLUDEDIR)/neuron/api

	install -d $(LIBDIR)
	cp -a $(PWD)/usr/lib64/*.so* $(LIBDIR)
	
	install -d $(SBINDIR)
	install $(PWD)/usr/sbin/* $(SBINDIR)

	install -d $(DATADIR)
	install -d $(DATADIR)/demo_dla
	install $(PWD)/usr/share/demo_dla/* $(DATADIR)/demo_dla
	install -d $(DATADIR)/benchmark_dla
	install $(PWD)/usr/share/benchmark_dla/* $(DATADIR)/benchmark_dla

ifeq ($(HW_SETTINGS_INSTALL), 1)
	$(info Installs hw settings to $(ETCDIR))
	install -d $(ETCDIR)
	cp $(PWD)/etc/* $(ETCDIR)
endif