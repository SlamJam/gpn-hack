FROM golang:1.17.0-alpine3.14 AS builder

RUN apk add --update make

WORKDIR /build
ADD . .
RUN make build

FROM alpine:3.14.1

RUN apk --no-cache add ca-certificates curl
COPY --from=builder /build/bin/app /etc/service/app

STOPSIGNAL 15
HEALTHCHECK --interval=5m --timeout=5s CMD curl -f http://127.0.0.1:8080/health-check || exit 1
EXPOSE 8080/tcp

WORKDIR /etc/service
CMD /etc/service/app
