package neftegaz

import (
	"net/http"
	"strings"
	"time"

	"github.com/242617/other/user_agent"
	"github.com/pkg/errors"
)

const RequestDelay = time.Second

func Request(url string) (*http.Response, error) {
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, errors.Wrap(err, "cannot create request")
	}
	req.Header.Set("User-Agent", user_agent.Random())

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, errors.Wrap(err, "cannot make request")
	}

	time.Sleep(RequestDelay)
	return res, err
}

func FixString(str string) string {
	str = strings.Trim(str, " \n\t,")
	for before, after := range map[string]string{
		"\t": " ",
		"\n": " ",
	} {
		str = strings.ReplaceAll(str, before, after)
	}
	for strings.Contains(str, "  ") {
		str = strings.ReplaceAll(str, "  ", " ")
	}
	return str
}

func FixSite(str string) string { return FixString(strings.Trim(str, "/\\")) }
