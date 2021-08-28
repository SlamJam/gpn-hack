package energybase

import "strings"

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
