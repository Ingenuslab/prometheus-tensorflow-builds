FROM arm64v8/ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV BAZEL_VERSION=7.4.1
ENV PYTHON_VERSION=3.10

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    python3 \
    python3-pip \
    openjdk-17-jdk \
    crossbuild-essential-arm64 \
    qemu-user-static \
    binfmt-support \
    wget \
    unzip \
    zip \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/bin:${PATH}"

RUN wget https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/bazel-${BAZEL_VERSION}-installer-linux-x86_64.sh \
    && chmod +x bazel-${BAZEL_VERSION}-installer-linux-x86_64.sh \
    && ./bazel-${BAZEL_VERSION}-installer-linux-x86_64.sh --user \
    && rm bazel-${BAZEL_VERSION}-installer-linux-x86_64.sh


RUN git clone https://github.com/tensorflow/tensorflow.git /tensorflow_src

WORKDIR /tensorflow_src

RUN echo "" | python3 configure.py

RUN pip3 install numpy wheel keras_applications keras_preprocessing

RUN bazel build --config=opt --config=mkl_aarch64 --cpu=aarch64 \
    --action_env=PYTHON_BIN_PATH="/usr/bin/python3" \
    --action_env=PYTHON_LIB_PATH="/usr/local/lib/python${PYTHON_VERSION}/dist-packages" \
    --action_env=TF_NEED_CUDA=0 \
    --action_env=TF_NEED_ROCM=0 \
    --action_env=TF_NEED_TENSORRT=0 \
    --action_env=TF_ENABLE_XLA=0 \
    --action_env=TF_DOWNLOAD_CLANG=0 \
    --action_env=TF_SET_ANDROID_WORKSPACE=0 \
    --action_env=CC="/usr/bin/aarch64-linux-gnu-gcc" \
    --action_env=CXX="/usr/bin/aarch64-linux-gnu-g++" \
    //tensorflow/tools/pip_package:build_pip_package_py

RUN mkdir -p /tmp/tensorflow_pkg \
    && ./bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg

RUN cp /tmp/tensorflow_pkg/*.whl /tensorflow_wheel.whl

CMD ["ls", "-l", "/tensorflow_wheel.whl"]
# Added a comment to trigger a new GitHub Actions run