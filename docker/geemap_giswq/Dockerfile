# https://github.com/giswqs/geemap_docker/blob/master/Dockerfile
FROM ubuntu:18.04
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# install dependencies - making some changes here to test 
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends\     
        build-essential \
        software-properties-common \
        python3.8 \
        python3-dev \
        python3-tk \
        python3-pip \
        build-essential \
        libfreetype6-dev \
        libpng-dev \
        libzmq3-dev \
        libspatialindex-dev \
	libgl1-mesa-glx \
        gdal-bin \
        libgdal-dev \
        python3-gdal \
        libsm6 \
        vim \
        wget \
        zip \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update

RUN /usr/bin/python3 -m pip install --upgrade pip

# install python package
RUN pip3 --no-cache-dir install --upgrade setuptools && \
    pip3 --no-cache-dir install wheel && \
    pip3 --no-cache-dir install \
	jupyter \
	jupyterlab \
	numpy --upgrade \
	scipy \
	Pillow \
	matplotlib \
	opencv-contrib-python \
	scikit-image \
	scikit-learn \
	sentinelhub --upgrade \
	sentinelsat \
	folium \
	fiona \
	shapely \
	geopandas \
	rasterio \
	tifffile \
	branca==0.3.1 \
	geemap==0.8.0

# Add additional packages
RUN pip3 --no-cache-dir install \
	pandas --upgrade \
	whitebox --upgrade \
	xarray --upgrade
	
# Making home & test folders
RUN mkdir geemap
RUN mkdir tests

# Copying tests
COPY /tests/test_geemap.py /tests
COPY /tests/run_tests.sh /tests

# Giving permission to tests to run
RUN chmod +x /tests/test_geemap.py
RUN chmod +x /tests/run_tests.sh

RUN apt-get install curl -y
RUN apt-get install apt-transport-https ca-certificates gnupg -y
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update && apt-get install google-cloud-cli -y

WORKDIR "geemap"
CMD ["/bin/bash"]