package storage

import (
	"bytes"

	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/pkg/errors"
)

func (s *Storage) Upload(filename string, barr []byte) error {
	object := &s3.PutObjectInput{
		Body:   bytes.NewReader(barr),
		Bucket: &s.cfg.BucketName,
		Key:    &filename,
	}
	_, err := s.svc.PutObject(object)
	if err != nil {
		return errors.Wrapf(err, "cannot put object %q", filename)
	}

	return nil
}
