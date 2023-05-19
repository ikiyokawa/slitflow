FROM gitpod/workspace-python-3.10
USER gitpod

RUN sudo apt update
RUN sudo apt-get update && sudo apt-get upgrade -y
RUN sudo echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | sudo debconf-set-selections \
  && sudo apt-get install -y --no-install-recommends ttf-mscorefonts-installer
RUN sudo apt-get install libgl1-mesa-dev -y
RUN pip install --upgrade pip
RUN pip install slitflow[full] git+https://gitlab.com/yumaitou/Spot-On-cli.git@py310