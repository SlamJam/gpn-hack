package server

import (
	"fmt"

	"github.com/pkg/errors"
)

func (s *Server) screenshot(id, url string) error {
	barr, err := s.scr.Do(url)
	if err != nil {
		return errors.Wrap(err, "cannot make screenshot")
	}

	filename := fmt.Sprintf("images/%s.png", id)
	if err := s.s3.Upload(filename, barr); err != nil {
		return errors.Wrapf(err, "cannot upload file with %q", id)
	}

	return nil
}
