[GPN Hack] Object 43 base
-------------------------

Install [Remote - Containers](vscode:extension/ms-vscode-remote.remote-containers) extension.

Build Docker image:

`$ docker build -f docker/Dockerfile .`

Run Luigi scheduler:

`$ docker run <image-name> lud`

Run task:

`$ docker run -v $(pwd)/luigi.cfg:/app/luigi.cfg <image-name> lu <TaskName>`

See `luigi.cfg.sample`.
