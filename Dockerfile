FROM heroku/miniconda

# Grab requirements.txt.
ADD requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip install -qr /tmp/requirements.txt

# Add our code
#ADD ./webapp /opt/webapp/
#WORKDIR /opt/webapp

RUN conda install scipy
RUN conda install numpy
RUN conda install pandas
RUN conda install bokeh

CMD gunicorn --bind 0.0.0.0:$PORT wsgi
