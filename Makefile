
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

# The llmsdk runners dlopen libneuronusdk_runtime.mtk.so by its unversioned
# name, so nothing in the ELF records which Neuron API they were built against
# and the loader cannot catch a mismatch. llmsdk/8/MANIFEST.yaml is the only
# record; this compares it against the headers actually shipped.
check-abi:
	@hdr=$$(git log -1 --format=%h -- neuron/8/usr/include); \
	rec=$$(sed -n 's/^ *neuron_api: *\([0-9a-f]\{7,\}\).*/\1/p' llmsdk/8/MANIFEST.yaml); \
	if [ -z "$$rec" ]; then \
		echo "check-abi: llmsdk/8/MANIFEST.yaml records no neuron_api commit"; \
		exit 1; \
	elif git merge-base --is-ancestor $$hdr $$rec; then \
		echo "check-abi: llmsdk/8 is current with the neuron/8 headers ($$hdr)"; \
	else \
		echo "check-abi: neuron/8 headers are at $$hdr, llmsdk/8 was built against $$rec"; \
		echo "check-abi: rebuild the llmsdk runners and update llmsdk/8/MANIFEST.yaml"; \
		exit 1; \
	fi

.PHONY: all install check-abi
