FROM jupyter/minimal-notebook
ARG MY-PROJECT-NAME
ADD ./requirements.txt .
RUN apt install gcc
RUN pip3 -q install pip --upgrade
RUN pip install --upgrade pip

RUN pip install -r requirements.txt
RUN pip install dvc
RUN git config --global --add safe.directory /workspaces/${MY-PROJECT-NAME}