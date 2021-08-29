package storage

import (
	"io"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/pkg/errors"
)

func (s *Storage) Get(filename string) ([]byte, error) {
	object := s3.GetObjectInput{
		Bucket: aws.String(s.cfg.BucketName),
		Key:    aws.String(filename),
	}
	out, err := s.svc.GetObject(&object)
	if err != nil {
		return nil, errors.Wrapf(err, "cannot get object %q", filename)
	}
	defer out.Body.Close()

	barr, err := io.ReadAll(out.Body)
	if err != nil {
		return nil, errors.Wrap(err, "cannot read body")
	}

	return barr, nil
}
