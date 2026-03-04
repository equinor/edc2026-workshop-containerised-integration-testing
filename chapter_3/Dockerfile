FROM python:3.14-slim AS build

WORKDIR /app

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends git
RUN apt-get install -y --no-install-recommends build-essential gcc

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

FROM python:3.14-slim
WORKDIR /app
COPY --from=build /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

EXPOSE 3000

# Add non-root user
RUN useradd --create-home --uid 1000 --shell /bin/bash app
RUN chown -R 1000 /app
RUN chmod 755 /app
USER 1000

#CMD ["tail", "-f", "/dev/null"]
CMD ["start-tickets-api"]
