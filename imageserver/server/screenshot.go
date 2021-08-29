package server

import (
	"fmt"
	"os"

	"github.com/pkg/errors"
)

func (s *Server) screenshot(id, url string) error {
	barr, err := s.scr.Do(url)
	if err != nil {
		return errors.Wrap(err, "cannot make screenshot")
	}

	filename := fmt.Sprintf("images/%s.png", id)
	if err := os.WriteFile(filename, barr, 0644); err != nil {
		return errors.Wrap(err, "cannot write file")
	}

	return nil
}
