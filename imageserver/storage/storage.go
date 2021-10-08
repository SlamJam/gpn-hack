package storage

import (
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/pkg/errors"
)

func New(cfg Config) (*Storage, error) {
	sess, err := session.NewSession(&aws.Config{
		Credentials: credentials.NewStaticCredentials(cfg.KeyID, cfg.Secret, ""),
		Endpoint:    aws.String(cfg.Endpoint),
		Region:      aws.String(cfg.Endpoint),
	})
	if err != nil {
		return nil, errors.Wrap(err, "cannot create session")
	}

	// result, err := s.svc.ListBuckets(nil)
	// if err != nil {
	// 	return nil, errors.Wrap(err, "cannot list buckets")
	// }
	// fmt.Println("Buckets:")
	// for _, b := range result.Buckets {
	// 	fmt.Printf("* %s created on %s\n",
	// 		aws.StringValue(b.Name), aws.TimeValue(b.CreationDate))
	// }

	return &Storage{
		cfg: cfg,
		svc: s3.New(sess),
	}, nil
}

type Storage struct {
	cfg Config
	svc *s3.S3
}
