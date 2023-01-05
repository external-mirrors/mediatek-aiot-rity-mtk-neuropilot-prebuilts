# Release Note

## 2023/01/05

Repo:  aiot_int/bsp/neuron-pilot-dev

Branch: mt8195

Commit:   18dbf3228259a4fae8b1412236d7e69e4f2905c7 

Changes:

- Upgrade neuron/ncc-tflite from 5.1.1 to 5.8.3

| Binary                     | Commit                                   | Branch                     | Module |
| -------------------------- | ---------------------------------------- | -------------------------- | ------ |
| libapu_mdw.so.2.0.0        | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libapu_mdw_batch.so.2.0.0  | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libedma.so.3.0.0           | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libmdla_ut.s0.2.0.0        | 82ffbd65a4c209684bfae76df8a1823a2fb27b2d | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_runtime.so.5.8.3 | 1dad43edb9824eb4ff04e667f2cdbceff75c646b | NP5_0                      |        |
| libvpu5.so.5.0.0           | 53f8320d404cb66e55dedc5709b095b3bbb93fed | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_platform.vpu.so  | 1dad43edb9824eb4ff04e667f2cdbceff75c646b | NP5_0                      |        |
| ncc-tflite                 | 21ff854ca7b1ed6754739cb2c2d551468db76e62 | NP5_0                      |        |
| neuronrt                   | 1dad43edb9824eb4ff04e667f2cdbceff75c646b | NP5_0                      |        |

## 2022/11/24

Repo:  aiot_int/bsp/neuron-pilot-dev

Branch: mt8195

Commit:  6fb38d868a5f26cc59bd46a06c57d9ab2cfa3237

Changes:

- Update benchmark.py, enable profile option

  -  Add profile option: `--profile` to print profile information after model inference.

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

Repo:  aiot_int/bsp/neuron-pilot-dev

Branch: mt8195

Commit: a1148264129aa0617cf5defe11be05ebcd4cbc40

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

Repo:  aiot_int/bsp/neuron-pilot-dev

Branch: mt8195

Commit: 8ae49e3c36f020b65d7926244c284a76b3477331

Changes:

- For benchmark, use proper way to query input/output info. Avoid print confusing error message, such as 'inference fail'

| Binary                     | Commit                                   | Branch                     | Module |
| -------------------------- | ---------------------------------------- | -------------------------- | ------ |
| libapu_mdw.so.2.0.0        | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libedma.so.3.0.0           | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libmdla_ut.s0.2.0.0        | 82ffbd65a4c209684bfae76df8a1823a2fb27b2d | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_runtime.so.5.1.1 | 94c28521c00482a9dd068d74455f263ea81bd8c2 | NP5_0_8139                 |        |
| libvpu5.s0.5.0.0           | 53f8320d404cb66e55dedc5709b095b3bbb93fed | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_platform.vpu.so  | 94c28521c00482a9dd068d74455f263ea81bd8c2 | NP5_0_8139                 |        |
| ncc-tflite                 | e81c87f5607285f36aca2249e21b5dfbad88f99e | NP5_0                      |        |
| neuronrt                   | 94c28521c00482a9dd068d74455f263ea81bd8c2 | NP5_0_8139                 |        |

## 2022/06/21

Repo:  aiot_int/bsp/neuron-pilot-dev

Branch: mt8195

Commit: b64a4636499bc7161ace4c5227aef6d9011138f8

Changes:

- Fix issue about benchmark does not run when user specifies model and target
- For runtime_api_sample and neuronrt: correct searching path of libneuron_runtime.so, avoid print confusing error message, such as 'Failed to open libneuron_runtime.5.so'

| Binary                     | Commit                                   | Branch                     | Module |
| -------------------------- | ---------------------------------------- | -------------------------- | ------ |
| libapu_mdw.so.2.0.0        | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libedma.so.3.0.0           | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libmdla_ut.s0.2.0.0        | 82ffbd65a4c209684bfae76df8a1823a2fb27b2d | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_runtime.so.5.1.1 | 94c28521c00482a9dd068d74455f263ea81bd8c2 | NP5_0_8139                 |        |
| libvpu5.s0.5.0.0           | 53f8320d404cb66e55dedc5709b095b3bbb93fed | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_platform.vpu.so  | 94c28521c00482a9dd068d74455f263ea81bd8c2 | NP5_0_8139                 |        |
| ncc-tflite                 | e81c87f5607285f36aca2249e21b5dfbad88f99e | NP5_0                      |        |
| neuronrt                   | 94c28521c00482a9dd068d74455f263ea81bd8c2 | NP5_0_8139                 |        |





## 2022/05/27

Repo:  aiot_int/bsp/neuron-pilot-dev

Branch: mt8195

Commit: c325a8515b598c0226bae9cfe5618f4a7511f312

Changes:

- Initial binaries

| Binary                     | Commit                                   | Branch                     | Module |
| -------------------------- | ---------------------------------------- | -------------------------- | ------ |
| libapu_mdw.so.2.0.0        | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libedma.so.3.0.0           | 7079fc5414795ea1b6ec54fef5658a4f618ba772 | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libmdla_ut.s0.2.0.0        | 82ffbd65a4c209684bfae76df8a1823a2fb27b2d | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_runtime.so.5.0.0 | 94c28521c00482a9dd068d74455f263ea81bd8c2 | NP5_0_8139                 |        |
| libvpu5.s0.5.0.0           | 53f8320d404cb66e55dedc5709b095b3bbb93fed | alps-mp-r0.mp6.tc33sp.ppr2 |        |
| libneuron_platform.vpu.so  | 94c28521c00482a9dd068d74455f263ea81bd8c2 | NP5_0_8139                 |        |
| ncc-tflite                 | e81c87f5607285f36aca2249e21b5dfbad88f99e | NP5_0                      |        |
| neuronrt                   | 94c28521c00482a9dd068d74455f263ea81bd8c2 | NP5_0_8139                 |        |



