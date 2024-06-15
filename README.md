# PyTorch/XLA

<b>Current CI status:</b>  ![GitHub Actions
status](https://github.com/pytorch/xla/actions/workflows/build_and_test.yml/badge.svg)

PyTorch/XLA is a Python package that uses the [XLA deep learning
compiler](https://www.tensorflow.org/xla) to connect the [PyTorch deep learning
framework](https://pytorch.org/) and [Cloud
TPUs](https://cloud.google.com/tpu/). You can try it right now, for free, on a
single Cloud TPU VM with
[Kaggle](https://www.kaggle.com/discussions/product-feedback/369338)!

Take a look at one of our [Kaggle
notebooks](https://github.com/pytorch/xla/tree/master/contrib/kaggle) to get
started:

* [Stable Diffusion with PyTorch/XLA
  2.0](https://github.com/pytorch/xla/blob/master/contrib/kaggle/pytorch-xla-2-0-on-kaggle.ipynb)
* [Distributed PyTorch/XLA
  Basics](https://github.com/pytorch/xla/blob/master/contrib/kaggle/distributed-pytorch-xla-basics-with-pjrt.ipynb)

## Getting Started

**PyTorch/XLA is now on PyPI!**

To install PyTorch/XLA stable build in a new TPU VM:

```
pip install torch~=2.3.0 torch_xla[tpu]~=2.3.0 -f https://storage.googleapis.com/libtpu-releases/index.html
```

To install PyTorch/XLA nightly build in a new TPU VM:

```
pip3 install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu
pip3 install https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-nightly-cp310-cp310-linux_x86_64.whl
```

To update your existing training loop, make the following changes:

```diff
-import torch.multiprocessing as mp
+import torch_xla as xla
+import torch_xla.core.xla_model as xm
+import torch_xla.distributed.xla_multiprocessing as xmp

 def _mp_fn(index):
   ...

+  # Move the model paramters to your XLA device
+  model.to(xla.device())

   for inputs, labels in train_loader:
+    with xla.step():
+      # Transfer data to the XLA device. This happens asynchronously.
+      inputs, labels = inputs.to(xla.device()), labels.to(xla.device())
       optimizer.zero_grad()
       outputs = model(inputs)
       loss = loss_fn(outputs, labels)
       loss.backward()
-      optimizer.step()
+      # `xm.optimizer_step` combines gradients across replicas
+      xm.optimizer_step(optimizer)

 if __name__ == '__main__':
-  mp.spawn(_mp_fn, args=(), nprocs=world_size)
+  # xmp.spawn automatically selects the correct world size
+  xmp.spawn(_mp_fn, args=())
```

If you're using `DistributedDataParallel`, make the following changes:


```diff
 import torch.distributed as dist
-import torch.multiprocessing as mp
+import torch_xla as xla
+import torch_xla.distributed.xla_multiprocessing as xmp
+import torch_xla.distributed.xla_backend

 def _mp_fn(rank):
   ...

-  os.environ['MASTER_ADDR'] = 'localhost'
-  os.environ['MASTER_PORT'] = '12355'
-  dist.init_process_group("gloo", rank=rank, world_size=world_size)
+  # Rank and world size are inferred from the XLA device runtime
+  dist.init_process_group("xla", init_method='xla://')
+
+  model.to(xm.xla_device())
+  # `gradient_as_bucket_view=True` required for XLA
+  ddp_model = DDP(model, gradient_as_bucket_view=True)

-  model = model.to(rank)
-  ddp_model = DDP(model, device_ids=[rank])

   for inputs, labels in train_loader:
+    with xla.step():
+      inputs, labels = inputs.to(xla.device()), labels.to(xla.device())
       optimizer.zero_grad()
       outputs = ddp_model(inputs)
       loss = loss_fn(outputs, labels)
       loss.backward()
       optimizer.step()

 if __name__ == '__main__':
-  mp.spawn(_mp_fn, args=(), nprocs=world_size)
+  xmp.spawn(_mp_fn, args=())
```

Additional information on PyTorch/XLA, including a description of its semantics
and functions, is available at [PyTorch.org](http://pytorch.org/xla/). See the
[API Guide](API_GUIDE.md) for best practices when writing networks that run on
XLA devices (TPU, CUDA, CPU and...).

Our comprehensive user guides are available at:

[Documentation for the latest release](https://pytorch.org/xla)

[Documentation for master branch](https://pytorch.org/xla/master)


## PyTorch/XLA tutorials

* [Cloud TPU VM
  quickstart](https://cloud.google.com/tpu/docs/run-calculation-pytorch)
* [Cloud TPU Pod slice
  quickstart](https://cloud.google.com/tpu/docs/pytorch-pods)
* [Profiling on TPU
  VM](https://cloud.google.com/tpu/docs/pytorch-xla-performance-profiling-tpu-vm)
* [GPU guide](docs/gpu.md)

## Available docker images and wheels

### Python packages

PyTorch/XLA releases starting with version r2.1 will be available on PyPI. You
can now install the main build with `pip install torch_xla`. To also install the
Cloud TPU plugin, install the optional `tpu` dependencies after installing the main build with

```
pip install torch_xla[tpu] -f https://storage.googleapis.com/libtpu-releases/index.html
```

GPU and nightly builds are available in our public GCS bucket.

| Version | Cloud TPU/GPU VMs Wheel |
| --- | ----------- |
| 2.3 (Python 3.8) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-2.3.0-cp38-cp38-manylinux_2_28_x86_64.whl` |
| 2.3 (Python 3.10) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-2.3.0-cp310-cp310-manylinux_2_28_x86_64.whl` |
| 2.3 (Python 3.11) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-2.3.0-cp311-cp311-manylinux_2_28_x86_64.whl` |
| 2.3 (CUDA 12.1 + Python 3.8) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/cuda/12.1/torch_xla-2.3.0-cp38-cp38-manylinux_2_28_x86_64.whl` |
| 2.3 (CUDA 12.1 + Python 3.10) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/cuda/12.1/torch_xla-2.3.0-cp310-cp310-manylinux_2_28_x86_64.whl` |
| 2.3 (CUDA 12.1 + Python 3.11) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/cuda/12.1/torch_xla-2.3.0-cp311-cp311-manylinux_2_28_x86_64.whl` |
| nightly (Python 3.8) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-nightly-cp38-cp38-linux_x86_64.whl` |
| nightly (Python 3.10) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-nightly-cp310-cp310-linux_x86_64.whl` |
| nightly (CUDA 12.1 + Python 3.8) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/cuda/12.1/torch_xla-nightly-cp38-cp38-linux_x86_64.whl` |

To install the release candidate, you can replace `torch_xla-nightly` with `torch_xla-2.4.0rc1`. Similarly, to install the corresponding Torch version, simply replace `torch_xla` with `torch`.

For installing a nightly wheel of a specified date, you can append `+yyyymmdd` after `torch_xla-nightly` or `torch-nightly`. To obtain the corresponding `libtpu` version, you can use the following link to install the desired wheels:

`https://storage.googleapis.com/cloud-tpu-tpuvm-artifacts/wheels/libtpu-nightly/libtpu_nightly-0.1.devyyyymmdd-py3-none-any.whl`.

Here is an example:

```
pip3 install torch==2.5.0.dev20240613+cpu --index-url https://download.pytorch.org/whl/nightly/cpu
pip3 install https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-nightly%2B20240613-cp310-cp310-linux_x86_64.whl
pip3 install https://storage.googleapis.com/cloud-tpu-tpuvm-artifacts/wheels/libtpu-nightly/libtpu_nightly-0.1.dev20240613-py3-none-any.whl
```

The torch wheel version `2.5.0.dev20240613+cpu` can be found at https://download.pytorch.org/whl/nightly/torch/.

<details>

<summary>older versions</summary>

| Version | Cloud TPU VMs Wheel |
|---------|-------------------|
| 2.2 (Python 3.8) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-2.2.0-cp38-cp38-manylinux_2_28_x86_64.whl` |
| 2.2 (Python 3.10) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-2.2.0-cp310-cp310-manylinux_2_28_x86_64.whl` |
| 2.2 (CUDA 12.1 + Python 3.8) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/cuda/12.1/torch_xla-2.2.0-cp38-cp38-manylinux_2_28_x86_64.whl` |
| 2.2 (CUDA 12.1 + Python 3.10) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/cuda/12.1/torch_xla-2.2.0-cp310-cp310-manylinux_2_28_x86_64.whl` |
| 2.1 (XRT + Python 3.10) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/xrt/tpuvm/torch_xla-2.1.0%2Bxrt-cp310-cp310-manylinux_2_28_x86_64.whl` |
| 2.1 (Python 3.8) | `https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-2.1.0-cp38-cp38-linux_x86_64.whl` |
| 2.0 (Python 3.8) | `https://storage.googleapis.com/tpu-pytorch/wheels/tpuvm/torch_xla-2.0-cp38-cp38-linux_x86_64.whl` |
| 1.13 | `https://storage.googleapis.com/tpu-pytorch/wheels/tpuvm/torch_xla-1.13-cp38-cp38-linux_x86_64.whl` |
| 1.12 | `https://storage.googleapis.com/tpu-pytorch/wheels/tpuvm/torch_xla-1.12-cp38-cp38-linux_x86_64.whl` |
| 1.11 | `https://storage.googleapis.com/tpu-pytorch/wheels/tpuvm/torch_xla-1.11-cp38-cp38-linux_x86_64.whl` |
| 1.10 | `https://storage.googleapis.com/tpu-pytorch/wheels/tpuvm/torch_xla-1.10-cp38-cp38-linux_x86_64.whl` |

<br/>

Note: For TPU Pod customers using XRT (our legacy runtime), we have custom
wheels for `torch` and `torch_xla` at
`https://storage.googleapis.com/tpu-pytorch/wheels/xrt`.

| Package | Cloud TPU VMs Wheel (XRT on Pod, Legacy Only) |
| --- | ----------- |
| torch_xla | `https://storage.googleapis.com/pytorch-xla-releases/wheels/xrt/tpuvm/torch_xla-2.1.0%2Bxrt-cp310-cp310-manylinux_2_28_x86_64.whl` |
| torch | `https://storage.googleapis.com/pytorch-xla-releases/wheels/xrt/tpuvm/torch-2.1.0%2Bxrt-cp310-cp310-linux_x86_64.whl` |

<br/>

| Version | GPU Wheel + Python 3.8 |
| --- | ----------- |
| 2.1+ CUDA 11.8 | `https://storage.googleapis.com/pytorch-xla-releases/wheels/cuda/11.8/torch_xla-2.1.0-cp38-cp38-manylinux_2_28_x86_64.whl` |
| 2.0 + CUDA 11.8 | `https://storage.googleapis.com/tpu-pytorch/wheels/cuda/118/torch_xla-2.0-cp38-cp38-linux_x86_64.whl` |
| 2.0 + CUDA 11.7 | `https://storage.googleapis.com/tpu-pytorch/wheels/cuda/117/torch_xla-2.0-cp38-cp38-linux_x86_64.whl` |
| 1.13 | `https://storage.googleapis.com/tpu-pytorch/wheels/cuda/112/torch_xla-1.13-cp38-cp38-linux_x86_64.whl` |
| nightly + CUDA 12.0 >= 2023/06/27| `https://storage.googleapis.com/pytorch-xla-releases/wheels/cuda/12.0/torch_xla-nightly-cp38-cp38-linux_x86_64.whl` |
| nightly + CUDA 11.8 <= 2023/04/25| `https://storage.googleapis.com/tpu-pytorch/wheels/cuda/118/torch_xla-nightly-cp38-cp38-linux_x86_64.whl` |
| nightly + CUDA 11.8 >= 2023/04/25| `https://storage.googleapis.com/pytorch-xla-releases/wheels/cuda/11.8/torch_xla-nightly-cp38-cp38-linux_x86_64.whl` |

<br/>

| Version | GPU Wheel + Python 3.7 |
| --- | ----------- |
| 1.13 | `https://storage.googleapis.com/tpu-pytorch/wheels/cuda/112/torch_xla-1.13-cp37-cp37m-linux_x86_64.whl` |
| 1.12 | `https://storage.googleapis.com/tpu-pytorch/wheels/cuda/112/torch_xla-1.12-cp37-cp37m-linux_x86_64.whl` |
| 1.11 | `https://storage.googleapis.com/tpu-pytorch/wheels/cuda/112/torch_xla-1.11-cp37-cp37m-linux_x86_64.whl` |

<br/>

| Version | Colab TPU Wheel |
| --- | ----------- |
| 2.0 | `https://storage.googleapis.com/tpu-pytorch/wheels/colab/torch_xla-2.0-cp310-cp310-linux_x86_64.whl` |

</details>

### Docker

| Version | Cloud TPU VMs Docker |
| --- | ----------- |
| 2.3 | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:r2.3.0_3.10_tpuvm` |
| 2.2 | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:r2.2.0_3.10_tpuvm` |
| 2.1 | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:r2.1.0_3.10_tpuvm` |
| 2.0 | `gcr.io/tpu-pytorch/xla:r2.0_3.8_tpuvm` |
| 1.13 | `gcr.io/tpu-pytorch/xla:r1.13_3.8_tpuvm` |
| nightly python | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:nightly_3.10_tpuvm` |

To use the above dockers, please pass `--privileged --net host --shm-size=16G` along. Here is an example:
```bash
docker run --privileged --net host --shm-size=16G -it us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:nightly_3.10_tpuvm /bin/bash
```

<br/>

| Version | GPU CUDA 12.1 Docker |
| --- | ----------- |
| 2.3 | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:r2.3.0_3.10_cuda_12.1` |
| 2.2 | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:r2.2.0_3.10_cuda_12.1` |
| 2.1 | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:r2.1.0_3.10_cuda_12.1` |
| nightly | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:nightly_3.8_cuda_12.1` |
| nightly at date | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:nightly_3.8_cuda_12.1_YYYYMMDD` |

<br/>

| Version | GPU CUDA 11.8 + Docker |
| --- | ----------- |
| 2.1 | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:r2.1.0_3.10_cuda_11.8` |
| 2.0 | `gcr.io/tpu-pytorch/xla:r2.0_3.8_cuda_11.8` |
| nightly | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:nightly_3.8_cuda_11.8` |
| nightly at date | `us-central1-docker.pkg.dev/tpu-pytorch-releases/docker/xla:nightly_3.8_cuda_11.8_YYYYMMDD` |

<br/>

<details>

<summary>older versions</summary>

| Version | GPU CUDA 11.7 + Docker |
| --- | ----------- |
| 2.0 | `gcr.io/tpu-pytorch/xla:r2.0_3.8_cuda_11.7` |

<br/>

| Version | GPU CUDA 11.2 + Docker |
| --- | ----------- |
| 1.13 | `gcr.io/tpu-pytorch/xla:r1.13_3.8_cuda_11.2` |

<br/>

| Version | GPU CUDA 11.2 + Docker |
| --- | ----------- |
| 1.13 | `gcr.io/tpu-pytorch/xla:r1.13_3.7_cuda_11.2` |
| 1.12 | `gcr.io/tpu-pytorch/xla:r1.12_3.7_cuda_11.2` |

</details>

To run on [compute instances with
GPUs](https://cloud.google.com/compute/docs/gpus/create-vm-with-gpus).

## Troubleshooting

If PyTorch/XLA isn't performing as expected, see the [troubleshooting
guide](TROUBLESHOOTING.md), which has suggestions for debugging and optimizing
your network(s).

## Providing Feedback

The PyTorch/XLA team is always happy to hear from users and OSS contributors!
The best way to reach out is by filing an issue on this Github. Questions, bug
reports, feature requests, build issues, etc. are all welcome!

## Contributing

See the [contribution guide](CONTRIBUTING.md).

## Disclaimer

This repository is jointly operated and maintained by Google, Meta and a
number of individual contributors listed in the
[CONTRIBUTORS](https://github.com/pytorch/xla/graphs/contributors) file. For
questions directed at Meta, please send an email to opensource@fb.com. For
questions directed at Google, please send an email to
pytorch-xla@googlegroups.com. For all other questions, please open up an issue
in this repository [here](https://github.com/pytorch/xla/issues).

## Additional Reads

You can find additional useful reading materials in
* [Performance debugging on Cloud TPU
  VM](https://cloud.google.com/blog/topics/developers-practitioners/pytorchxla-performance-debugging-tpu-vm-part-1)
* [Lazy tensor
  intro](https://pytorch.org/blog/understanding-lazytensor-system-performance-with-pytorch-xla-on-cloud-tpu/)
* [Scaling deep learning workloads with PyTorch / XLA and Cloud TPU
  VM](https://cloud.google.com/blog/topics/developers-practitioners/scaling-deep-learning-workloads-pytorch-xla-and-cloud-tpu-vm)
* [Scaling PyTorch models on Cloud TPUs with
  FSDP](https://pytorch.org/blog/scaling-pytorch-models-on-cloud-tpus-with-fsdp/)

## Related Projects

* [OpenXLA](https://github.com/openxla)
* [HuggingFace](https://huggingface.co/docs/accelerate/en/basic_tutorials/tpu)
* [JetStream](https://github.com/google/JetStream-pytorch)
