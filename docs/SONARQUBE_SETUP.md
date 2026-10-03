# SonarQube setup for FleetOps

This project uses SonarCloud by default in GitHub Actions, but the same setup works with a self-hosted SonarQube instance.

## 1. Create the SonarQube project

1. Sign in to SonarCloud or your SonarQube server.
2. Create a project for this repository.
3. Copy the project key.

For this repository, the default project key is:

```text
fleetops
```

## 2. Generate a token

1. Open your user profile.
2. Go to Security.
3. Generate a new token.
4. Copy the token value.

This token must be stored as a GitHub repository secret named:

```text
SONAR_TOKEN
```

## 3. Add GitHub repository variables

In GitHub:

- Go to Settings
- Open Secrets and variables
- Open Actions
- Select the Variables tab

Add these values:

```text
SONAR_PROJECT_KEY = fleetops
SONAR_HOST_URL = https://sonarcloud.io
```

If you use a self-hosted SonarQube server, replace the host with your server URL instead of SonarCloud.

## 4. What the workflow uses

The GitHub Actions workflow calls SonarQube with these values:

- `SONAR_TOKEN` from GitHub secrets
- `SONAR_PROJECT_KEY` from GitHub variables
- `SONAR_HOST_URL` from GitHub variables

The repo workflow also supports the older variable name `SONAR_URL` as a fallback for compatibility.

## 5. Trigger the analysis

After the values are saved, push a commit or trigger the workflow manually from GitHub Actions.

The SonarQube job runs automatically when `SONAR_TOKEN` exists.

## 6. Troubleshooting

If the job does not run:

- make sure the secret name is exactly `SONAR_TOKEN`
- make sure the variable name is exactly `SONAR_PROJECT_KEY`
- make sure the variable name is exactly `SONAR_HOST_URL`
- confirm the project key matches the project created in SonarCloud or SonarQube

If the project key is wrong, SonarQube will reject the upload or create a new project instead of updating the expected one.
