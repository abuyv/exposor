# Standard
import argparse
import csv
import logging
import os
import sys
from pathlib import Path

# Local
from exposor import __version__
from exposor.feeds import query_builder
from exposor.feeds.shodan.shodan_feed import Shodan
from exposor.utils import logging_utils, search_utils, update_utils
from exposor.utils.args_helpers import (
    CustomHelpFormatter,
    RegexValidator,
    check_api_keys,
    check_country_args,
    check_domain_args,
    check_net_args,
    check_required_args,
    init_feed_api_keys,
    validate_args,
)


def supports_color():
    if not sys.stdout.isatty():
        return False
    if os.name == "nt":
        if any(
            var in os.environ for var in ["ANSICON", "WT_SESSION", "COLORTERM"]
        ):
            return True
        else:
            return False
    return True


def banner():
    if supports_color():
        CYAN = "\033[36m"   # ANSI code for cyan text
        GREEN = "\033[32m"  # ANSI code for green text
        RESET = "\033[0m"   # ANSI code to reset text
    else:
        CYAN = ""
        GREEN = ""
        RESET = ""

    font = rf""" {CYAN}
   __
  /__\__  __ _ __    ___   ___   ___   _ __
 /_\  \ \/ /| '_ \  / _ \ / __| / _ \ | '__|
//__   >  < | |_) || (_) |\__ \| (_) || |
\__/  /_/\_\| .__/  \___/ |___/ \___/ |_|
            |_|
                                    {GREEN} version: {__version__} {RESET}
"""

    print(CYAN + font)


def get_intels_path():
    LOCAL_INTELS_DIR = Path(__file__).parent / "intels"

    if not LOCAL_INTELS_DIR.exists():
        raise FileNotFoundError(
            f"Intels directory not found at {LOCAL_INTELS_DIR}"
        )
    if not LOCAL_INTELS_DIR.is_dir():
        raise NotADirectoryError(
            f"Expected a directory but found a file at {LOCAL_INTELS_DIR}"
        )
    return LOCAL_INTELS_DIR


