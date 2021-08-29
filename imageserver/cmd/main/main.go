package main

import (
	"context"
	"log"
	"os"
	"time"

	"github.com/SlamJam/gpn-hack/imageserver/screenshoter"
	"github.com/SlamJam/gpn-hack/imageserver/server"
	"github.com/SlamJam/gpn-hack/imageserver/storage"
)

func init() { log.SetFlags(log.Lshortfile) }
func main() {
	delay, err := time.ParseDuration(os.Getenv("LOAD_PAGE_TIMEOUT"))
	if err != nil {
		log.Fatal(err)
	}
	scr := screenshoter.New(screenshoter.Config{Delay: delay})

	s3, err := storage.New(storage.Config{
		Endpoint:   os.Getenv("S3_ENDPOINT"),
		KeyID:      os.Getenv("S3_KEY_ID"),
		Secret:     os.Getenv("S3_SECRET"),
		BucketName: os.Getenv("S3_BUCKET_NAME"),
	})
	if err != nil {
		log.Fatal(err)
	}

	srv := server.New(server.Config{Address: os.Getenv("HTTP_ADDRESS")}, scr, s3)
	if err := srv.Start(context.TODO()); err != nil {
		log.Fatal(err)
	}
}
