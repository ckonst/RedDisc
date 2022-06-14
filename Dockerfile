FROM python:3.8.5

# set the working directory for the app
WORKDIR /app

# copy all the files to the container
COPY . .

# install all the dependencies
RUN pip install -r requirements.txt

# run the command
CMD ["python", "./epicbot.py"]
