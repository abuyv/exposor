<p align="center">
  <img alt="Exposor-Logo" src="https://raw.githubusercontent.com/abuyv/exposor/main/docs/media/exposor-logo.png" height="150" />
  <br>
<strong>Exposor - A Contactless Reconnaissance Tool with unified syntax</strong>
  <p align="center">
    &nbsp;<a href="https://web.archive.org/web/20250827133954/https://blackhat.com/us-25/arsenal/schedule/index.html#exposor---a-contactless-reconnaissance-tool-using-internet-search-engines-with-a-unified-syntax-44637"><img alt="Static Badge" src="https://img.shields.io/badge/BlackHat_USA_2025-Arsenal-blue.svg"></a>
    &nbsp;<a href="https://web.archive.org/web/20251112050509/https://www.appsecvillage.com/events/dc-2025/exposor-a-contactless-reconnaissance-tool-using-internet-search-engines-with-a-unified-syntax-929434"><img alt="Static Badge" src="https://img.shields.io/badge/DEFCON_USA_2025-AppSec_Village-orange.svg"></a>
  &nbsp;<a href="https://web.archive.org/web/20250403064040/https://blackhatmea.com/agenda-2024?combine=exposor&field_swapcard_sessions_day_target_id=All"><img alt="Static Badge" src="https://img.shields.io/badge/BlackHat_MEA_2024-Arsenal-red.svg"></a>
  &nbsp;<a href="https://blackhat.com"><img alt="Static Badge" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  </p>
</p>

<div align="center">
  