def parse_args():
    parser = argparse.ArgumentParser(
        prog = "exposor.py",
        usage = "%(prog)s -q cpe:2.3:a:vendor:product --feed all -o result.csv",
        description = (
            "Explore multiple feeds for a given CPE or CVE. Supported feeds "
            "include Censys, Fofa, Shodan, and Zoomeye"),
        formatter_class = CustomHelpFormatter,
        add_help=False
    )
    
    # General Options 
    general_group = parser.add_argument_group("General Options")
    
    general_group.add_argument(
        "-h", "--help",
        action="help",
        help="Show this help message and exit"
    )
    general_group.add_argument(
        "--init",
        nargs = "+",
        help = "Initialize API keys for the feeds in the format `feed:credentials`"
    )
    general_group.add_argument(
        "--update",
        action = "store_true",
        help = "Update the intelligence files (intels folder) to include the latest queries"
    )
    
    # Query Options
    query_group = parser.add_argument_group("Query Options")
    query_group.add_argument(
        "-q", "--query",
        help = (
             "Specify the search query. "
             "(e.g. `cpe:2.3:a:vendor:product` for technologies or `CVE-2024-XXXX` for vulnerabilities)"
        ),
        action = RegexValidator
    )
    query_group.add_argument(
        "-qL", "--query-limit",
        choices = ["yes", "no"],
        default = "yes",
        help = (
            "Limit the number of queries sent to the specified feed for a given query. The default value "
            "is `yes`, means the query is already limited to sending only one query per feed. If you "
            "want to send all possible queries in each feed, disable this option by using `-qL no`"
        )
    )
    query_group.add_argument(
        "-f", "--feed",
        nargs = '+',
        choices = ["all", "censys", "fofa", "shodan", "zoomeye"],
        help = "Chooese one or more data feeds to query from. Use `all` to query all supported feeds"
    )
    query_group.add_argument(
        "-c", "--country",
         help = "Search technologies by specific country using country codes (e.g. `US` for the USA)"
    )
    query_group.add_argument(
        "-n", "--netblock",
         help = (
             "Provde a netblock or a specific IP address to search"
             " (e.g. `192.168.0.1/24` or `192.168.0.1`)"
             )
    )
    query_group.add_argument(
        "-d", "--domain-name",
         help = (
             "Specify the target domain to search"
             " (e.g. `example.com`)"
             )
    )
    query_group.add_argument(
        "--limit",
        type = int,
        default = 50,
        help = (
            "Set the maximum number of results to fetch for each query in each feed."
            "For instance, if the limit is 10 and there are 3 queries for a feed, "
            "a total of 30 results will be fetched from that feed (10 results × 3 queries)."
            " (default value is `50`)"
        )
    )
    
    # Result Options
    result_group = parser.add_argument_group("Result Options")
    result_group.add_argument(
        "-v", "--verbose",
        action = "count",
        default = 0,
        help = "Enable verbose output to get detailed logs, increase output verbosity (`-v`, `-vv`)"
    )
    result_group.add_argument(
        "-o",
        "--output",
        required = False,
        help = "Specify the output file name (e.g. `results.csv`)"
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    return args, parser


def main():
    banner()
    queries_yaml = []
    unique_result = set()
    flattened_results = []

    args, parser = parse_args()

    logging_utils.setup_logging(args.verbose, color_supported=supports_color())
    logging.debug(f"Parsed arguments: {args}")
    check_required_args(args, parser)

    if args.update:
        intels_folder = get_intels_path()
        logging.debug(f"intels folder is {intels_folder}")
        update_utils.update(intels_folder)
        return

    if args.init:
        logging.info("Initializing API keys...")
        init_feed_api_keys(args.init, parser)
        logging.info("API keys initialized.")
        return

    if args.feed:
        validate_args(args, parser)
        if not check_api_keys(args.feed, parser):
            logging.info("Please initialize missing API keys to continue.")
    else:
        logging.debug("No feed provide. Defaulting to `shodan`.")
        args.feed = ["shodan"]

    if args.country:
        country_file_path = Path(__file__).parent / "data" / "ISO-3166-countries.json"
        if not check_country_args(args.country, country_file_path, parser):
            parser.error("Invalid `country code` provided (please in ISO-3166 alpha-2 format).")

    if args.netblock:
        if not check_net_args(args.netblock, parser):
            parser.error("Invalid netblock provided `IP address` or `CIDR`.")

    if args.domain_name:
        if not check_domain_args(args.domain_name, parser):
            parser.error("Invalid `hostname` provided (e.g. `example.com`).")

    logging.info(f"Starting search for query: {args.query} ({args.query_type})")

    if args.query_type == "CPE":
        logging.debug(f"Performing CPE search for: {args.query}")
        queries_yaml = search_utils.find_technology_intel(args.query)
    elif args.query_type == "CVE":
        logging.debug(f"Performing CVE search for: {args.query}")
        queries_yaml = search_utils.find_vulnerability_intel(args.query)

    if queries_yaml is None:
        logging.warning("No logic found for the given query.")
        sys.exit(1)

    logging.info("Search completed successfully.")

    list_of_results = query_builder.query_parser(queries_yaml, args)

    for sublist in list_of_results:
        for item in sublist:
            ip = item.get('ip')
            port = item.get('port')
            domain = item.get('domain')
            cpe = item.get('cpe')
            # find hostnames for the missings ones (async)
            # if not domain:
            #    domains = Shodan.internet_db(ip)
            #    print(domains)
            unique_key = (ip, port, domain, cpe)
            if unique_key not in unique_result:
                unique_result.add(unique_key)
                flattened_results.append(item)

    if not flattened_results:
        logging.warning("No results to display.")
        sys.exit(0)

    logging.debug(f"result of feeds:{list_of_results}")

    max_rows = 9

    headers = ["IP", "Domain", "Port", "Country", "Technology", "Feed", "Timestamp"]

    col_widths = {header: max(len(str(row.get(header.lower(), ""))) for row in flattened_results) for header in headers}
    col_widths = {header: max(col_widths[header], len(header)) for header in headers}

    header_row = "  ".join(header.ljust(col_widths[header]) for header in headers)
    print(header_row)
    print("-" * len(header_row))

    for i, item in enumerate(flattened_results):
        if i >= max_rows:
            row = "  ".join(str("---").ljust(col_widths[header]) for header in headers)
            print(row)
            row = "  ".join(str(item.get(header.lower(), "")).ljust(col_widths[header]) for header in headers)
            print(row)
            break
        row = "  ".join(str(item.get(header.lower(), "")).ljust(col_widths[header]) for header in headers)
        print(row)

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as csv_file:
            fieldnames = flattened_results[0].keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_results)


if __name__ == '__main__':
    main()
