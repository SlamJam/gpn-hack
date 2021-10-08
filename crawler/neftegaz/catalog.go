package neftegaz

import (
	"fmt"

	"github.com/PuerkitoBio/goquery"
	"github.com/pkg/errors"
)

type CatalogItem struct {
	URL   string
	Title string
}

func CrawlCatalogPage(url string) ([]CatalogItem, error) {
	fmt.Printf("crawl catalog page %q\n", url)

	res, err := Request(url)
	if err != nil {
		return nil, errors.Wrapf(err, "cannot get url %q", url)
	}
	defer res.Body.Close()

	doc, err := goquery.NewDocumentFromReader(res.Body)
	if err != nil {
		return nil, errors.Wrap(err, "cannot create new document reader")
	}

	var infos []CatalogItem
	doc.Find(".m-company-table__row").Each(func(_ int, s *goquery.Selection) {
		var info CatalogItem
		info.Title = FixString(s.Find(".m-company-table__name").Text())
		info.URL, _ = s.Find("a[href]").Attr("href")
		if info.URL == "" || info.Title == "" {
			return
		}
		infos = append(infos, info)
	})

	return infos, nil
}
