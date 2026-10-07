# Production Deployment

The public beta currently runs on Streamlit Community Cloud, which can hibernate inactive apps. For a steadier public endpoint, deploy NeuroPipe-SABV as a Docker web service on Render or another container host.

## Recommended Host: Render Web Service

This repository includes:

- `Dockerfile` for a production Streamlit container.
- `render.yaml` for a Render Blueprint.
- `/_stcore/health` health checks so failed deploys do not replace a healthy running version.

Use a paid always-on Render web service plan. Free plans are useful for testing but are not the fix for an app that needs to stay online.

### Deploy Steps

1. In Render, create a new Blueprint or Web Service from `kobeqanderson-png/NeuroPipe-SABV`.
2. Use the `main` branch.
3. Keep the Docker runtime selected.
4. Keep the health check path as `/_stcore/health`.
5. Use an always-on compute plan such as `0.5c-512mb` or larger.
6. After the first successful deploy, update the README app link to the new `onrender.com` or custom-domain URL.

## Local Container Check

```bash
docker build -t neuropipe-sabv .
docker run --rm -p 8501:8501 neuropipe-sabv
```

Then open `http://localhost:8501`.

## Host Requirements

Any alternative host should provide:

- A persistent web process that does not hibernate after inactivity.
- Python 3.12 or Docker support.
- A configurable HTTP port exposed through the `PORT` environment variable.
- HTTPS for public use.
- Application health checks against `/_stcore/health`.

