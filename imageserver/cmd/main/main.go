package main

import (
	"context"
	"log"

	"github.com/SlamJam/gpn-hack/imageserver/server"
)

func init() { log.SetFlags(log.Lshortfile) }
func main() {
	ctx := context.TODO()
	srv := server.New(server.Config{Address: "0.0.0.0:8081"})
	if err := srv.Start(ctx); err != nil {
		log.Fatal(err)
	}
}
