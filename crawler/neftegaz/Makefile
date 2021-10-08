
build:
	@CGO_ENABLED=0 \
	go build \
		--trimpath \
		-o bin/app \
		cmd/main/main.go

run: build
	@bin/app

debug:
	@go run \
		cmd/debug/main.go


docker\:build:
	docker build \
		-t 242617/neftegaz:0.0.1 \
		.

docker\:run:
	docker run \
		-it --rm \
		-v /Users/dmitry/dev/github.com/slamjam/gpn-hack/crawler/neftegaz/data:/etc/service/data \
		242617/neftegaz:0.0.1
	# docker run -d --rm -v `pwd`/data:/etc/service/data 242617/neftegaz:0.0.1
