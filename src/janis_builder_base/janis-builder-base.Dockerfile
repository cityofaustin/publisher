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

# Create directories
RUN mkdir src
RUN mkdir src/cache
WORKDIR /src

# Copy scripts into /src
COPY "./scripts/publish.sh" .
COPY "./scripts/cache_exists.py" .
COPY "./scripts/install_yarn_dependencies.sh" .
COPY "./scripts/hello.html" .


# Install python libraries
COPY "./requirements.txt" .
RUN pip install -r requirements.txt
