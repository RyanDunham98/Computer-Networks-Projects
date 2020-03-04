#!/usr/bin/python3
import csv
import dns.resolver
import ipaddress
from argparse import ArgumentParser

#prints results of the experiment
def print_results(ecs,non_ecs,inaccess,alias,error,domain_names):
    d = len(domain_names)
    ecs = 100*(len(ecs)/d)
    non_ecs = 100*(len(non_ecs)/d)
    inaccess = 100*(len(inaccess)/d)
    alias = 100*(len(alias)/d)
    error = 100*(len(error)/d)
    print("%f" % ecs + "% of Popular Domains support ECS" )
    print("%f" % non_ecs + "% of Popular Domains do not support ECS")
    print("%f" % inaccess + "% of Popular Domains are inaccessable")
    print("%f" % alias + "% of Popular Domains are alias's")
    print("%f" % error + "% of Popular Domains are errors")

#gets the correct IP address for the given subnet
def get_subnet(ip, sub):
    ip = ip.split('.')
    if (sub == '/8'):
        keep = ip[0]
        network = ".".join([str(keep), "0", "0", "0"])
        network += "/8"
        return network

    elif (sub== '/16'):
        keep = ip[0:2]
        keep = ".".join(keep)
        network = ".".join([str(keep), "0", "0"])
        network += "/16"
        return network

    else:
        keep = ip[0:3]
        keep = ".".join(keep)
        network = ".".join([str(keep), "0"])
        network += "/24"
        return network

#checks if the response from the NS contains an ECS marker
def check_ecs(response):
    for option in response.options:
        if (option.otype == dns.edns.ECS):
            return True

    return False

def check_alias(response):
    for record_set in response.answer:
        for record in record_set:
            if (record.rdtype == dns.rdatatype.CNAME):
                return True

    return False

#gets the IP address of the NS for a given domain name
def get_NS(response):
    response_code = response.rcode()
    response_description = dns.rcode.to_text(response_code)

    if response_code != 0:
        return None

    #get name server ip addresss
    for record_set in response.additional:
        for record in record_set:
            # IPv4 address
            if (record.rdtype == dns.rdatatype.A):
                return [str(record.address),"A"]
            # Name server domain name
            elif (record.rdtype == dns.rdatatype.NS):
                return [str(record.target),"NS"]
            # Other type of record
            else:
                return [str(record),"AAAA"]

#contructs a DNS query
def construct_query(domain, record_type, client_network=None):
    if client_network is None:
        query = dns.message.make_query(domain, record_type)
    else:
        network_address = str(client_network.network_address)
        network_prefixlen = client_network.prefixlen
        ecs = dns.edns.ECSOption(network_address, network_prefixlen)
        query = dns.message.make_query(domain, record_type, use_edns=True,
                options=[ecs])
    return query

#issues a DNS query
def issue_query(domain, ns_ip, client_network=None):
    record_type = 'A'
    query = construct_query(domain, record_type, client_network)
    tout = 3

    try:
        response = dns.query.udp(query, ns_ip, timeout=tout)
    except dns.exception.Timeout:
        print('Query timed out')
        return
    except dns.query.BadResponse:
        print('Bad Response')
        return
    except dns.message.TrailingJunk:
        print('Trailing Junk')
        return
    except dns.exception.FormError:
        print('DNS message is malfomed')
        return
    except dns.query.UnexpectedSource:
        print('Unexpected source')
        return

    return(response)

def main():

    arg_parser = ArgumentParser(description='Messenger', add_help=False)
    arg_parser.add_argument('-s', dest='start', action='store',
            type=int, required=True, help='start index')
    arg_parser.add_argument('-e', dest='end', action='store',
            type=int, required=True, help='end index')
    settings = arg_parser.parse_args()

    subnets = ["/8","/16","/24"]
    RECURSIVE_RESOLVER = '149.43.80.12'

    domain_names = []
    with open('top-1m.csv', newline='') as f:
        reader = csv.reader(f)
        for line in enumerate(reader):
            data = line[1][1]
            domain_names.append(data)

    ecs = []
    non_ecs = []
    inaccess = []
    alias = []
    error =[]
    domain_names = domain_names[settings.start:settings.end]

    for name in domain_names:
        print(name)
        response = issue_query(name, RECURSIVE_RESOLVER)
        if response == None:
            inaccess.append(name)
        elif check_alias(response):
            alias.append(name)
        else:
            name_server = get_NS(response)

            if (name_server == None):
                error.append(name)

            elif(name_server[1] == "AAAA"):
                inaccess.append(name)

            else:
                is_ecs = False
                for sub in subnets:
                    ip = get_subnet('149.43.80.0', sub)
                    client_network = ipaddress.ip_network(ip)
                    reply = issue_query(name, name_server[0], client_network)
                    if reply != None:
                        is_ecs = check_ecs(reply)
                        if is_ecs:
                            ecs.append(name)
                            break

                if reply == None:
                    inaccess.append(name)

                if name not in ecs and name not in inaccess:
                    non_ecs.append(name)

    print_results(ecs,non_ecs,inaccess,alias,error,domain_names)

if __name__ == '__main__':
    main()
