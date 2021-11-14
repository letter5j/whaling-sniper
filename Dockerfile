FROM python:3.9

WORKDIR /app

RUN adduser worker
RUN chown -R worker:worker /app

USER worker

COPY --chown=worker:worker ./requirements.txt /app/requirements.txt

RUN pip install --user --no-cache-dir --upgrade -r /app/requirements.txt

COPY --chown=worker:worker ./ /app


LABEL maintainer="Hsin <letter5j@pm.me>" \
      version="0.0.1"
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["python", "main.py"]