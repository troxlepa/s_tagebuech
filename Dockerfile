FROM python:3.10

# Create app directory
WORKDIR /app

# Install app dependencies
COPY requirements.txt ./

ENV PYTHONUNBUFFERED 1
RUN apt -y update && apt -y upgrade && apt -y install libvips libgl1

RUN apt -y install intltool imagemagick libmagickcore-dev pstoedit libpstoedit-dev
RUN apt-get -y install autoconf autogen autopoint
RUN git clone https://github.com/autotrace/autotrace.git
WORKDIR /app/autotrace
#unnecessary command for clarification should bugs be introduced later
RUN git rev-parse HEAD
#6468859336870a663106d8179578867caf2cfced

RUN /app/autotrace/autogen.sh
#put everything into /usr/{bin,lib,share,include}
RUN LD_LIBRARY_PATH=/usr/local/lib ./configure --prefix=/usr
RUN make
RUN make install

WORKDIR /app

RUN pip3 install -r requirements.txt

# Bundle app source
COPY . .

EXPOSE 7007
CMD [ "flask", "run","--host","0.0.0.0","--port","7007"]