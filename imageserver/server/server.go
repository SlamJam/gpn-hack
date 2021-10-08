package server

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/pkg/errors"

	"github.com/SlamJam/gpn-hack/imageserver"
	"github.com/SlamJam/gpn-hack/imageserver/screenshoter"
	"github.com/SlamJam/gpn-hack/imageserver/storage"
)

func New(cfg Config, scr *screenshoter.Screenshoter, s3 *storage.Storage) *Server {
	s := Server{
		cfg: cfg,
		scr: scr,
		s3:  s3,
	}
	s.srv = &http.Server{
		Addr:    cfg.Address,
		Handler: http.HandlerFunc(s.handler),
	}
	return &s
}

type Server struct {
	cfg Config
	srv *http.Server
	scr *screenshoter.Screenshoter
	s3  *storage.Storage
}

type UpdateRequest struct {
	ID    string `json:"id"`
	URL   string `json:"url"`
	Async bool   `json:"async"`
}

func (s *Server) handler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:

		filename := fmt.Sprintf("images/%s", strings.TrimLeft(r.RequestURI, "/"))
		barr, err := s.s3.Get(filename)
		if err != nil {
			// log.Println(errors.Wrapf(err, "cannot get file %q", filename))
			w.Write(imageserver.NotFound)
			return
		}

		if _, err := w.Write(barr); err != nil {
			log.Println(errors.Wrap(err, "cannot copy file to response"))
			return
		}

	case http.MethodPost:

		defer r.Body.Close()

		var request UpdateRequest
		if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
			http.Error(w, "cannot decode request", http.StatusBadRequest)
			return
		}

		if request.Async {
			go s.screenshot(request.ID, request.URL)
			return
		}
		s.screenshot(request.ID, request.URL)

	default:
		http.Error(w, "not implemented", http.StatusNotImplemented)
		return
	}
}

func (s *Server) Start(ctx context.Context) error {
	fmt.Printf("listening %q\n", s.cfg.Address)
	return s.srv.ListenAndServe()
}
