# Production Deployment

The public beta is moving from Streamlit Community Cloud to a Panel app served from a Docker web service. This avoids the demo-host hibernation pattern and gives the project a normal always-on web process.

## Recommended Host: Render Web Service

This repository includes:

- `Dockerfile` for a production Panel container.
- `render.yaml` for a Render Blueprint.
- Health checks against `/` so failed deploys do not replace a healthy running version.

Use a paid always-on Render web service plan. Free plans are useful for testing but are not the fix for an app that needs to stay online.

### Deploy Steps

1. In Render, create a new Blueprint or Web Service from `kobeqanderson-png/NeuroPipe-SABV`.
2. Use the `main` branch.
3. Keep the Docker runtime selected.
4. Keep the health check path as `/`.
5. Use an always-on compute plan such as `0.5c-512mb` or larger.
6. After the first successful deploy, update the README app link to the new `onrender.com` or custom-domain URL.

## Local Container Check

```bash
docker build -t neuropipe-sabv .
docker run --rm -p 5006:5006 neuropipe-sabv
```

Then open `http://localhost:5006`.

## Host Requirements

Any alternative host should provide:

- A persistent web process that does not hibernate after inactivity.
- Python 3.12 or Docker support.
- A configurable HTTP port exposed through the `PORT` environment variable.
- HTTPS for public use.
- Application health checks against `/`.
