# Release Note

Releases from `scarthgap-v1.0.0` onward are versioned and tagged. See
[VERSIONING.md](VERSIONING.md) for the increment rules and the tag format; the
dated entries below predate tagging.

Per-binary provenance lives in the per-component `MANIFEST.yaml` files, not in
the tables here. For any release,
`git diff <prev-tag>..<tag> -- '*/MANIFEST.yaml'` is the authoritative answer
to "what was this built from".

## [Unreleased]

Bump: MINOR - `neuron/8`'s adapter/runtime and `mvpu/25`'s nn/cv op libs gain
ONNX GridSample support on MVPU (Genio Pro 5100 / MT8894 only); no existing
interface removed, existing op mappings unchanged.

`neuron/8/usr/lib64/libneuronusdk_{adapter,runtime}.mtk.so.8.2.16` and
`mvpu/25/usr/lib64/libmvpuop25_mtk_{cv,nn}.so` rebuilt from
neuropilot_aiv/neuron (NP8_0 @83f5cfad + the GridSample adapter/MVPU-backend
patches 0004-0006 in aiot_int/bsp/neuron-pilot-dev's libneuron recipe) and
MVPU_v2_SW/mvpu_op (MVPU_SDK_Release_SW4.x @95eee2f8b + the GridSampler2d
patches in neuron-pilot-dev's mvpu-algo recipe). Adds adapter support for mapping ONNX GridSample to MVPU's
GridSampler2d op, and fixes a general MVPU-backend bug where a failed
GenKernels() returned a successful compile/execute with an unwritten output.
Both additive/defensive: no existing op mapping or SoC besides MT8894 (the
only one with MVPU) is affected.

Verified on Genio Pro 5100 EVK: GridSample reaches MVPU for the
fp16/bilinear/zero-padding path (cos 0.994-0.99999 across an 18-shape sweep,
IGEV-RT end-to-end 47.7 ms cosine 1.00000, no regression on softmax/tanh);
unsupported combinations (nearest, non-zero border, reflection) now report
unsupported at compile instead of running with garbage output. Full sweep and
acceptance commands: `gp5100_npu/mvpu_info/gridsample-5100-candidate-1004/
README.md` (v6) and `gp5100_npu/mvpu_info/neuron-build-dev-notes.md`.

Known residual, not fixed by this drop: the GridSampler2d kernel binaries
sample fp16 absolute pixel coordinates, so precision drops for H/W >= 200
(cos 0.997 @ 200px, 0.994 @ 300px). Needs an fp32-grid kernel binary.

See `neuron/8/MANIFEST.yaml` (`deviations.gridsample-mvpu`) and
`mvpu/25/MANIFEST.yaml` (`gridsample_op_lib`) for full provenance.

**Fixed:** `llmsdk/8/usr/sbin/llm_cmdline_tool` hit a random `std::bad_alloc`
(or a global OOM kill that also dropped adb) at model init in about 1 run in 4,
seen with Qwen3-1.7B on Genio 720. An uninitialized flag sent plain LLMs into
the Qwen3-VL mRoPE table builder, which allocated with a negative length.
All seven LLM/VLM/ASR runners rebuilt from nda/gai-cmdline-tool NP8_0
@40aa356: 0 failures in 100 runs, output identical, performance unchanged;
VLM and ASR runners pass regression.

**Fixed (untagged regression from d2f5bf8):** the first GridSample drop of
`libneuronusdk_{adapter,runtime}.mtk.so.8.2.16` was built with `-march=armv9-a`
and carried ~49k / ~25k SVE instructions. `neuron/8` ships to every np8 SoC,
and Genio 720 (MT8391: Cortex-A78 + A55) has no SVE, so the runtime died with
SIGILL at init (`mllm_llava` qwen3vl, exit 132). Rebuilt from the same source
with `-march=armv8-a+crc`: 0 SVE instructions; SONAME, DT_NEEDED and the
exported symbol set are unchanged from both d2f5bf8 and bfd81e6. No source
change, so GridSample behaviour on MT8894 is the same as above.

`sample/8/mt8894` added: the demo and benchmark DLAs compiled for MT8894
(Genio Pro 5100). NP8 stopped being one APU configuration when MT8894 landed -
mt8391/mt8366 are 1 x MDLA 5.3 with a 256 KB L1, MT8894 is 4 x MDLA 5.5 with a
4 MB TCM plus 2 x MVPU 2.5 and EDPA 2.0 - and a DLA is tiled for the core count
and L1 size it was compiled against, so the flat `sample/8` set leaves three of
MT8894's four cores idle. It does still load: MT8894's nhw accepts MDLA
5.0..5.5. The refusal is asymmetric - a 5.5 DLA on G720 is the direction that
fails - so do not rely on a load error to catch a mis-targeted DLA here.

This is an **overlay**, not a second copy: the `.tflite`, label and script
assets under `sample/8/usr/share` are target-independent and stay where they
are (~100 MB), and consumers lay this directory over them. `Makefile` gains
`DLA_OVERLAY` for that, matching `NP_DLA_OVERLAY` in `neuropilot-bin.bb`.

Compiled in-house with `ncc-tflite --arch=mdla5.5,mvpu2.5 --l1-size-kb=4096
--num-mdla=4` (host 8.2.19), not taken from a vendor drop. Explicit flags rather
than `--platform-config mt6991`: MT8894 is mt6991-derived but its TCM is 4 MB
and its DMA engine is EDPA 2.0, and no SDK on hand has an mt8894 platform
config. EDPA is left out because NP8 has no `edpa2.0` target at all. See
`sample/8/mt8894/MANIFEST.yaml` for the detail, including why host 8.2.19
against an 8.2.16 runtime is safe.

Needs the nhw on `mtk-apusys-firmware`'s `mt8894` branch to be in the image:
without it the Neuron runtime cannot enumerate the APU at all, so none of these
load. Verified together on genio-pro-5100-evk - all five models dump their IO
table, mobilenet_v1 classifies grace_hopper correctly, and the four benchmark
models run at 0.78 to 3.23 ms/inference.

## [scarthgap-v1.0.0] - 2026-09-09

Bump: MAJOR - yearly baseline. First tagged release. No binary changes: this
adds the version contract in VERSIONING.md and back-fills a `MANIFEST.yaml`
for every component from the entries below and from the commit history.

Back-filling the manifests turned up two things worth stating plainly.

**No upstream SHA in this repo has been verified against its upstream repo.**
Every value in the manifests is transcribed from a Release.md table or a commit
message, so each one carries `verified: no` and a `claimed_in:` citation.
Alongside it, `repo_commit` records the commit of *this* repo that last changed
those files, which is checkable and is what the manifests key on.

**The tables in the entries below were carried forward by copy-paste**, so a
row is not evidence that the binary was built from the SHA next to it:

* `neuron/6` ships binaries from four separate drops - the runtime and adapter
  libraries from `5aa46ad`, `ncc-tflite` and `neuronrt` from `1615e4e`,
  `libneuron_platform.vpu.so` and `runtime_api_sample` from `d53a85e`, the
  headers from `620aed6` - yet each entry lists all of them under that drop's
  SHA. The 2024/11/19 and 2024/12/23 tables also list `libneuronusdk_*.6.3.3`
  under two different SHAs while the files did not change between them, and
  the tools appear at `633cf504` in 2024/12/23 and at the older `553bb891` in
  2025/4/30.
* `mdw/android13` has not changed since `d53a85e` (2024-11-06), but its rows
  reappear in all three later entries.

Provenance gaps, recorded as `commit: unknown` rather than guessed:

* `neuron/8` - **no commit in its history records an upstream SHA, and it has
  never had a Release.md entry.** Everything currently shipped there comes from
  `36bd7f8`; `81faafd` was superseded by it. `3b031cab1f` is not neuron/8's
  provenance - that SHA is recorded in `7574b42`, which touched `mdw/android15`
  and no file under `neuron/8`.
* `mdw/android13` - no table has ever listed the five test tools in
  `usr/sbin`; every entry covers the libraries only.
* `llmsdk/8` - yaml-cpp, sentencepiece, re2 and hf-tokenizers arrived with the
  vendor drop with no source recorded.
* `llmsdk/8` `built_against.neuron_api` is derived, not recorded: nothing
  states which Neuron header revision the runners were compiled against, so it
  is set to where `neuron/8/usr/include` stood when they were built. Until a
  drop records it, `make check-abi` detects drift from that baseline rather
  than confirming the baseline.

Also found while inventorying: `llmsdk/8/usr/lib64/libhf-tokenizer.so`
(1.2 MB, singular) is referenced by nothing - it is absent from every runner's
`DT_NEEDED` and no runner contains its name as a dlopen string. The nine
runners link the 66 KB `libhf-tokenizers.so` instead. Left in place pending a
decision.

The changes between the 2025/4/30 and 2026/8/26 entries went unrecorded here.
Summary, with provenance now in the manifests and in `1615e4e..1acf5b7`:

* neuron/8 - NP8 support added
  - `libneuronusdk_runtime.mtk.so.8.2.16`,
    `libneuronusdk_adapter.mtk.so.8.2.16`, `neuronrt`, `runtime_api_sample`
  - DLB (Dynamic Load Balancing) support enabled
  - rebuilt with clang 18 after clang 20 core-dumped under the Neuron Stable
    Delegate
  - warning logs suppressed when NEON or GPU is disabled
  - `dlopen` library names corrected in the example applications

* llmsdk/8 - LLM/VLM/ASR runners added, NP8 only
  - `llm_cmdline_tool`, `asr_cmdline_tool`, `run_moonshine_asr.sh`
  - `mllm_llava`, `mllm_llava_medusa`, `mllm_llava_spec_dec`, `mllm_omni`
  - `main_whisper`, `main_qwen3_asr`, `moonshine_asr`
  - all seven binaries built from `nda/gai-cmdline-tool` NP8_0 (`00e2704`),
    stripped, reporting time-to-first-token in the `[Latency]` block
  - whisper output-buffer corruption fixed; three consecutive runs now give
    identical tokens and a correct transcript

* sample - NP8 example and benchmark files added, benchmark flow redesigned
  for NP8 platforms

* Makefile - install paths made specific to the NP version

MT8894 enablement (`mdw/mt8894`, `mvpu/25`) is in the 2026/8/26 entry below.

## 2026/8/26

MT8894 (Genio Pro 5100) enablement: APUSYS middleware and MVPU 2.5a userspace.

`mdw/mt8894` is a separate middleware build from `mdw/android15` -- MDLA 5.5 plus
EDMA, the unit tests, EDPA and CBFC:
`MDLA_VERISON=5.5 ENABLE_EDMA=1 ENABLE_UT=1 ENABLE_EDPAUT=1 ENABLE_CBFCUT=1`.

`mvpu/25` is MVPU 2.5a, taken from the mt8678 prebuilt RPMs -- MT8894 is mt8678
silicon, so the aarch64 binaries are used unmodified except where noted below.
`libmcve.so` is deliberately not published: it is the only library that pulls in
libdmabufheap/libsync/libprop, and nothing in the MVPU or MDLA stack links it.

|            Binary            |                  Commit                  |         Repo/Branch         |  What's Changed  |
| :--------------------------: | :--------------------------------------: | :-------------------------: | :--------------: |
| mdw/mt8894/*                 | f69f5c260b93c5e4f1120b34914dc86b04329300 | yocto/src/multimedia/apusys<br>spm-mp-scarthgap.mp1 | new |
| mvpu/25 libmvpu_runtime.so   | ade6526006ae4886ac233eafd04c81743cd35db1 | mvpu_runtime<br>spm-mp-scarthgap.mp1-1 | v |
| mvpu/25 libmvpu_pattern*.so  | 1e9d8737b149925c899e2c9225d45520c93acfb0 | mvpu-si/mt8678/mvpu_runtime<br>spm-mp-scarthgap.mp1 | new |
| mvpu/25 rt_*, mvpu_tester    | 1e9d8737b149925c899e2c9225d45520c93acfb0 | mvpu-si/mt8678/mvpu_runtime<br>spm-mp-scarthgap.mp1 | new |
| mvpu/25 libmvpu_engine*.so   | 60c4cd44cb05544acb9012cb3fe9393ab5f4d8d1 | mvpu-si/mt8678/mvpu<br>spm-mp-scarthgap.mp1 | v |
| mvpu/25 libmvpu_config*.so   | 60c4cd44cb05544acb9012cb3fe9393ab5f4d8d1 | mvpu-si/mt8678/mvpu<br>spm-mp-scarthgap.mp1 | new |
| mvpu/25 libmvpuop25_*.so     | c2f05a4707e229b628ebc009a9fbad291f3400de | mvpu-si/mt8678/mvpu-algo<br>spm-mp-scarthgap.mp1 | new |
| mvpu/25 libmvpu_clc_*.so     | d3242d26cb38c0aa934a2ca1d5e8698b71d0f132 | mvpu-si/mt8678/cl-toolchain<br>spm-mp-scarthgap.mp1 | new |

Two deviations from the vendor RPMs, both intentional:

1. `libmvpu_runtime.so` is **not** the RPM binary. The RPM's copy has a
   lost-wakeup race in the 2.5 runtime: `rt_simplecl` hangs in `clFinish()` or
   returns -501 in roughly 1 run in 9 (measured 21 failures in 200). This one is
   built from mvpu_runtime `ade6526` plus a fix for that race and the double
   dispatch behind it, and measured 0 failures in 200. Replace it with the vendor
   binary once an RPM carries the fix; the fix is also posted to the ALPS
   mvpu_runtime repo. Note it is built with clang 20.1.1 where the vendor uses
   18.1.2.
2. `libmvpu_runtime.so` and `libmvpu_engine.so` have had `libglog.so.1` and
   `libion.so` removed from their `DT_NEEDED`. Neither library contributes a
   single undefined symbol, and neither exists on rity, so the alternative was
   shipping stubs. Redo this with `patchelf --remove-needed` if either binary is
   refreshed.
3. `libatrace.so` is **not** a vendor binary. `libmvpu_engine.so` is an Android
   build and keeps a `DT_NEEDED` on it, calling `atrace_init`/`atrace_begin`/
   `atrace_end` from its session paths. The calls sit behind an MVPU config bit
   that is off by default, but the library is linked `BIND_NOW`, so the loader
   resolves every relocation up front and `patchelf --remove-needed` turns into
   a load failure rather than a no-op -- which is why this one needs a real
   library where libglog and libion did not. `src/atrace.c` implements the three
   entry points on the ftrace `trace_marker`, so the events still land in a
   `trace-cmd`/`perfetto` capture. Built with the rity aarch64 toolchain:

       $CC -O2 -fPIC -shared -g0 -Wl,-s -Wl,-soname,libatrace.so \
           -o usr/lib64/libatrace.so src/atrace.c

   Drop both the library and `src/` once `libmvpu_engine.so` is published from a
   non-Android build with the trace calls compiled out; nothing else in the
   image wants the ATrace ABI.

## 2025/4/30

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev

- Branch: NP6_0

- Commit:   553bb891aa37017dbbef35ab676304845fa459e8

  |               Binary               |                  Commit                  |         Repo/Branch         |  What's Changed  |
  | :--------------------------------: | :--------------------------------------: | :-------------------------: | :--------------: |
  |        libapu_mdw.so.2.0.0         | b2e99f004964a5b44e215a98549bdc69938b9375 |    aiv-mp-kirkstone.mp1     |                  |
  |     libapu_mdw_batch.so.2.0.0      | b2e99f004964a5b44e215a98549bdc69938b9375 |    aiv-mp-kirkstone.mp1     |                  |
  |      libapusys_edma.so.3.0.0       | b2e99f004964a5b44e215a98549bdc69938b9375 |    aiv-mp-kirkstone.mp1     |                  |
  |        libmdla_ut.so.2.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |                  |
  |        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |                  |
  |          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |       alps-mp-t0.mp5        |                  |
  | libneuronusdk_runtime.mtk.so.6.3.3 | 553bb891aa37017dbbef35ab676304845fa459e8 |           NP6_0             |                  |
  | libneuronusdk_adapter.mtk.so.6.3.3 | 553bb891aa37017dbbef35ab676304845fa459e8 |           NP6_0             |                  |
  |     libneuron_platform.vpu.so      | 553bb891aa37017dbbef35ab676304845fa459e8 |           NP6_0             |                  |
  |             ncc-tflite             | 553bb891aa37017dbbef35ab676304845fa459e8 |           NP6_0             |         v        |
  |              neuronrt              | 553bb891aa37017dbbef35ab676304845fa459e8 |           NP6_0             |         v        |
  |         runtime_api_sample         | 553bb891aa37017dbbef35ab676304845fa459e8 |           NP6_0             |         v        |


Changes:

* ncc-tflite/neruonrt/runtime_api_sample
  - Update neuron tools for supporting dynamic nhw loading with environment variable

## 2024/12/23

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev

- Branch: NP6_0

- Commit:   633cf50420c26df6ef09e2cc5514efe386bd82c9

  |               Binary               |                  Commit                  |         Repo/Branch         | Module |
  | :--------------------------------: | :--------------------------------------: | :-------------------------: | :----: |
  |        libapu_mdw.so.2.0.0         | b2e99f004964a5b44e215a98549bdc69938b9375 |    aiv-mp-kirkstone.mp1     |        |
  |     libapu_mdw_batch.so.2.0.0      | b2e99f004964a5b44e215a98549bdc69938b9375 |    aiv-mp-kirkstone.mp1     |        |
  |      libapusys_edma.so.3.0.0       | b2e99f004964a5b44e215a98549bdc69938b9375 |    aiv-mp-kirkstone.mp1     |        |
  |        libmdla_ut.so.2.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |       alps-mp-t0.mp5        |        |
  | libneuronusdk_runtime.mtk.so.6.3.3 | 553bb891aa37017dbbef35ab676304845fa459e8 |           NP6_0             |        |
  | libneuronusdk_adapter.mtk.so.6.3.3 | 553bb891aa37017dbbef35ab676304845fa459e8 |           NP6_0             |        |
  |     libneuron_platform.vpu.so      | 553bb891aa37017dbbef35ab676304845fa459e8 |           NP6_0             |        |
  |             ncc-tflite             | 633cf50420c26df6ef09e2cc5514efe386bd82c9 |           NP6_0             |        |
  |              neuronrt              | 633cf50420c26df6ef09e2cc5514efe386bd82c9 |           NP6_0             |        |
  |         runtime_api_sample         | 633cf50420c26df6ef09e2cc5514efe386bd82c9 |           NP6_0             |        |


Changes:

* libneuron
  - Hash bump for including follwing change in source repo
    - [AUTO00182656] To support diverse platform in a single image using environment variable
    - [MDLA/3.x] Fix Softmax with channel = 2 and beta != 1.0 accuracy issue

## 2024/11/19

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev

- Branch: NP6_0

- Commit:   633cf50420c26df6ef09e2cc5514efe386bd82c9

  |               Binary               |                  Commit                  |         Repo/Branch         | Module |
  | :--------------------------------: | :--------------------------------------: | :-------------------------: | :----: |
  |        libapu_mdw.so.2.0.0         | b2e99f004964a5b44e215a98549bdc69938b9375 |    aiv-mp-kirkstone.mp1     |        |
  |     libapu_mdw_batch.so.2.0.0      | b2e99f004964a5b44e215a98549bdc69938b9375 |    aiv-mp-kirkstone.mp1     |        |
  |      libapusys_edma.so.3.0.0       | b2e99f004964a5b44e215a98549bdc69938b9375 |    aiv-mp-kirkstone.mp1     |        |
  |        libmdla_ut.so.2.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |       alps-mp-t0.mp5        |        |
  | libneuronusdk_runtime.mtk.so.6.3.3 | 633cf50420c26df6ef09e2cc5514efe386bd82c9 |           NP6_0             |        |
  | libneuronusdk_adapter.mtk.so.6.3.3 | 633cf50420c26df6ef09e2cc5514efe386bd82c9 |           NP6_0             |        |
  |     libneuron_platform.vpu.so      | 633cf50420c26df6ef09e2cc5514efe386bd82c9 |           NP6_0             |        |
  |             ncc-tflite             | 633cf50420c26df6ef09e2cc5514efe386bd82c9 |           NP6_0             |        |
  |              neuronrt              | 633cf50420c26df6ef09e2cc5514efe386bd82c9 |           NP6_0             |        |
  |         runtime_api_sample         | 633cf50420c26df6ef09e2cc5514efe386bd82c9 |           NP6_0             |        |


Changes:

* libneuron
  - Hash bump for follwing change in source repo
    - Bug fixing for [AUTO00302004] Error while trying to run a yolov8
  - Add support for dynamic nhw loading

* midware
  - Hash bump for follwing change in source repo
    - apusys: fix coverity 10948845
    - Change the source branch from aiv-mp-hardknott.mp1 to to aiv-mp-kirkstone.mp1

## 2024/5/20

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev

- Branch: NP6_0

- Commit:   fc1df999d16107994636c0452cd20bfab46cc8a5

  |               Binary               |                  Commit                  |         Repo/Branch         | Module |
  | :--------------------------------: | :--------------------------------------: | :-------------------------: | :----: |
  |        libapu_mdw.so.2.0.0         | 88f5f1215381087737b262747ff2901260c0fef4 |    aiv-mp-hardknott.mp1     |        |
  |     libapu_mdw_batch.so.2.0.0      | 88f5f1215381087737b262747ff2901260c0fef4 |    aiv-mp-hardknott.mp1     |        |
  |      libapusys_edma.so.3.0.0       | 88f5f1215381087737b262747ff2901260c0fef4 |    aiv-mp-hardknott.mp1     |        |
  |        libmdla_ut.so.2.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |       alps-mp-t0.mp5        |        |
  | libneuronusdk_runtime.mtk.so.6.3.3 | fc1df999d16107994636c0452cd20bfab46cc8a5 |           NP6_0             |        | 
  | libneuronusdk_adapter.mtk.so.6.3.3 | fc1df999d16107994636c0452cd20bfab46cc8a5 |           NP6_0             |        | 
  |     libneuron_platform.vpu.so      | fc1df999d16107994636c0452cd20bfab46cc8a5 |           NP6_0             |        | 
  |             ncc-tflite             | fc1df999d16107994636c0452cd20bfab46cc8a5 |           NP6_0             |        |
  |              neuronrt              | fc1df999d16107994636c0452cd20bfab46cc8a5 |           NP6_0             |        |
  |         runtime_api_sample         | fc1df999d16107994636c0452cd20bfab46cc8a5 |           NP6_0             |        |


Changes:
- Hash bump for libneuron
- Update the binary for ncc-tflite which is dependent on libneuron

## 2024/5/6

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev

- Branch: NP6_0

- Commit:   78a4c98b2d4e64d5869cf101961ffee6bd78530f

  |               Binary               |                  Commit                  |         Repo/Branch         | Module |
  | :--------------------------------: | :--------------------------------------: | :-------------------------: | :----: |
  |        libapu_mdw.so.2.0.0         | 88f5f1215381087737b262747ff2901260c0fef4 |    aiv-mp-hardknott.mp1     |        |
  |     libapu_mdw_batch.so.2.0.0      | 88f5f1215381087737b262747ff2901260c0fef4 |    aiv-mp-hardknott.mp1     |        |
  |      libapusys_edma.so.3.0.0       | 88f5f1215381087737b262747ff2901260c0fef4 |    aiv-mp-hardknott.mp1     |        |
  |        libmdla_ut.so.2.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |       alps-mp-t0.mp5        |        |
  | libneuronusdk_runtime.mtk.so.6.3.3 | 5306284d66bd2bb9577e642043f0bfa52a79a76a |           NP6_0             |        | 
  | libneuronusdk_adapter.mtk.so.6.3.3 | 5306284d66bd2bb9577e642043f0bfa52a79a76a |           NP6_0             |        | 
  |     libneuron_platform.vpu.so      | 5306284d66bd2bb9577e642043f0bfa52a79a76a |           NP6_0             |        | 
  |             ncc-tflite             | 78a4c98b2d4e64d5869cf101961ffee6bd78530f |           NP6_0             |        |
  |              neuronrt              | 5306284d66bd2bb9577e642043f0bfa52a79a76a |           NP6_0             |        |
  |         runtime_api_sample         | 5306284d66bd2bb9577e642043f0bfa52a79a76a |           NP6_0             |        |


Changes:
- Remove unnessary dependency on ncurses/libtinfo
- Hash bump for ncc-tflite

## 2023/12/5


Commit: ae952e0a666eb83a53af68b476c873abfaba14fe

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev

- Branch: NP6_0

- Commit:   dff37081fa477fd861f859e782c4b12bcd71ab66

  |               Binary               |                  Commit                  |         Repo/Branch         | Module |
  | :--------------------------------: | :--------------------------------------: | :-------------------------: | :----: |
  |        libapu_mdw.so.2.0.0         | 88f5f1215381087737b262747ff2901260c0fef4 |    aiv-mp-hardknott.mp1     |        |
  |     libapu_mdw_batch.so.2.0.0      | 88f5f1215381087737b262747ff2901260c0fef4 |    aiv-mp-hardknott.mp1     |        |
  |      libapusys_edma.so.3.0.0       | 88f5f1215381087737b262747ff2901260c0fef4 |    aiv-mp-hardknott.mp1     |        |
  |        libmdla_ut.so.2.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |       alps-mp-t0.mp5        |        |
  | libneuronusdk_runtime.mtk.so.6.3.3 | dff37081fa477fd861f859e782c4b12bcd71ab66 |           NP6_0             |        | 
  | libneuronusdk_adapter.mtk.so.6.3.3 | dff37081fa477fd861f859e782c4b12bcd71ab66 |           NP6_0             |        | 
  |     libneuron_platform.vpu.so      | dff37081fa477fd861f859e782c4b12bcd71ab66 |           NP6_0             |        | 
  |             ncc-tflite             | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |           NP6_0             |        |
  |              neuronrt              | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |           NP6_0             |        |
  |         runtime_api_sample         | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |           NP6_0             |        |


Changes:
- Turn off libcmdl warning log if GPU is disabled
- Update midware library

## 2023/12/1

Commit: 687d27eedb3007c18dc9dfad4a985c98079501e8

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev

- Branch: NP6_0

- Commit:   87f52c77428c5c0bb85c38aba09ce581f515a41e

  |               Binary               |                  Commit                  |         Repo/Branch         | Module |
  | :--------------------------------: | :--------------------------------------: | :-------------------------: | :----: |
  |        libapu_mdw.so.2.0.0         | 57b1d899ada6731c1cc839305ef9dad7acfc3bde |    aiv-mp-hardknott.mp1     |        |
  |     libapu_mdw_batch.so.2.0.0      | 57b1d899ada6731c1cc839305ef9dad7acfc3bde |    aiv-mp-hardknott.mp1     |        |
  |      libapusys_edma.so.3.0.0       | 57b1d899ada6731c1cc839305ef9dad7acfc3bde |    aiv-mp-hardknott.mp1     |        |
  |        libmdla_ut.so.2.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |       alps-mp-t0.mp1        |        |
  |          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |       alps-mp-t0.mp5        |        |
  | libneuronusdk_runtime.mtk.so.6.3.3 | 3522125c1d0722c9eb5cce1f5ed48e435761b8b8 | neuropilot_aiv/neuron/NP6_0 |        | 
  | libneuronusdk_adapter.mtk.so.6.3.3 | 3522125c1d0722c9eb5cce1f5ed48e435761b8b8 | neuropilot_aiv/neuron/NP6_0 |        | 
  |     libneuron_platform.vpu.so      | 3522125c1d0722c9eb5cce1f5ed48e435761b8b8 | neuropilot_aiv/neuron/NP6_0 |        | 
  |             ncc-tflite             | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |           NP6_0             |        |
  |              neuronrt              | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |           NP6_0             |        |
  |         runtime_api_sample         | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |           NP6_0             |        |


Changes:
- Fix VPU XRP 3.0 ImportBuffer security issue
- neuron: Fix coverity
- neuron NP 6.0.3 official release


## 2023/08/10

Commit:   3b73fca6a790cebedd298253ce97496257361f7b

Changes:

- Fix syntax error in label_image.py

## 2023/07/31

Commit:   f6409400b13be0971d682592600b5048a2847575

Changes:

- Update demo script to remove hardcoded python script path
- Update benchmark script to remove hardcoded python script path
- Update benchmark script to add error handling for missing input file

## 2023/07/26

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev

- Branch: NP6_0

- Commit:   0a2ec1cdd662d3e980cd7488ba9aa094283e1d9b

  |               Binary               |                  Commit                  |        Branch        | Module |
  | :--------------------------------: | :--------------------------------------: | :------------------: | :----: |
  |        libapu_mdw.so.2.0.0         | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
  |     libapu_mdw_batch.so.2.0.0      | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
  |      libapusys_edma.so.3.0.0       | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
  |        libmdla_ut.so.2.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |    alps-mp-t0.mp1    |        |
  |        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |    alps-mp-t0.mp1    |        |
  |          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |    alps-mp-t0.mp5    |        |
  | libneuronusdk_runtime.mtk.so.6.2.3 | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |
  | libneuronusdk_adapter.mtk.so.6.2.3 | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |
  |     libneuron_platform.vpu.so      | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |
  |             ncc-tflite             | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |
  |              neuronrt              | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |
  |         runtime_api_sample         | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |

  Changes:

  -  Remove misleading warning messages and print detailed information for easier debugging
     - Don't try to load libcmdl library if GPU isn't enabled
     - Print detailed error message when CONV2D check filter fail

## 2023/07/21

Commit:  a3a3a147b562b96785ebdaccadbfb2da619ff451

- Binaries source:

  - Repo: aiot_int/bsp/neuron-pilot-dev
  - Branch: NP6_0
  - Commit:  31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b

|               Binary               |                  Commit                  |        Branch        | Module |
| :--------------------------------: | :--------------------------------------: | :------------------: | :----: |
|        libapu_mdw.so.2.0.0         | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
|     libapu_mdw_batch.so.2.0.0      | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
|      libapusys_edma.so.3.0.0       | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
|        libmdla_ut.so.2.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |    alps-mp-t0.mp1    |        |
|        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |    alps-mp-t0.mp1    |        |
|          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |    alps-mp-t0.mp5    |        |
| libneuronusdk_runtime.mtk.so.6.2.3 | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |
| libneuronusdk_adapter.mtk.so.6.2.3 | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |
|     libneuron_platform.vpu.so      | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |
|             ncc-tflite             | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |
|              neuronrt              | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |
|         runtime_api_sample         | 31b04ec356c3d2ca8319d74b29cc5d2965bf7e1b |        NP6_0         |        |

Changes:

-  Refine error message to print detailed information for easier debugging
  - Refine error message when checking bias quantization
  * Print detailed error message when CONV_2D check failed
  * Print detailed error message when PRelu layer verify failed

## 2023/02/08

Commit:  44fe607495911c4617252d9da39b9d221788aeb1 

Changes: 

- Update demo and benchmark scripts

## 2023/02/02

Commit: e8af43794f1b19630ec32594c486be2a666b3d65

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev
- Branch: NP6_0
- Commit: bd10bcea7fbe2ef99d285900b22e2f1ea07d6c2d

|               Binary               |                  Commit                  |        Branch        | Module |
| :--------------------------------: | :--------------------------------------: | :------------------: | :----: |
|        libapu_mdw.so.2.0.0         | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
|     libapu_mdw_batch.so.2.0.0      | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
|      libapusys_edma.so.3.0.0       | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
|        libmdla_ut.so.2.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |    alps-mp-t0.mp1    |        |
|        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |    alps-mp-t0.mp1    |        |
|          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |    alps-mp-t0.mp5    |        |
| libneuronusdk_runtime.mtk.so.6.2.3 | 38e3d4fe1fd50ec198b3b9be39bf43493c5caf77 |        NP6_0         |        |
| libneuronusdk_adapter.mtk.so.6.2.3 | 38e3d4fe1fd50ec198b3b9be39bf43493c5caf77 |        NP6_0         |        |
|     libneuron_platform.vpu.so      | 38e3d4fe1fd50ec198b3b9be39bf43493c5caf77 |        NP6_0         |        |
|             ncc-tflite             | e7d2ffcfff0e17a3e81fc4c6a3020f7328e1a92c |        NP6_0         |        |
|              neuronrt              | 38e3d4fe1fd50ec198b3b9be39bf43493c5caf77 |        NP6_0         |        |
|         runtime_api_sample         | e7d2ffcfff0e17a3e81fc4c6a3020f7328e1a92c |        NP6_0         |        |

Changes:

- Support universal neuron: 

  For mt8195 and mt8188, use one single user space library. In user space, there are 2 parts: neuron and apusys midware. 

  Before, mt8195 and mt8188 apusys kernel driver are ported from different android branches (aka different neuropilot version):

  - mt8195: neuropilot 5, android R.
  - mt8188: neuropilot 6, android T.

  So they used different neuron libraries and apusys midware libraries on mt8195 and mt8188.

  Now we upgrade mt8195 apusys kernel driver from android R to android T, makes mt8195 and mt8188 use the same kernel driver, so they can use the same neuron and apusys midware user space library.

  Below are changes:

  - Remove mt8195/mt8188 folder
  - Create mdw folder to place apusys midware user space libraries
  - Create neuron folder to place neuron user space libraries
  - Create sample folder to place demo and benchmark scripts

  ```
  ├── LICENSE
  ├── Makefile
  ├── mdw
  │   └── android13
  │       ├── README.md
  │       └── usr
  │           ├── lib64
  │           │   ├── libapu_mdw_batch.so -> libapu_mdw_batch.so.2.0.0
  │           │   ├── libapu_mdw_batch.so.2 -> libapu_mdw_batch.so.2.0.0
  │           │   ├── libapu_mdw_batch.so.2.0.0
  │           │   ├── libapu_mdw.so -> libapu_mdw.so.2.0.0
  │           │   ├── libapu_mdw.so.2 -> libapu_mdw.so.2.0.0
  │           │   ├── libapu_mdw.so.2.0.0
  │           │   ├── libapusys_edma.so -> libapusys_edma.so.3.0.0
  │           │   ├── libapusys_edma.so.3 -> libapusys_edma.so.3.0.0
  │           │   ├── libapusys_edma.so.3.0.0
  │           │   ├── libmdla_ut.so.2 -> libmdla_ut.so.2.0.0
  │           │   ├── libmdla_ut.so.2.0.0
  │           │   ├── libmdla_ut.so.3 -> libmdla_ut.so.3.0.0
  │           │   ├── libmdla_ut.so.3.0.0
  │           │   ├── libvpu5.so -> libvpu5.so.5.0.0
  │           │   ├── libvpu5.so.5 -> libvpu5.so.5.0.0
  │           │   └── libvpu5.so.5.0.0
  │           └── sbin
  │               ├── apu_mdw_test
  │               ├── edma_test
  │               ├── mdla2_player
  │               ├── mdla3_player
  │               └── vpu5_test
  ├── neuron
  │   └── 6
  │       └── usr
  │           ├── include
  │           │   └── neuron
  │           │       └── api
  │           │           ├── DLAMuxerFence.h
  │           │           ├── DLAMuxer.h
  │           │           ├── Fence.h
  │           │           ├── Misc.h
  │           │           ├── NeuronAdapter.h
  │           │           ├── RuntimeAPI.h
  │           │           ├── RuntimeV2.h
  │           │           └── Types.h
  │           ├── lib64
  │           │   ├── libneuron_platform.vpu.so
  │           │   ├── libneuronusdk_adapter.mtk.so -> libneuronusdk_adapter.mtk.so.6
  │           │   ├── libneuronusdk_adapter.mtk.so.6 -> libneuronusdk_adapter.mtk.so.6.2.3
  │           │   ├── libneuronusdk_adapter.mtk.so.6.2.3
  │           │   ├── libneuronusdk_runtime.mtk.so -> libneuronusdk_runtime.mtk.so.6
  │           │   ├── libneuronusdk_runtime.mtk.so.6 -> libneuronusdk_runtime.mtk.so.6.2.3
  │           │   └── libneuronusdk_runtime.mtk.so.6.2.3
  │           └── sbin
  │               ├── ncc-tflite
  │               ├── neuronrt
  │               └── runtime_api_sample
  └── sample
      └── usr
          └── share
              ├── benchmark_dla
              │   ├── benchmark.py
              │   ├── inception_v3_quant.tflite
              │   ├── mobilenet_v2_1.0_224_quant.tflite
              │   ├── ResNet50V2_224_1.0_quant.tflite
              │   └── ssd_mobilenet_v1_coco_quantized.tflite
              └── demo_dla
                  ├── grace_hopper.jpg
                  ├── imagenet_slim_labels.txt
                  ├── label_image.py
                  └── mobilenet_v1_1.0_224_quant.tflite
  
  ```



## 2023/01/05

Commit: 961c5876e11c0c0674a8415fc068cedae9ec20fe

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev
- Branch: mt8195
- Commit: 18dbf3228259a4fae8b1412236d7e69e4f2905c7

Changes:

- Upgrade neuron/ncc-tflite from 5.1.1 to 5.8.3

|           Binary           |                  Commit                  |           Branch           | Module |
| :------------------------: | :--------------------------------------: | :------------------------: | :----: |
|    libapu_mdw.so.2.0.0     | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libapu_mdw_batch.so.2.0.0  | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
|      libedma.so.3.0.0      | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
|    libmdla_ut.s0.2.0.0     | 82ffbd65a4c209684bfae76df8a1823a2fb27b2d | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_runtime.so.5.8.3 | 1dad43edb9824eb4ff04e667f2cdbceff75c646b |           NP5_0            |        |
|      libvpu5.so.5.0.0      | 53f8320d404cb66e55dedc5709b095b3bbb93fed | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_platform.vpu.so  | 1dad43edb9824eb4ff04e667f2cdbceff75c646b |           NP5_0            |        |
|         ncc-tflite         | 21ff854ca7b1ed6754739cb2c2d551468db76e62 |           NP5_0            |        |
|          neuronrt          | 1dad43edb9824eb4ff04e667f2cdbceff75c646b |           NP5_0            |        |

## 2022/12/5

commit: f929d5176893d1d94cba2ebae3a5854710c2cf75 

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev
- Branch: mt8188

- Commit: f571d8bb5baa44ec8c9dca725c6c970f13c050df


Changes:

- Initial binaries

|               Binary               |                  Commit                  |        Branch        | Module |
| :--------------------------------: | :--------------------------------------: | :------------------: | :----: |
|        libapu_mdw.so.2.0.0         | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
|     libapu_mdw_batch.so.2.0.0      | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
|      libapusys_edma.so.3.0.0       | 57b1d899ada6731c1cc839305ef9dad7acfc3bde | aiv-mp-hardknott.mp1 |        |
|        libmdla_ut.so.3.0.0         | 78a707e2cda54500af8db2b2f1b479be9fc7ca6e |    alps-mp-t0.mp1    |        |
|          libvpu5.so.5.0.0          | 4ad18f265d97cf44ed3badc491cdceb891da9cbf |    alps-mp-t0.mp5    |        |
| libneuronusdk_runtime.mtk.so.6.2.3 | 38e3d4fe1fd50ec198b3b9be39bf43493c5caf77 |        NP6_0         |        |
| libneuronusdk_adapter.mtk.so.6.2.3 | 38e3d4fe1fd50ec198b3b9be39bf43493c5caf77 |        NP6_0         |        |
|     libneuron_platform.vpu.so      | 38e3d4fe1fd50ec198b3b9be39bf43493c5caf77 |        NP6_0         |        |
|             ncc-tflite             | e7d2ffcfff0e17a3e81fc4c6a3020f7328e1a92c |        NP6_0         |        |
|              neuronrt              | 38e3d4fe1fd50ec198b3b9be39bf43493c5caf77 |        NP6_0         |        |

## 2022/11/24

Commit: 0e9448659b0f42bd4f3bb7bddb57c1ec4f781696

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev
- Branch: mt8195

- Commit: 6fb38d868a5f26cc59bd46a06c57d9ab2cfa3237


Changes:

- Update benchmark.py, enable profile option

  - Add profile option: `--profile` to print profile information after model inference.

  - Example

    - ```
      $ python3 benchmark.py --stress --profile --count 2
      2022-04-28 23:58:55,812 [INFO] ssd_mobilenet_v1_coco_quantized.tflite, mdla2.0, inference start
      INFO: ----------------------------------------------------------------------------------------------------
      INFO:                                  Runtime Status (LEVEL 1) - Summary
      INFO: ----------------------------------------------------------------------------------------------------
      INFO:   Total Execution Time: 46.73193359375 ms over 2 times inference.
      INFO:  ====Time===, ==Ratio==, =ExeTimes=, =Time/Inf.=, ===Description===
      INFO:       10.218,     21.9%,          1, -----------, Read Compiled Network
      INFO:        1.106,      2.4%,          1, -----------, Extract Compiled Network
      INFO:        3.830,      8.2%,          2, -----------, Map Device Memory
      INFO:        3.310,      7.1%,          2, -----------, Fill Constant Data
      INFO:        0.022,      0.0%,          2, -----------, Deserialize DLA Sections
      INFO:        0.002,      0.0%,          2, -----------, Process target-specific data
      INFO:        0.116,      0.2%,          2,       0.058, Set Inference Input
      INFO:        0.427,      0.9%,         24,       0.213, Set Inference Output
      INFO:       27.702,     59.3%,          2,      13.851, Inference
      INFO:       46.732,    100.0%,          2,      14.122, Total
      INFO: ----------------------------------------------------------------------------------------------
      INFO:                                 Runtime Status (LEVEL 1) - Breakdown
      INFO: ----------------------------------------------------------------------------------------------
      INFO:   Inference: avg Time/inf.: 13.850830078125 ms over 2 times inference.
      INFO:  ====Time===, ==GraphIdx==, ==ExeIdx==, ===Description===
      INFO:       24.964,          ---,         #0, Inference
      INFO:        2.738,          ---,         #1, Inference
      INFO:  ----------------------------------------------------------------------------------------------
      INFO: ...
      ```

- Remove unused option: `--dla`, `--quit`

## 2022/10/19

Commit: 90f0bde56562e7cf98925c3e5c880448855ea038

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev

- Branch: mt8195

- Commit: a1148264129aa0617cf5defe11be05ebcd4cbc40


Changes:

- Install Neuron SDK headers to /usr/include/neuron/api/

- Refine /usr/share/benchmark_dla/benchmark.py

  - Use argparse to write user friendly command line interfaces, such as:

    ```
    options:
      -h, --help
      --auto
      --stress
      --file FILE
      --target {mdla2.0,vpu,tflite_cpu}
      --dla DLA
      --count COUNT
      --quit
    ```

    Find detailed description of each option by cmd: `python3 benchmark.py -h`

## 2022/06/23

Commit: c535f824ddbca2e815e51cfcc6e52177efd76f97

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev
- Branch: mt8195

- Commit: 8ae49e3c36f020b65d7926244c284a76b3477331


Changes:

- For benchmark, use proper way to query input/output info. Avoid print confusing error message, such as 'inference fail'

|           Binary           |                  Commit                  |           Branch           | Module |
| :------------------------: | :--------------------------------------: | :------------------------: | :----: |
|    libapu_mdw.so.2.0.0     | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
|      libedma.so.3.0.0      | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
|    libmdla_ut.s0.2.0.0     | 82ffbd65a4c209684bfae76df8a1823a2fb27b2d | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_runtime.so.5.1.1 | 94c28521c00482a9dd068d74455f263ea81bd8c2 |         NP5_0_8139         |        |
|      libvpu5.s0.5.0.0      | 53f8320d404cb66e55dedc5709b095b3bbb93fed | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_platform.vpu.so  | 94c28521c00482a9dd068d74455f263ea81bd8c2 |         NP5_0_8139         |        |
|         ncc-tflite         | e81c87f5607285f36aca2249e21b5dfbad88f99e |           NP5_0            |        |
|          neuronrt          | 94c28521c00482a9dd068d74455f263ea81bd8c2 |         NP5_0_8139         |        |

## 2022/06/21

Commit: 7ea117aa3983e98fba3b9c265081d8c7fe58a67f

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev
- Branch: mt8195

- Commit: b64a4636499bc7161ace4c5227aef6d9011138f8


Changes:

- Fix issue about benchmark does not run when user specifies model and target
- For runtime_api_sample and neuronrt: correct searching path of libneuron_runtime.so, avoid print confusing error message, such as 'Failed to open libneuron_runtime.5.so'

|           Binary           |                  Commit                  |           Branch           | Module |
| :------------------------: | :--------------------------------------: | :------------------------: | :----: |
|    libapu_mdw.so.2.0.0     | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
|      libedma.so.3.0.0      | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
|    libmdla_ut.s0.2.0.0     | 82ffbd65a4c209684bfae76df8a1823a2fb27b2d | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_runtime.so.5.1.1 | 94c28521c00482a9dd068d74455f263ea81bd8c2 |         NP5_0_8139         |        |
|      libvpu5.s0.5.0.0      | 53f8320d404cb66e55dedc5709b095b3bbb93fed | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_platform.vpu.so  | 94c28521c00482a9dd068d74455f263ea81bd8c2 |         NP5_0_8139         |        |
|         ncc-tflite         | e81c87f5607285f36aca2249e21b5dfbad88f99e |           NP5_0            |        |
|          neuronrt          | 94c28521c00482a9dd068d74455f263ea81bd8c2 |         NP5_0_8139         |        |

## 2022/05/27

Commit: 79fd7fe0edc81c3916fdee0f334d5244a7f627db

Binaries source:

- Repo: aiot_int/bsp/neuron-pilot-dev
- Branch: mt8195

- Commit: c325a8515b598c0226bae9cfe5618f4a7511f312


Changes:

- Initial binaries

|           Binary           |                  Commit                  |           Branch           | Module |
| :------------------------: | :--------------------------------------: | :------------------------: | :----: |
|    libapu_mdw.so.2.0.0     | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
|      libedma.so.3.0.0      | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
|    libmdla_ut.s0.2.0.0     | 82ffbd65a4c209684bfae76df8a1823a2fb27b2d | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_runtime.so.5.0.0 | 94c28521c00482a9dd068d74455f263ea81bd8c2 |         NP5_0_8139         |        |
|      libvpu5.s0.5.0.0      | 53f8320d404cb66e55dedc5709b095b3bbb93fed | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_platform.vpu.so  | 94c28521c00482a9dd068d74455f263ea81bd8c2 |         NP5_0_8139         |        |
|         ncc-tflite         | e81c87f5607285f36aca2249e21b5dfbad88f99e |           NP5_0            |        |
|          neuronrt          | 94c28521c00482a9dd068d74455f263ea81bd8c2 |         NP5_0_8139         |        |
