package main

import (
	"context"
	"log"
	"os"
	"time"

	"github.com/SlamJam/gpn-hack/imageserver/screenshoter"
	"github.com/SlamJam/gpn-hack/imageserver/server"
)

func init() { log.SetFlags(log.Lshortfile) }
func main() {
	ctx := context.TODO()

	delay, err := time.ParseDuration(os.Getenv("LOAD_PAGE_TIMEOUT"))
	if err != nil {
		log.Fatal(err)
	}
	scr := screenshoter.New(screenshoter.Config{Delay: delay})

	srv := server.New(server.Config{Address: os.Getenv("HTTP_ADDRESS")}, scr)
	if err := srv.Start(ctx); err != nil {
		log.Fatal(err)
	}
}
