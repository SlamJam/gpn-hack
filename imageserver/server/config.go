package server

import "time"

type Config struct {
	Address         string
	LoadPageTimeout time.Duration
}
