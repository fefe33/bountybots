# bountybots
repo for selenium bots and scrapers to hopefully help with bug bounties

# Crawlbot.py

this script does the following:
scrapes a given site (or set of sites) for form methods, parameters, and actions, returning them as JSON.

<code> usage: crawlbot.py [-h] -b {chrome firefox} -u URL -is [INSCOPE ...] [-o OUT]</code><br>
<code>a selenium bot that crawls websites for forms</code><br>
<code>options:</code><br>
 <code> -h, --help  show this help message and exit </code><br>
 <code> -b, --browser {chrome, firefox}  the browser the bot should use </code><br>
 <code> -u, --url  the initial URL for the bot to start crawling</code><br>
 <code> -is, --inscope [INSCOPE ...] keywords to test against the url before adding to the crawl list</code><br>
 <code> -o, --out OUT  the name of the option output JSON file for the scan results </code><br><br>


<hr>
