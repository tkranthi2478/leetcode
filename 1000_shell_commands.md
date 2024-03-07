# Network Commands

## Domain Name Related
whois <domain_name>
nslookup <domain_name>  //may return multiple IPs hosted zone resolves like that
dig <domain_name>
dig -x <ip_address> //reverse dns




cat /var/log/nginx/access.log | awk '{print $7}' | sort | uniq -c | sort -r -n | head -n 5

awk
sort
uniq
head
xargs