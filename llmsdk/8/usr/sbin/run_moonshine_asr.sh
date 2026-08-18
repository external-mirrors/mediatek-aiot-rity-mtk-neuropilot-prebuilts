#!/bin/sh
# Thin wrapper around moonshine_asr, which takes 6 positional paths and has no config file
# (unlike llm_cmdline_tool's runners). This script is the equivalent of their config yaml:
# it pins the on-device asset layout.
#
#   run_moonshine_asr.sh [--wav <file> | <wav>] [extra args...]
#
# Assets are NOT shipped in the image: they come from the moonshine-tiny inference package, which
# the user downloads and pushes with its own scripts/ (same layout as the other pretrained-DLA
# packages). Expected layout under the model dir:
#   dla/encoder.dla  dla/decoder_init.dla  dla/decoder.dla   <- MT8391 builds
#   tokenizer/vocab.bin  tokenizer/embed_weights.bin         <- platform-independent
#   test_audio_16k.wav                                       <- optional sample
#
# The model dir is looked up as /usr/share/llm/moonshine-tiny (where the package's
# 00_detect_os.bat + 01_push-models.bat put it on Yocto), then /root/moonshine-tiny.
# Override with MODELS=/some/where.
#
# Prefer the 16 kHz sample for a first run: the 48 kHz WAV goes through the CPU
# polyphase resampler, which is the slowest part of the pipeline and only muddies
# a first-light test.

set -e

# Locate the binary. Prefer one sitting next to this script — that is the adb-push / scp layout,
# where both land in /root and nothing is in PATH. Fall back to PATH, which is the
# recipe-installed layout (both go to ${bindir}). Override with BIN=/path/to/moonshine_asr.
if [ -z "$BIN" ]; then
    _d=$(dirname "$0")
    if [ -x "$_d/moonshine_asr" ]; then
        BIN="$_d/moonshine_asr"
    else
        BIN=moonshine_asr
    fi
fi

# Model dir: wherever the inference package was pushed. Take whichever exists; fall back to the
# package's Yocto location so the error message names something a user can act on.
if [ -z "${MODELS:-}" ]; then
    for _d in /usr/share/llm/moonshine-tiny /root/moonshine-tiny; do
        if [ -d "$_d" ]; then
            MODELS="$_d"
            break
        fi
    done
    MODELS="${MODELS:-/usr/share/llm/moonshine-tiny}"
fi

# --wav <file> is accepted so this wrapper honours the asr_cmdline_tool contract ("every ASR
# entry takes --wav"); the original positional form still works.
# (plain `if` instead of `[ $# -gt 0 ] && shift`: same behaviour under `set -e`, just one less
# thing to reason about now that there are two branches.)
if [ "${1:-}" = "--wav" ] || [ "${1:-}" = "-w" ]; then
    shift
    if [ $# -eq 0 ]; then
        echo "--wav needs a file argument" >&2
        exit 1
    fi
    WAV="$1"
    shift
else
    WAV="${1:-$MODELS/test_audio_16k.wav}"
    if [ $# -gt 0 ]; then shift; fi
fi

for f in dla/encoder.dla dla/decoder_init.dla dla/decoder.dla \
         tokenizer/vocab.bin tokenizer/embed_weights.bin; do
    if [ ! -f "$MODELS/$f" ]; then
        echo "Missing asset: $MODELS/$f" >&2
        echo "Push the moonshine-tiny inference package first (scripts/run_all_asr.bat)," >&2
        echo "or point MODELS= at wherever you put it." >&2
        exit 1
    fi
done
if [ ! -f "$WAV" ]; then
    echo "Missing WAV: $WAV" >&2
    exit 1
fi

exec "$BIN" \
    "$MODELS/dla/encoder.dla" \
    "$MODELS/dla/decoder_init.dla" \
    "$MODELS/dla/decoder.dla" \
    "$MODELS/tokenizer/vocab.bin" \
    "$WAV" \
    "$MODELS/tokenizer/embed_weights.bin" \
    "$@"
