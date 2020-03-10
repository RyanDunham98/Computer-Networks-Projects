Reproducing DNS research

Instructions:

Run the file ecs.py with two input arguments -s -e, that indicate the start and end of the 1 million popular domains dataset slice you wish to run. ex. ./ecs.py -s 0 -e 100000 (issue queries to 0th to 99,999th entry in top 1m domains).

Summary

This project aimed to reproduce a portion of the paper, Exploring EDNS-Client-Subnet Adopters in your Free Time (https://conferences.sigcomm.org/imc/2013/papers/imc163s-streibeltA.pdf). In section 3.2 of this paper, the authors run an experiment in order to determine ECS adopters among the 1 million most popular domain names. ECS or EDNS-Client-Subnet, is a DNS extension that many popular companies such as google have begun to adopt. ECS enabled resolvers pass client IP information to authoritative name servers. This prevents the servers from mislocating the origin of the DNS request, allowing them to provide better service to end users. This project aims to repeat this procedure to understand what proportion of the 1 million top domain names are ECS enabled.

The goal was to determine what fraction of popular domains support ECS and for those that aren't, are they innaccessible, alias' for other domains, or a name server with an error. To do this Cisco Umbrella 1 Million, a public database of one million of the most popular domain names, was used. To determine which DNs were ECS enabled we sent each ECS query three times, each with a subnet of /8, /16, or /24. If there is no response when the query is first sent then it is marked as innaccessible. If there is a response we first attempt to receive the name server, if we cannot it is marked as an error. After we check if the response is in CNAME instead of A, if it is it is marked as alias. We then do a similar test checking if it is AAAA, if it is it is marked again as innaccessible. Finally, we can check if the query response corresponds with ECS. We find the network using each subnet, then we can check if it supports ECS, if it is it is marked as ECS, if not it is marked as non_ecs. The 1 millions DNs were run in parallel in ten groups of one hundred thousand to cut down on run time.

39.3% of DNs support ECS, 12.8% of DNs do not support ECS, and 0.9% are inaccessible. 

25.8% of DNs have errors and 21.2% of DNs are alias'.
