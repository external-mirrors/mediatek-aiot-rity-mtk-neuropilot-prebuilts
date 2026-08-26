// SPDX-License-Identifier: MIT
/*
 * Copyright (c) 2026 MediaTek Inc.
 *
 * Minimal libatrace: the ATrace ABI that MediaTek's Android-built userspace
 * libraries link against, implemented on top of the ftrace trace_marker so the
 * events land in a normal `trace-cmd`/`perfetto` capture.
 *
 * NOTE: only the three entry points the shipped prebuilts reference.  Add more
 * of the ATrace ABI when a binary actually needs them.
 */
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

static int marker_fd = -1;

void atrace_init(void)
{
	static const char *const paths[] = {
		"/sys/kernel/tracing/trace_marker",
		"/sys/kernel/debug/tracing/trace_marker",
	};
	size_t i;

	if (marker_fd >= 0)
		return;

	for (i = 0; i < sizeof(paths) / sizeof(paths[0]); i++) {
		marker_fd = open(paths[i], O_WRONLY | O_CLOEXEC);
		if (marker_fd >= 0)
			return;
	}
	/* Tracing not mounted: every call below becomes a no-op. */
}

void atrace_begin(const char *name)
{
	char buf[256];
	int len;

	if (marker_fd < 0)
		return;

	len = snprintf(buf, sizeof(buf), "B|%d|%s", getpid(), name ? name : "");
	if (len > 0)
		(void)write(marker_fd, buf, len < (int)sizeof(buf) ? (size_t)len
								  : sizeof(buf) - 1);
}

void atrace_end(void)
{
	if (marker_fd < 0)
		return;

	(void)write(marker_fd, "E", 1);
}
