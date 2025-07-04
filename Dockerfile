FROM armswdev/tensorflow-arm-neoverse:latest

# No need to install Bazel or compile TensorFlow from source
# TensorFlow for ARM is already included in the base image.

# Keep Python dependencies for any custom scripts or future needs
RUN pip3 install numpy wheel keras_applications keras_preprocessing

# You can add your custom TensorFlow-related code here
# For example, if you have a Python script that uses TensorFlow:
# COPY your_script.py /app/your_script.py
# WORKDIR /app
# CMD ["python3", "your_script.py"]

# This CMD is just for verification, you can change it to your application's entry point
CMD ["python3", "-c", "import tensorflow as tf; print(tf.__version__)"]
