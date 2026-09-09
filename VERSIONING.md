# Versioning

Releases follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):
`MAJOR.MINOR.PATCH`.

Tags are applied on the `scarthgap` branch only. `kirkstone` stays untagged;
if it is ever tagged it gets its own independent counter under its own prefix.

## Tag format

    scarthgap-v<MAJOR>.<MINOR>.<PATCH>

Each release line carries its own prefix and its own counter, because the
branches hold different binaries and never merge. `scarthgap-v1.2.0` and a
future `kirkstone-v1.2.0` are unrelated packages.

    git describe --match 'scarthgap-v*' --tags

Pre-release candidates, when one is needed before a monthly drop:
`scarthgap-v1.2.0-rc.1`.

## What the version describes

The version tracks **this repository's contract with its consumers**, not the
upstream version of any binary inside it. Every prebuilt already carries its
own version in its filename (`libneuronusdk_runtime.mtk.so.8.2.16`,
`libapu_mdw.so.2.0.0`), and its build provenance in a `MANIFEST.yaml`.

The contract is:

| Contract surface | Location |
| --- | --- |
| C header API | `neuron/*/usr/include/neuron/api/*.h` |
| Shared library soname | `*.so.N` in `neuron/*/usr/lib64`, `mdw/*/usr/lib64`, `llmsdk/*/usr/lib64`, `mvpu/*/usr/lib64` |
| Install interface | `Makefile` — accepted `NP_VER` / `MDW_VER` values, install paths, variable names |
| CLI interface | `neuronrt`, `ncc-tflite`, `llm_cmdline_tool`, `asr_cmdline_tool`, the `mllm_*` and ASR runners — flags and output format |
| Compiled artifact format | `.dla` compatibility, i.e. whether a consumer must recompile their models |

## Provenance: one MANIFEST.yaml per component

Every component directory carries a `MANIFEST.yaml` recording the upstream
repo, branch and commit its binaries were built from, the toolchain, and any
deliberate deviation from the vendor drop:

    neuron/6/MANIFEST.yaml      mdw/android13/MANIFEST.yaml
    neuron/8/MANIFEST.yaml      mdw/android15/MANIFEST.yaml
    llmsdk/8/MANIFEST.yaml      mdw/mt8894/MANIFEST.yaml
                                mvpu/25/MANIFEST.yaml

### Two commits per entry, and one of them is a claim

Each group of binaries records both:

    repo_commit: 36bd7f8            # ground truth
    upstream_commit: unknown        # a claim
    claimed_in: Release.md 2026/8/26
    verified: no

- `repo_commit` is the commit of **this** repo that last changed those files.
  It is derivable (`git log -1 -- <path>`), always correct, and is what the
  manifests key on.
- `upstream_commit` is transcribed from a release note or a commit message.
  **No upstream SHA in this repo has been verified against its upstream
  repo**, so every one carries `verified: no` and a `claimed_in:` citation
  saying where it was copied from.

That distinction is not pedantry. The historic Release.md tables were carried
forward by copy-paste, restamping rows for binaries that had not changed, so a
row is not evidence that the binary was built from the SHA beside it —
`neuron/6` ships artifacts from four different drops that every table lists
under a single SHA. Trust `repo_commit`; treat `upstream_commit` as a lead
until someone with access to the upstream repo confirms it and flips
`verified`.

Prefer `unknown` with a `NOTE:` over a plausible guess. An honest gap is
reviewable; a wrong SHA is worse than a missing one because it stops anyone
looking.

The rules:

- **Record only what the artifact cannot tell you.** Sizes, hashes and
  sonames are already in git and in the ELF headers. Source commits, build
  flags, toolchain versions and patched-in fixes are not.
- **One file per component, never one at the root.** Five teams appending to
  one file conflicts on every drop; each team touching only its own directory
  never does. `git log <component>/MANIFEST.yaml` is that component's version
  history for free.
- **A drop that changes binaries changes its manifest in the same commit.**
  If the upstream commit is genuinely unknown, write `commit: unknown` with a
  `NOTE:` saying why. An honest gap is reviewable; a stale value is not.
- **No per-component version numbers.** The repo ships as one Yocto `SRCREV`,
  so it has one version. A component's independent progression is expressed
  by which manifest changed in a release — `git log <prev-tag>..<tag> --
  llmsdk/` answers "what changed in llmsdk" without a second counter to keep
  in sync. Per-component versions would only be real if a consumer could
  install one component without the others, which the `Makefile` does not
  allow; that would be a repo split, not a numbering change.
