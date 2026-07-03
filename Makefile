
LIBDIR ?= "/usr/lib64"
SBINDIR ?= "/usr/sbin"
DATADIR ?= "/usr/share"
INCLUDEDIR ?= "/usr/include"
MDW_VER ?= "android13"
NP_VER ?= "6"
PWD ?= ""
LIBS=/usr/lib64/*


all:

install:
	install -d $(INCLUDEDIR)
	install -d $(INCLUDEDIR)/neuron
	install -d $(INCLUDEDIR)/neuron/api
	install ${PWD}/neuron/${NP_VER}/usr/include/neuron/api/*.h $(INCLUDEDIR)/neuron/api

	install -d $(LIBDIR)
	cp -a $(PWD)/neuron/${NP_VER}/usr/lib64/*.so* $(LIBDIR)
	cp -a $(PWD)/mdw/${MDW_VER}/usr/lib64/*.so* $(LIBDIR)

	# Install llmsdk libraries for NP_VER 8
	if [ "${NP_VER}" = "8" ] && [ -d "$(PWD)/llmsdk/8/usr/lib64" ]; then \
		cp -a $(PWD)/llmsdk/8/usr/lib64/*.so* $(LIBDIR); \
	fi

	install -d $(SBINDIR)
	install $(PWD)/neuron/${NP_VER}/usr/sbin/* $(SBINDIR)
	install $(PWD)/mdw/${MDW_VER}/usr/sbin/* $(SBINDIR)

	# Install llmsdk tools for NP_VER 8
	if [ "${NP_VER}" = "8" ] && [ -d "$(PWD)/llmsdk/8/usr/sbin" ]; then \
		install $(PWD)/llmsdk/8/usr/sbin/llm_cmdline_tool $(SBINDIR); \
		install $(PWD)/llmsdk/8/usr/sbin/mllm_llava $(SBINDIR); \
	fi

	install -d $(DATADIR)
	install -d $(DATADIR)/demo_dla
	install $(PWD)/sample/${NP_VER}/usr/share/demo_dla/* $(DATADIR)/demo_dla
	install -d $(DATADIR)/benchmark_dla
	install $(PWD)/sample/${NP_VER}/usr/share/benchmark_dla/* $(DATADIR)/benchmark_dla
