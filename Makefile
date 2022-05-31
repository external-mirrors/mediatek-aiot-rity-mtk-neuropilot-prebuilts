
LIBDIR ?= "/usr/lib64"
SBINDIR ?= "/usr/sbin"
DATADIR ?= "/usr/share"
INCLUDEDIR ?= "/usr/include"
PWD ?= ""
LIBS=/usr/lib64/*

all:

install:
	install -d $(INCLUDEDIR)
	install ${PWD}/usr/include/*.h $(INCLUDEDIR)

	install -d $(LIBDIR)
	cp -a $(PWD)/usr/lib64/*.so* $(LIBDIR)
	
	install -d $(SBINDIR)
	install $(PWD)/usr/sbin/* $(SBINDIR)

	install -d $(DATADIR)
	install -d $(DATADIR)/demo_dla
	install $(PWD)/usr/share/demo_dla/* $(DATADIR)/demo_dla
	install -d $(DATADIR)/benchmark_dla
	install $(PWD)/usr/share/benchmark_dla/* $(DATADIR)/benchmark_dla
