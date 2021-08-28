import logging
import math
import re
import sys

import bs4
import httpx
import purl
import tenacity
import trio

_JUNK_SYMBOLS_IN_DESC_RE = re.compile("([\r\n\xa0]+)")

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

logger = logging.getLogger(__name__)


retry = tenacity.retry(
    wait=(
        tenacity.wait_random_exponential(multiplier=0.1, max=10)
        # tenacity.wait_exponential(multiplier=1, min=4, max=10)
        # + tenacity.wait_random(0, 2)
    ),
    sleep=trio.sleep,
    # after=tenacity.after_log(logger, logging.DEBUG),
    # stop=tenacity.stop_after_attempt(3),
    before_sleep=tenacity.before_sleep_log(logger, logging.DEBUG),
)


# def get_industries():
#     with httpx.Client() as client:
#         r = client.get("https://api.hh.ru/industries")
#     r.raise_for_status()

#     return r.json()


@retry
async def get_company(client, company_id):
    r = await client.get(f"https://api.hh.ru/employers/{company_id}")
    r.raise_for_status()

    return r.json()


@retry
async def get_url(client, url):
    r = await client.get(url)
    r.raise_for_status()

    return r.text


def build_absolute_url_regard_to(relative, base):
    relative = purl.URL(relative)
    base = purl.URL(base)

    return base.path(relative.path()).query(relative.query())


def select_companies_from_sub_industries_page(soup):
    for element in soup.select(
        "div.employers-company__list_companies div.employers-company__item a"
    ):
        href = element.get("href")
        p_href = purl.URL(href)

        # company id at second path segment
        yield p_href.path_segment(1)


async def company_resolver(client, task_channel, result_channel):
    async with result_channel:
        async for company_id in task_channel:
            resp = await get_company(client, company_id)
            await result_channel.send(resp)


@retry
async def get_contries(client):
    r = await client.get("https://api.hh.ru/areas/countries")
    r.raise_for_status()

    return r.json()


async def sub_industries_parser(
    client, url, nursery, limit, companies_send_channel, pages_send_channel
):

    global sub_industries

    async with limit, companies_send_channel, pages_send_channel:
        data = await get_url(client, url)
        base_url = purl.URL(url)

        soup = bs4.BeautifulSoup(data, "html.parser")
        for element in soup.find_all("a", class_="employers-sub-industries__item"):
            href = element.get("href")
            link = build_absolute_url_regard_to(href, base_url)

            nursery.start_soon(
                sub_industries_parser,
                client,
                link.as_string(),
                nursery,
                limit,
                companies_send_channel.clone(),
                pages_send_channel.clone(),
            )

        await companies_send_channel.send(
            list(select_companies_from_sub_industries_page(soup))
        )

        pages = soup.select('div[data-qa="pager-block"] a[data-qa="pager-page"]')
        if pages:
            values = [int(p["data-page"]) for p in pages]
            max_page = max(values)

            for page in range(1, max_page + 1):
                link = base_url.query_param("page", page)
                await pages_send_channel.send(link.as_string())


async def sub_industries_page_parser(
    client, pages_receive_channel, companies_send_channel
):
    async with companies_send_channel:
        async for url in pages_receive_channel:
            data = await get_url(client, url)
            soup = bs4.BeautifulSoup(data, "html.parser")

            await companies_send_channel.send(
                list(select_companies_from_sub_industries_page(soup))
            )


async def collect_companies_ids_with_parsing(
    area_id, *, max_page_parsers=80, max_sub_industries_parsers=40
):
    """Собирает ID компаний путём парсинга страницы с компаниями в регионе area_id"""

    pages_send_channel, pages_receive_channel = trio.open_memory_channel(math.inf)
    companies_send_channel, companies_receive_channel = trio.open_memory_channel(
        math.inf
    )
    sub_industries_limit = trio.CapacityLimiter(max_sub_industries_parsers)

    async with httpx.AsyncClient() as client, trio.open_nursery() as nursery:
        url = purl.URL("https://hh.ru/employers_company")
        url = url.query_param("area", area_id).as_string()

        data = await get_url(client, url)
        base_url = purl.URL(url)

        soup = bs4.BeautifulSoup(data, "html.parser")

        with pages_send_channel, companies_send_channel:
            for element in soup.find_all("a", class_="employers-company__item"):
                href = element.get("href")
                link = build_absolute_url_regard_to(href, base_url)

                nursery.start_soon(
                    sub_industries_parser,
                    client,
                    link.as_string(),
                    nursery,
                    sub_industries_limit,
                    companies_send_channel.clone(),
                    pages_send_channel.clone(),
                )

            # парсеры, гуляющие по page'ам раздела (индустрии)
            for _ in range(max_page_parsers):
                nursery.start_soon(
                    sub_industries_page_parser,
                    client,
                    pages_receive_channel,
                    companies_send_channel.clone(),
                )

    companies_ids = set()
    async for batch in companies_receive_channel:
        companies_ids.update(batch)

    return companies_ids


async def resolve_companies_info(company_ids):
    companies_send_channel, companies_receive_channel = trio.open_memory_channel(
        math.inf
    )
    result_send_channel, result_receive_channel = trio.open_memory_channel(math.inf)

    max_company_resolvers = 200

    async with httpx.AsyncClient() as client, trio.open_nursery() as nursery:
        with result_send_channel:
            for _ in range(max_company_resolvers):
                nursery.start_soon(
                    company_resolver,
                    client,
                    companies_receive_channel,
                    result_send_channel.clone(),
                )

        with companies_send_channel:
            for company_id in company_ids:
                await companies_send_channel.send(company_id)

        companies = []
        async for company in result_receive_channel:
            companies.append(company)

    return companies


def strip_tags_in_description(company):
    def clean(s):
        def decode_match(match):
            return " "

        return _JUNK_SYMBOLS_IN_DESC_RE.sub(decode_match, s).strip()

    c = company.copy()
    desc = c["description"]

    if not desc:
        return c

    soup = bs4.BeautifulSoup(desc, "html.parser")
    c["description"] = clean(soup.get_text())

    return c