- `sample/` has no manifest. Those are scripts written in this repo, so git
  history *is* their provenance.

### The dlopen coupling, and `make check-abi`

The llmsdk runners do not link Neuron. `readelf -d` shows no `libneuronusdk_*`
in any runner's `DT_NEEDED`; they `dlopen("libneuronusdk_runtime.mtk.so")` —
the unversioned symlink. So the loader enforces nothing, soname protection
does not apply, and a runner will happily load an incompatible runtime and
misbehave at run time with no error from the linker.

`llmsdk/8/MANIFEST.yaml`'s `built_against.neuron_api` is the only record of
that dependency. It holds the commit of *this repo* that last changed
`neuron/8/usr/include`, which makes it checkable:

    make check-abi

The check fails when the shipped headers have moved past what llmsdk was built
against. That is the rebuild trigger, and it is a **header change**, not a
library change: a soname-compatible runtime refresh (`8.2.16` -> `8.2.17`)
needs no rebuild.

When Neuron's headers change:

1. Rebuild the llmsdk runners against the new headers.
2. Update `source.commit` and `built_against.neuron_api` in
   `llmsdk/8/MANIFEST.yaml`.
3. `make check-abi` must pass before the tag.

## Increment rules

**MAJOR** — breaking API/ABI changes, a raise of the minimum required Neuron
Runtime version, or the yearly baseline bump.

In this repository that means:

- a header is removed, or a function signature changes
- a library soname major changes (`.so.6` -> `.so.8`)
- an existing `NP_VER` / `MDW_VER` value is dropped, or an install path or
  Makefile variable is renamed
- a CLI flag is removed, or output a consumer parses changes shape
- `.dla` format becomes incompatible with previously compiled models
- the minimum required Neuron Runtime version is raised, i.e. the drop no
  longer runs on a board whose `libneuronusdk_runtime.mtk.so` predates it
- the yearly baseline, cut once a year even when nothing above applies

**MINOR** — backward-compatible features, delivered on a monthly cadence:

- a new library, tool or runner is added
- a new `NP_VER` / `MDW_VER` target is added
- a new header API or a new CLI flag
- an upstream NeuroPilot uplift that stays backward compatible
  (`8.2.16` -> `8.3.0`)

**PATCH** — backward-compatible bug fixes, released as needed:

- binaries rebuilt from the same API, bug fixes
- documentation, release note or licence corrections

## Cadence

- MAJOR — once a year, as the baseline bump.
- MINOR — once a month, carrying that month's drop.
- PATCH — as needed, whenever a fix has to be delivered.

A breaking change does not wait for the yearly baseline: it takes a MAJOR
whenever it lands.

Mid-month fixes are committed to `scarthgap` as usual and are not tagged
individually. A PATCH tag is cut when a state has to be pinned by a consumer.

    scarthgap-v1.1.0   monthly drop
    scarthgap-v1.1.1   mid-month fix, delivered on request
    scarthgap-v1.2.0   next monthly drop
    scarthgap-v2.0.0   yearly baseline

## Release checklist

Per drop, by whoever updates a component:

1. Update the prebuilts and that component's `MANIFEST.yaml` in the same
   commit.
2. `make check-abi`.

At tag time, by the release owner only:

3. Add one `Release.md` entry: `## [scarthgap-vX.Y.Z] - YYYY-MM-DD`, a `Bump:`
   line naming the level and the reason, and prose on what changed and why.
   No per-binary table — that is what the manifests are for.
4. `git tag -a scarthgap-vX.Y.Z -m "..."`.
5. `git push origin scarthgap --follow-tags`.
6. Hand the tag's commit SHA to the Yocto side.

Splitting it this way is deliberate: contributors touch only their own
directory, so the monthly drops stop conflicting in `Release.md`, and one
person writes the entry once.

The `Bump:` line is what keeps this honest — it forces whoever reviews the
drop to answer whether the change is breaking.

To answer "what was this release built from":

    git diff <prev-tag>..<tag> -- '*/MANIFEST.yaml'

## Consuming from Yocto

    SRCBRANCH = "scarthgap"
    SRCREV = "<the SHA the tag points at>"
    PV = "1.1.0"

Pin the SHA rather than the tag name; a tag can be moved, a SHA cannot.

## Source of truth

Git tags. There is deliberately no `VERSION` file and no generated changelog —
one more place to fall out of sync, for no gain at this cadence.
