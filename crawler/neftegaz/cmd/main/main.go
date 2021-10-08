package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/pkg/errors"

	"github.com/SlamJam/gpn-hack/crawler/neftegaz"
)

const URLTemplate = "https://market.neftegaz.ru/catalog/company/%d"

func init() { log.SetFlags(log.Lshortfile) }
func main() {
	okCh := make(chan struct{})
	infosCh := make(chan neftegaz.CatalogItem)

	go func() {
		for info := range infosCh {
			info := info
			company, err := neftegaz.CrawlCompanyPage(info.URL)
			if err != nil {
				log.Println("err", errors.Wrap(err, "cannot crawl company page"))
				continue
			}
			if err := neftegaz.DumpCompany(*company); err != nil {
				log.Println("err", errors.Wrap(err, "cannot dump company"))
				continue
			}
		}
		okCh <- struct{}{}
	}()

	for i := 1; i < 1602; i++ {
		url := fmt.Sprintf(URLTemplate, i)
		companies, err := neftegaz.CrawlCatalogPage(url)
		if err != nil {
			log.Println("err", errors.Wrapf(err, "cannot crawl catalog page %q", url))
			continue
		}
		for _, company := range companies {
			infosCh <- company
		}
	}
	close(infosCh)

	quitCh := make(chan os.Signal, 1)
	signal.Notify(quitCh, os.Interrupt, syscall.SIGINT, syscall.SIGTERM)
	select {
	case <-quitCh:
		fmt.Println("quit")
	case <-okCh:
		fmt.Println("done")
	}
}
