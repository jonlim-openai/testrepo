# testrepo

Minimal example consisting of a small FastAPI service (`backend.py`)
that mints an `EPHEMERAL_KEY` for the OpenAI realtime WebRTC API and a
matching Streamlit app (`app.py`) that demonstrates the browser
interaction.

## Quick start

1. **Install the dependencies**  
   The backend only depends on `fastapi`, `uvicorn` and `openai` while
   the app relies on `streamlit`:

   ```bash
   pip install fastapi uvicorn streamlit openai
   ```

2. **Set up your credentials**  
   The backend will refuse to start unless the environment variable
   `OPENAI_API_KEY` is defined:

   ```bash
   export OPENAI_API_KEY="sk-..."  # replace with your key
   ```

3. **Run the backend**  
   In one shell run:

   ```bash
   uvicorn backend:app --host 0.0.0.0 --port 8000
   ```

4. **Run the Streamlit frontend**  
   In another terminal execute:

   ```bash
   streamlit run app.py --server.port 8501
   ```

   The demo page becomes available at <http://localhost:8501> and will
   internally call `http://localhost:8000/session` when the "Connect &
   Talk" button is pressed.

### Testing

Basic syntax check for both python files:

```bash
python3 -m py_compile backend.py app.py
```

To ensure the backend is reachable, start it as shown above and try to
fetch a session:

```bash
curl http://localhost:8000/session
```

This should return a JSON document containing a `client_secret`.  When
running in restricted environments the call may fail with *Realtime
token request failed* if the `openai` library lacks realtime
functionality or the outgoing connection is blocked.

## Ideas for further improvements

- Provide a `requirements.txt` or `pyproject.toml` to make the
  dependency versions explicit.  This also allows for `pip
  install -r requirements.txt` style bootstrapping.
- Automatically read configuration from a `.env` file using
  `python-dotenv` to avoid the need for external environment variables.
- Add input validation and better error reporting in `create_session`
  so it becomes obvious whether the OpenAI request failed due to
  network restrictions or missing API capabilities.
- Ship a `Dockerfile` and `docker-compose.yml` for reproducible local
  runs (especially handy when the local python environment is missing
  some requirements).
- Include unit tests for the FastAPI route and a simple smoke test for
  the Streamlit component to facilitate regression testing.
- Lint/format the project via tools such as `flake8`, `pylint`, or
  `black` to keep the code quality high (CI integration would help
  automate this.)
- Expose the service on a configurable host/port instead of fixed
  values to simplify embedding into other systems.
