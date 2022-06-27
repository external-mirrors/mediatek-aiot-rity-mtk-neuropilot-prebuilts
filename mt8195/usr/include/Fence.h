#pragma once

#include <stdint.h>
#include <sys/cdefs.h>

__BEGIN_DECLS

/*!
 * This struct is used to receive the fence file descriptor and the post-inference callback
 * in fenced execution. Specifically, user should allocate this struct, and pass its address into
 * fenced execution API. The fence FD and the call back will be set properly. After fence is
 * triggered, caller can invoke the callback to retrieve execution status and execution time.
 */
typedef struct {
    /// The file descriptor of the fence to be triggered before inference.
    int64_t inputFenceFd;

    /// The file descriptor of the fence to be triggered at the end of inference.
    int64_t fenceFd;

    /// Caller should call this callback after fence is triggered to retrieve execution status
    /// and time. Caller should send back the address of the original FenceInfo which possesses
    /// this callback in the first parameter 'opaque'.
    void (*callback)(void* opaque);

    /// Execution status. This will be set after callback is called.
    uint32_t status;

    /// Execution time. This will be set after callback is called.
    uint32_t microseconds;

    /// The following data are for internal use. Don't access them.
    uint64_t __internal__[4];
} FenceInfo;

/**
 * Check if the model supports fenced execution. Call this function after runtime is loaded with
 * model.
 * @param runtime The address of the created neuron runtime instance.
 * @param supported Non-zero value indicates that the model supports fenced execution.
 * @return An error code indicates whether the test model executes successfully.
 */
int NeuronRuntime_isFenceSupported(void* runtime, uint8_t* supported);

/**
 * Do fenced-inference. The call should return without waiting for inference to finish. The caller
 * should prepare a FenceInfo structure and pass its address into this API. FenceFd in FenceInfo
 * will be set, and the caller can be signaled when inference completes (or error exit) by waiting
 * on the fence. Most importantly, after the fence is triggered, caller MUST call the callback in
 * fenceInfo so that Neuron can perform certain post-execution tasks. The final execution status
 * and inference time can be retrieved in FenceInfo after the callback is executed.
 * @param runtime The address of the created neuron runtime instance.
 * @param fenceInfo The struct is used to receive the fence file descriptor and the post-inference
 *                  callback in fenced execution.
 * @return A Runtime error code.
 */
int NeuronRuntime_inferenceFenced(void* runtime, FenceInfo* fenceInfo);

__END_DECLS
