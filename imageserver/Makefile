-include config.env
export

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
		-t imageserver:0.0.1 \
		.

docker\:run:
	docker run \
		-it --rm \
		-v `pwd`/images:/etc/service/images \
		imageserver:0.0.1
