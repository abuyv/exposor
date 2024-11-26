import logging
import requests

class Shodan:
    def auth(key):
        try:
            response = requests.get("https://api.shodan.io/api-info?key={0}".format(key))
            if response.status_code != 200:
                return False
            else:
                logging.debug(f"Shodan response body: {response.content.decode('utf-8')}")
                logging.info("Authentication successful for shodan")
                credits = response.json()['query_credits']
                logging.info(f"Shodan - remaining credits: {credits}")
                return True
        except Exception as e:
            logging.error(str(e))
            return False

    def search(key, queries, args, technology):
        limit_result = args.limit
        query_limit = args.query_limit
        country_code = args.country
        net = args.netblock
        domain_name = args.domain_name
        results = []
        page = 0
        try:
            for q in queries:
                if country_code:
                    q = f"{q} country:{country_code}"
                if net:
                    q = f"{q} net:{net}"
                if domain_name:
                    q = f"{q} hostname:{domain_name}"

                page = 1
                counter = 0
                logging.debug(f"We send request for {q}")
                while counter < int(limit_result):
                    url = f"https://api.shodan.io/shodan/host/search?query={q}&page={page}&key={key}"
                    response = requests.get(url)
                    if response.status_code != 200:
                        logging.debug(f"Shodan - request failed with status code: {response.status_code}")
                        break

                    banners = response.json()
                    total_tech = banners.get('total', 0)
                    logging.info(f"Shodan - total result: {total_tech} for query: {q}")
                    matches = banners.get('matches', [])
                    if not matches:
                        logging.debug(f"No matches found for query: {q} on page: {page}")
                        break
                    remaining = int(limit_result) - counter
                    matches_to_add = matches[:remaining]
                    #print(matches_to_add)
                    for banner in matches_to_add:
                        domains = banner.get('domains', [])
                        if not domains:
                            counter+=1
                        for domain in domains:                            
                            if counter>int(limit_result):
                                break
                            counter+=1
                            banner_dic = {
                                'ip':banner.get('ip_str', None),
                                'domain': domain,
                                'port': banner.get('port', None),
                                'country': banner.get('location', {}).get('country_code', None),
                                'technology': technology,
                                'feed': 'shodan',
                                'timestamp': banner.get('timestamp', None)
                            }
                            results.append(banner_dic)

                    page += 1
                if query_limit.lower() == "yes":
                    break

            return results
        except Exception as e:
            logging.error(f"ERROR shodan search {e}")

        return results

    def internet_db(ip):
        hostnames = []
        try:
            response = requests.get("https://internetdb.shodan.io/{0}".format(ip))
            if response.status_code != 200:
                return hostnames
            else:
                logging.debug(f"Shodan Internet DB body: {response.content.decode('utf-8')}")
                banners = response.json()
                return banners.get('hostnames', [])
        except Exception as e:
            logging.error(f"Shodan InternetDB exception: {str(e)}")
            return hostnames
