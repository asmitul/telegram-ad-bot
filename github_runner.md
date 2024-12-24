docker run -d \
  --name g-r-ad-bot \
  --restart always \
  -e RUNNER_NAME=g-r-ad-bot \
  -e RUNNER_WORKDIR=/tmp/g-r-ad-bot \
  -e RUNNER_GROUP=Default \
  -e RUNNER_TOKEN=ABPLEL6ZSAOTPJNIK5CW4ATHNKNGS \
  -e REPO_URL=https://github.com/asmitul/telegram-ad-bot \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --cpus="0.3" \
  myoung34/github-runner:latest