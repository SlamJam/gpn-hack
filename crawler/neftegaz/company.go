package neftegaz

import (
	"encoding/json"
	"fmt"
	"hash/fnv"
	"os"
	"regexp"
	"strings"

	"github.com/PuerkitoBio/goquery"
	"github.com/pkg/errors"
)

var logoStyleRE = regexp.MustCompile(`background-image: url\((.*)\)`)

const LogoTemplate = "https://market.neftegaz.ru%s"

type Company struct {
	Name       string   `json:"name"`
	Labels     []string `json:"labels"`
	Logo       string   `json:"logo"`
	Geo        string   `json:"geo"`
	Attributes struct {
		PostalAddress string `json:"postal_address"`
		Phone         string `json:"phone"`
		Email         string `json:"email"`
		Site          string `json:"site"`
		INN           string `json:"inn"`
	} `json:"attributes"`
}

func CrawlCompanyPage(url string) (*Company, error) {
	fmt.Printf("crawl company page %q\n", url)

	req, err := Request(url)
	if err != nil {
		return nil, errors.Wrapf(err, "cannot get url %q", url)
	}
	defer req.Body.Close()

	doc, err := goquery.NewDocumentFromReader(req.Body)
	if err != nil {
		return nil, errors.Wrap(err, "cannot create new document reader")
	}

	var company Company
	company.Name = FixString(doc.Find(".m-company-info__head-title span").Text())
	logoStyle, _ := doc.Find(".m-company-info__head-img").Attr("style")
	company.Logo = ExtractLogo(logoStyle)
	doc.Find(".m-company-info__contacts-title a").Each(func(_ int, s *goquery.Selection) {
		company.Labels = append(company.Labels, FixString(s.Text()))
	})
	company.Geo = FixString(doc.Find(".m-company-info__geo").Text())
	doc.Find(".m-company-info__contacts-table-row").Each(func(_ int, s *goquery.Selection) {

		s.Find(".m-company-info__contacts-table-cell").EachWithBreak(func(_ int, s *goquery.Selection) bool {

			title := strings.ToLower(s.Text())
			switch {
			case strings.Contains(title, "почтовый адрес"):
				company.Attributes.PostalAddress = FixString(s.Next().Text())
			case strings.Contains(title, "телефон"):
				company.Attributes.Phone = FixString(s.Next().Text())
			case strings.Contains(title, "e-mail"):
				company.Attributes.Email = FixString(s.Next().Text())
			case strings.Contains(title, "сайт"):
				company.Attributes.Site = FixSite(s.Next().Text())
			case strings.Contains(title, "инн"):
				company.Attributes.INN = FixString(s.Next().Text())
			}

			return false
		})
	})

	return &company, nil
}

func DumpCompany(company Company) error {
	fmt.Printf("dump company %q\n", company.Name)

	h := fnv.New64()
	h.Write([]byte(company.Name))

	filename := fmt.Sprintf("data/%d.json", h.Sum64())
	file, err := os.OpenFile(filename, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return errors.Wrap(err, "cannot open file")
	}
	defer file.Close()

	if err := json.NewEncoder(file).Encode(&company); err != nil {
		return errors.Wrap(err, "cannot encode company")
	}

	return nil
}

func ExtractLogo(style string) string {
	submatch := logoStyleRE.FindStringSubmatch(style)
	if len(submatch) > 1 {
		return fmt.Sprintf(LogoTemplate, submatch[1])
	}
	return ""
}
