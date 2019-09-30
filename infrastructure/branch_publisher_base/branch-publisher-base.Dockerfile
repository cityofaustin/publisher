FROM python:3.7.4-stretch

# Install node
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get update && apt-get install -y nodejs build-essential

# Install yarn
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update && apt-get install yarn

# Install other dependencies
RUN apt-get update && apt-get install -y git

# Install python libraries
RUN pip install awscli==1.16.248 boto3==1.9.238 botocore==1.12.238

# Create directories
RUN mkdir src
RUN mkdir src/cache
WORKDIR /src

# Copy scripts into /src
COPY "./scripts/publish.sh" .
COPY "./scripts/cache_exists.py" .
COPY "./scripts/install_yarn_dependencies.sh" .
