FROM alpine:3.1

# Update
RUN apk add --update python py-pip

# Install app dependencies
RUN pip install Flask redis

# Bundle app source
COPY sub_app.py /src/sub_app.py

CMD ["python", "/src/sub_app.py"]
