FROM ubuntu:16.04

MAINTAINER Shantha Kumar <p.shanthakumar@spi-global.com>

ARG username=la_acs_user
ARG userid=10005
ARG deployment_folder=la_acs_deployment
ARG logdir=la_acs_log_dir

RUN echo "building image with username: ${username}, userid: ${userid} and deployment will be present inside ${deployment_folder}"

RUN apt-get update && apt-get install -y --no-install-recommends \
      make \
      bzip2 \
      g++ \
      git \
      graphviz \
      libgl1-mesa-glx \
      libhdf5-dev \
      openmpi-bin \
      vim \
      nano \
      unzip \
      wget && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update
RUN apt-get install -y software-properties-common

#Install Open JDK 8

RUN add-apt-repository -y ppa:openjdk-r/ppa
RUN apt-get update

RUN apt-get -y install openjdk-8-jdk

ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
#ENV PATH $JAVA_HOME/bin:$PATH


# Install miniconda
ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH


RUN wget --quiet --no-check-certificate https://repo.continuum.io/miniconda/Miniconda3-4.2.12-Linux-x86_64.sh && \
    echo "c59b3dd3cad550ac7596e0d599b91e75d88826db132e4146030ef471bb434e9a *Miniconda3-4.2.12-Linux-x86_64.sh" | sha256sum -c - && \
    /bin/bash /Miniconda3-4.2.12-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda3-4.2.12-Linux-x86_64.sh && \
    echo export PATH=$CONDA_DIR/bin:'$PATH' > /etc/profile.d/conda.sh

RUN useradd -u ${userid} -m -s /bin/bash -N ${username}
RUN chown ${username} $CONDA_DIR -R


ARG python_version=3.6
RUN conda install -y python=${python_version}
RUN pip install --upgrade pip

COPY requirements.txt /home/${username}/requirements.txt
RUN pip install -r /home/${username}/requirements.txt
RUN rm /home/${username}/requirements.txt

## install nltk all packages
RUN python -m nltk.downloader punkt

## down and install spacy english
RUN python -m spacy download en

USER ${username}
RUN mkdir /home/${username}/${deployment_folder}

# create a log directory
RUN mkdir /home/${username}/${deployment_folder}/${logdir}

COPY server /home/${username}/${deployment_folder}/server
COPY language_assessment_core /home/${username}/${deployment_folder}/language_assessment_core


ENV PYTHONPATH "${PYTHONPATH}:/home/${username}/${deployment_folder}"
ENV LA_ACS_LOG_DIR "/home/${username}/${deployment_folder}/${logdir}"

WORKDIR /home/${username}/${deployment_folder}/server

EXPOSE 8000 80 443
