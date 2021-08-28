package server

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/chromedp/chromedp"
	"github.com/pkg/errors"

	"github.com/SlamJam/gpn-hack/imageserver"
)

func New(cfg Config) *Server {
	s := Server{
		cfg: cfg,
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
}

type UpdateRequest struct {
	ID  string `json:"id"`
	URL string `json:"url"`
}

func (s *Server) handler(w http.ResponseWriter, r *http.Request) {

	switch r.Method {
	case http.MethodGet:

		filename := fmt.Sprintf("images/%s", strings.TrimLeft(r.RequestURI, "/"))
		file, err := os.OpenFile(filename, os.O_RDONLY, 0644)
		if err != nil {
			w.Write(imageserver.NotFound)
			return
		}
		defer file.Close()

		if _, err := io.Copy(w, file); err != nil {
			log.Println(errors.Wrap(err, "cannot copy file to response"))
			return
		}

	case http.MethodPost:

		var request UpdateRequest
		if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
			http.Error(w, "cannot decode request", http.StatusBadRequest)
			return
		}

		go func() {
			defer r.Body.Close()

			ctx, cancel := chromedp.NewContext(context.Background(), chromedp.WithErrorf(log.Printf))
			defer cancel()

			var barr []byte
			if err := chromedp.Run(ctx, imageserver.ScreenshotTasks(request.URL, &barr)); err != nil {
				log.Println(errors.Wrap(err, "cannot run chrome task"))
				return
			}

			filename := fmt.Sprintf("images/%s.png", request.ID)
			if err := ioutil.WriteFile(filename, barr, 0644); err != nil {
				log.Println(errors.Wrap(err, "cannot write file"))
				return
			}
		}()

	default:
		http.Error(w, "not implemented", http.StatusNotImplemented)
		return
	}
}

func (s *Server) Start(ctx context.Context) error {
	fmt.Printf("listening %q\n", s.cfg.Address)
	return s.srv.ListenAndServe()
}
