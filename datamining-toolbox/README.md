[GPN Hack] Object 43 base
-------------------------

Install [Remote - Containers](vscode:extension/ms-vscode-remote.remote-containers) extension.

Build Docker image:

`$ docker build -f docker/Dockerfile .`

Run Luigi scheduler:

`$ docker run <image-name> lud`

Run task:

`$ docker run -v $(pwd)/luigi.cfg:/app/luigi.cfg <image-name> lu <TaskName>`

Example `luigi.cfg`:

```
[core]
# from docker-compose.yml
scheduler_host=scheduler

[s3]
aws_access_key_id=XXXXXXXXXXXXXXXXXXXXXXXX
aws_secret_access_key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
endpoint_url=https://storage.yandexcloud.net
```