[Getting started](#getting-started) •
[Installation](#installation) •
[Usage](#Usage) •
[Contribution](#Contribution) •
[Future Work](#Future-Work) •
[Disclaimer](#Disclaimer) •
[License](#License)

</div>

***

## Getting Started

Exposor is a contactless reconnaissance tool focused on technology detection across [Censys](https://search.censys.io), [Fofa](https://fofa.info), [Shodan](https://www.shodan.io), and [Zoomeye](https://www.zoomeye.org). With a unified syntax for multi-platform querying, It gives security researchers and professionals a clear view of exposed systems, enabling quick risk identification.


### How it Works

- Configure your API keys for supported feeds.
- Use exposor's query syntax to find technologies
- Retrive and analyze results accross multiple search engines in a single workflow.
- Contribute custom YAML files to extend detection capabilities.

<div align="center">
<img alt="Exposor Help" src="https://raw.githubusercontent.com/abuyv/exposor/main/docs/media/exposor-help.gif" width="800"/>
</div>

### Key Features
 - Easily configure API credentials and keep the intelligence files updated.
 - Perform targeted searches by netblock, country code, or hostname.
 - Execute queries across multiple feeds with a unified syntax.
 - Extend intel capabilities by contributing new YAML files. 
 - Identify exposed systems and potential vulnerabilities using CPEs or CVEs.

These features make Exposor a powerful tool for cybersecurity professionals conducting non-intrusive active reconnaissance.


## Installation

You have two options to install **Exposor**:

Intall via pip

```bash
#latest stable release
pip install exposor
```

Clone the repository

```bash
git clone https://github.com/abuyv/exposor.git
cd exposor
pip install -r requirements.txt
```

> [!NOTE]  
> For the latest stable releases, visit the [Releases page](https://github.com/abuyv/exposor/releases)

### Configuration

To use **Exposor**, you must configure API keys for the feeds you want to search. At least one API key is required to enable searching on a feed.

#### Adding API Keys

You can add your API keys in two ways:

1. Using `--init` option

Run `exposor --init` option to create a configuration file:

```bash
exposor --init shodan:api_key zoomeye:api_key censys:api_id:api_secret fofa:email:api_key
```


1. Using env variables
   
Set the API keys as environment variables using the following commands:

```bash

# Unix
export CENSYS_API_ID="your_censys_api_id"
export CENSYS_API_KEY="your_censys_api_secret"
export FOFA_EMAIL="your_fofa_email"
export FOFA_API_KEY="your_fofa_api_key"
export SHODAN_API_KEY="your_shodan_api_key"
export ZOOMEYE_API_KEY="your_zoomeye_api_key"

# Windows
$env:CENSYS_API_ID="your_censys_api_id"
$env:CENSYS_API_KEY="your_censys_api_secret"
$env:FOFA_EMAIL="your_fofa_email"
$env:FOFA_API_KEY="your_fofa_api_key"
$env:SHODAN_API_KEY="your_shodan_api_key"
$env:ZOOMEYE_API_KEY="your_zoomeye_api_key"

```

These keys will be automatically picked up by Exposor.




> [!IMPORTANT]  
> At least one API key must be configured to perform searches on any feed.
> 
> If you need to update your keys, you can either re-export them or re-run the `--init` command 



## Usage

Run Exposor to detect specific technologies using predefined YAML files:

```bash
   __
  /__\__  __ _ __    ___   ___   ___   _ __
 /_\  \ \/ /| '_ \  / _ \ / __| / _ \ | '__|
//__   >  < | |_) || (_) |\__ \| (_) || |
\__/  /_/\_\| .__/  \___/ |___/ \___/ |_|
            |_|
                                     version: 1.0.0 


Usage: exposor.py -q cpe:2.3:a:vendor:product --feed all -o result.csv

Explore multiple feeds for a given CPE or CVE. Supported feeds include Censys, Fofa, Shodan, and Zoomeye.

General Options:
-h, --help                Display this help message and exit
--init                    Initialize API keys for the supported feeds in the format `feed:credentials`
--update                  Update the intelligence files (intels folder) to include the latest queries

Query Options:
-q, --query               Specify the search query. 
                          (e.g. `cpe:2.3:a:vendor:product` for technologies or `CVE-2024-XXXX` for vulnerabilities)
-qL, --query-limit        Limit the number of queries sent to the specified feed for a given CPE. The default value 							  
                          is "yes", means the query is already limited to sending only one query per feed. If you 
                          want to send all possible queries in each feed, disable this option by using `-qL no`
-f, --feed                Chooese one or more data feeds to query from. Use 'all' to query all supported feeds
-c, --country             Search technologies by specific country using country codes (e.g. `US` for the USA) 
-n, --netblock            Provde a netblock or a specific IP address to search (e.g. `192.168.0.1/24` or `192.168.0.1`)
-d --domain-name          Specify the target domain to search (e.g. `example.com`)
--limit                   Set the maximum number of results to fetch for each query in each feed. For instance,
                          if the limit is 10 and there are 3 queries for a feed, a total of 30 results will 
                          be fetched (10 results × 3 queries). (default value is '50')

Result Options:
-v, --verbose             Enable verbose output to get detailed logs, increase output verbosity (-v, -vv)
-o, --output              Specify the output file name (e.g. `results.csv`)


```

## Contribution

If you wish to contribute to the project and help expand the coverage of intels, follow the instructions below to add a new YAML file:
- Please read [Contributing Guidelines](CONTRIBUTING.md) to understand how to propose changes.

- **`technology_intels/`**: Contains YAML files for detecting specific technologies or platforms. Files are organized by `vendor_name/product_name/vendor_product.yaml`.
- **`vulnerability_intels/`**: Contains YAML files for tracking vulnerabilities (e.g., CVEs) generated using the `vulners-api.py` script.

```text
exposor/                               
├── intels/                                               # Folder for intelligence YAML files
│   ├── technology_intels/                                # Technology-specific YAML files 
│   │   ├── vendor_name/                                  # Vendor name folder
│   │   │   ├── product_name/                             # Product name folder
│   │   │   │   ├── vendor_product.yaml   <––– Example technology YAML
│   └── vulnerability_intels/                             # Vulnerability-specific YAML files
│   │   ├── vendor_product_cves.yaml      <––– Example vulnerability YAML
└── ...
```




## Future Work
Integrate more feeds
- [x] [Censys](https://search.censys.io)
- [x] [Fofa](https://fofa.info)
- [x] [Shodan](https://www.shodan.io)
- [x] [Zoomeye](https://www.zoomeye.org)
- [ ] [Quake](https://quake.360.net/quake/#/index)
- [ ] [Hunter](https://hunter.qianxin.com)

Pending features
- [ ] Auto unifying queries across feeds 
- [ ] Auto generation of vulnerability YAML files
- [ ] Supporting multiple API keys for a single feed
- [ ] Implementing custom query syntax
- [ ] Adding a logical OR operator for queries to save API credits and optimize usage.

## Disclaimer

Use `Exposor` responsibly and follow all regulations. You are fully responsible for your actions. If you misuse this tool or break the law, <ins>it’s entirely your own responsibility<ins>.

## License

`Exposor` is developed by [@abuyv](https://twitter.com/abuyv) and is [MIT License](https://github.com/abuyv/exposor/blob/main/LICENSE)

***

## 💙 Thank you</h2>
<img src="https://raw.githubusercontent.com/abuyv/exposor/main/docs/media/exposor-star-repo.gif" alt="Starred" width="300"/>

If you are here and found it useful, consider giving the repository a ⭐ to show your support. 

