# Release Note

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



