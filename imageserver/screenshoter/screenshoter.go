package screenshoter

import (
	"bytes"
	"context"
	_ "embed"
	"image/png"
	"log"
	"time"

	"github.com/chromedp/cdproto/page"
	"github.com/chromedp/chromedp"
	"github.com/nfnt/resize"
	"github.com/pkg/errors"
)

func New(cfg Config) *Screenshoter {
	return &Screenshoter{
		cfg: cfg,
	}
}

type Screenshoter struct {
	cfg Config
}

func (s *Screenshoter) Do(url string) ([]byte, error) {
	ctx, cancel := chromedp.NewContext(context.Background(), chromedp.WithErrorf(log.Printf))
	defer cancel()

	var barr []byte
	if err := chromedp.Run(ctx, s.tasks(url, &barr)); err != nil {
		return nil, errors.Wrap(err, "cannot run chrome task")
	}

	img, err := png.Decode(bytes.NewBuffer(barr))
	if err != nil {
		return nil, errors.Wrap(err, "cannot decode image")
	}
	m := resize.Resize(320, 0, img, resize.Lanczos3)

	var buf bytes.Buffer
	if err := png.Encode(&buf, m); err != nil {
		return nil, errors.Wrap(err, "cannot encode image")
	}

	return buf.Bytes(), nil
}

func (s *Screenshoter) tasks(url string, barr *[]byte) chromedp.Tasks {
	return chromedp.Tasks{
		chromedp.Navigate(url),
		chromedp.ActionFunc(func(ctx context.Context) error {
			time.Sleep(s.cfg.Delay)
			return nil
		}),
		chromedp.ActionFunc(func(ctx context.Context) error {
			var err error
			*barr, err = page.CaptureScreenshot().WithQuality(90).Do(ctx)
			return err
		}),
	}
}
