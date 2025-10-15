import multi


host_client = multi.Client('IF')
host = multi.Host(host_client, 'UnoGame', 1919810)
host.wait()