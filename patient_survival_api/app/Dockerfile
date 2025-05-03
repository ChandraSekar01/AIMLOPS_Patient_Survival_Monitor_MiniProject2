FROM python:3.11.12-slim
WORKDIR /app
COPY . /app
COPY model /app/model
RUN pip install --no-cache-dir -r app/requirements.txt
EXPOSE 8002
# (Optional) List files in /app/model to verify files were copied
RUN echo "Listing files in /app/model:" && ls -l /app/model
# (Optional) List files in the working directory
RUN echo "Listing files in /app:" && ls -l /app
# ENV FLASK_APP=flower_prediction_api
CMD ["python", "app/main.py"]