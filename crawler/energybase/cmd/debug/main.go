package main

import "log"

func init() { log.SetFlags(log.Lshortfile) }
func main() {
	// str := "background-image: url(/upload/resize_cache/webp/upload/iblock/9f1/2ox0aiu86w1z4l2wl93dd4ltgsw14ihb/TS.webp)"
	// log.Println(re.FindStringSubmatch(str))
	// return

	// file, err := os.OpenFile("company.html", os.O_RDONLY, 0644)
	// if err != nil {
	// 	log.Fatal(err)
	// }

	// doc, err := goquery.NewDocumentFromReader(file)
	// if err != nil {
	// 	log.Fatal(err)
	// }

	// var company energybase.Company
	// company.Name = energybase.FixString(doc.Find(".m-company-info__head-title span").Text())
	// logoStyle, _ := doc.Find(".m-company-info__head-img").Attr("style")
	// company.Logo = energybase.ExtractLogo(logoStyle)
	// doc.Find(".m-company-info__contacts-title a").Each(func(_ int, s *goquery.Selection) {
	// 	company.Labels = append(company.Labels, energybase.FixString(s.Text()))
	// })
	// company.Geo = energybase.FixString(doc.Find(".m-company-info__geo").Text())
	// doc.Find(".m-company-info__contacts-table-row").Each(func(_ int, s *goquery.Selection) {

	// 	s.Find(".m-company-info__contacts-table-cell").EachWithBreak(func(_ int, s *goquery.Selection) bool {

	// 		title := strings.ToLower(s.Text())
	// 		switch {
	// 		case strings.Contains(title, "почтовый адрес"):
	// 			company.Attributes.PostalAddress = energybase.FixString(s.Next().Text())
	// 		case strings.Contains(title, "телефон"):
	// 			company.Attributes.Phone = energybase.FixString(s.Next().Text())
	// 		case strings.Contains(title, "e-mail"):
	// 			company.Attributes.Email = energybase.FixString(s.Next().Text())
	// 		case strings.Contains(title, "сайт"):
	// 			company.Attributes.Site = energybase.FixSite(s.Next().Text())
	// 		case strings.Contains(title, "инн"):
	// 			company.Attributes.INN = energybase.FixString(s.Next().Text())
	// 		}

	// 		return false
	// 	})
	// })

	// json.NewEncoder(os.Stdout).Encode(&company)
}
