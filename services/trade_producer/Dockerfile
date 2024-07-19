#The base layer of the docker file is the official python image
# FROM specifies the base image for the Docker image being built.
# The base image is derived from the official Python image repository.
# python: This indicates that the image is from the official Python repository on Docker Hub.
# 3.10.3: This specifies the version of Python to be used, ensuring consistency and compatibility.
# slim: This is a variant of the image that includes only the essential components, making it smaller in size.
# buster: This refers to the Debian Buster distribution, providing a stable and secure Linux base.
FROM python:3.10-slim-buster 

#Stream output to the console
# ENV is used to set environment variables in the container.
# PYTHONUNBUFFERED: This environment variable is set to 1 to ensure that the output from Python is not buffered, allowing it to be streamed to the console.
ENV PYTHONUNBUFFERED=1

#Installing Poetry
# RUN is used to execute commands during the build process.
RUN pip install poetry==1.8.3

#Setting the working directory
WORKDIR /app 
 
#Copying the pyproject.toml file to the container
COPY pyproject.toml /app/

#Installing dependencies from pyproject.toml
# RUN poetry install is used to install the dependencies specified in the pyproject.toml file.
RUN poetry install

#Copying our local code to the container
# COPY is used to copy files from the local file system to the container.
COPY . /app/

#Running the service
# CMD is used to specify the command that should be executed when the container is started.
CMD ["poetry", "run", "python", "src/main.py"]