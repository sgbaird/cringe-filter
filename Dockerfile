# The MCP server over streamable HTTP, for a platform that runs containers
# (Hugging Face Spaces, Cloud Run, Fly.io, Render). It serves /mcp on $PORT,
# or 8000 when the platform sets none. Every tool is stateless and offline,
# so the container needs nothing mounted or configured, and the platform
# can run as many copies as it likes.
#
#   docker build -t cringe-filter-mcp .
#   docker run -p 8000:8000 cringe-filter-mcp
FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY cringe_filter ./cringe_filter
RUN pip install --no-cache-dir '.[mcp]'

# Hugging Face Spaces runs the container as user 1000.
RUN useradd --create-home --uid 1000 user
USER user

EXPOSE 8000
CMD ["cringe-filter", "mcp", "--transport", "streamable-http", "--host", "0.0.0.0"]
