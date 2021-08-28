package main

import (
	"fmt"
	"log"

	"github.com/pkg/errors"

	"github.com/SlamJam/gpn-hack/crawler/energybase"
)

const URLTemplate = "https://market.neftegaz.ru/catalog/company/%d"

func init() { log.SetFlags(log.Lshortfile) }
func main() {
	okCh := make(chan struct{})
	infocsCh := make(chan energybase.CatalogItem)

	go func() {
		for info := range infocsCh {
			info := info
			company, err := energybase.CrawlCompanyPage(info.URL)
			if err != nil {
				log.Println("err", errors.Wrap(err, "cannot crawl company page"))
				continue
			}
			if err := energybase.DumpCompany(*company); err != nil {
				log.Println("err", errors.Wrap(err, "cannot dump company"))
				continue
			}
		}
		okCh <- struct{}{}
	}()

	for i := 1; i < 1602; i++ {
		url := fmt.Sprintf(URLTemplate, i)
		companies, err := energybase.CrawlCatalogPage(url)
		if err != nil {
			log.Println("err", errors.Wrapf(err, "cannot crawl catalog page %q", url))
			continue
		}
		for _, company := range companies {
			infocsCh <- company
		}
	}
	close(infocsCh)

	<-okCh
	fmt.Println("ok")
}
