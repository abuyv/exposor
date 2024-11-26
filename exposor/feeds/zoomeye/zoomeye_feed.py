import requests
import json
import logging


class Zoomeye:
    def auth(zoomeye_api_key):
        try:
            url = "https://api.zoomeye.hk/resources-info"
            # this service not aviliable in your area, please use api.zoomeye.org instead'
            # use following urls for the api calls
            url_org = "https://api.zoomeye.org/resources-info"
            url_hk = "https://api.zoomeye.hk/resources-info"

            headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "API-KEY": zoomeye_api_key
            }

            response = requests.get(url, headers=headers)
            logging.debug(f"Zoomeye response body: {response.json()}")
            response_text = response.content.decode('utf-8')
            response_json = json.loads(response_text)

            if "login_required" in response_json.values():
                return False
            else:
                logging.info("Authentication successful for zoomeye")
                credits = response.json()['quota_info']['remain_total_quota']
                logging.info(f"Zoomeye - remaining credits: {credits}")
                return True

        except Exception as e:
            logging.error(str(e))
            return False

    def search(key, queries, args, technology):
        results = []
        page = 0
        limit_result = args.limit
        query_limit = args.query_limit
        country_code = args.country
        net = args.netblock
        domain_name = args.domain_name

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "API-KEY": key
            }

        try:
            for q in queries:
                if net:
                    q = f"cidr:\"{net}\" %2B{q}"

                if country_code:
                    q = f"{q} %2Bcountry:\"{country_code}\""

                if domain_name:
                    q = f"{q} %2Bhostname:\"{domain_name}\""

                page = 1
                counter = 0

                while counter < int(limit_result):
                    params = {'query': q, 'page': page}

                    url = f"https://api.zoomeye.hk/web/search?query={q}&page={page}"
                    # url = "https://api.zoomeye.hk/web/search"

                    response = requests.get(url, headers=headers)

                    if response.status_code != 200:
                        logging.debug(f"Zoomeye - request failed with status code: {response.status_code}")
                        break

                    banners = response.json()
                    total_tech = banners.get('total', 0)
                    logging.debug(f"Zoomeye - total result: {total_tech} for query: {q}")

                    if total_tech == 0:
                        break

                    matches = banners.get('matches', [])
                    remaining = int(limit_result) - counter
                    matches_to_add = matches[:remaining]
                    for banner in matches_to_add:
                        ip_addresses = banner.get('ip', [])
                        if not ip_addresses:
                            counter+=1
                        for ip in ip_addresses:                            
                            if counter > int(limit_result):
                                break
                            counter+=1
                            banner_dic = {
                                'ip': ip,
                                'domain': banner.get('site', None),
                                'port': banner.get('portinfo', {}).get('port', None),
                                'country': banner.get('geoinfo', {}).get('country', {}).get('code', None),
                                'technology': technology,
                                'feed': 'zoomeye',
                                'timestamp': banner.get('timestamp', None)
                            }
                            results.append(banner_dic)
                    page += 1

                if query_limit.lower() == "yes":
                    break
            return results
        except Exception as e:
            logging.error(f"ERROR zoomeye search {e}")

        return results
