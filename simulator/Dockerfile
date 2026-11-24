FROM python:3.13-alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY simulator.py .
USER 65534
EXPOSE 8080
CMD ["python", "simulator.py"]
