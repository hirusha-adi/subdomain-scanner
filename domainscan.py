import requests, os
from threading import Thread, Lock
from queue import Queue
from time import sleep as tsleep

q = Queue()
list_lock = Lock()
discovered_domains = []

def scan_subdomains(domain):
    global q

    while True:
        subdomain = q.get()
        url = f"http://{subdomain}.{domain}"
        try:
            requests.get(url)

        except requests.ConnectionError:
            pass

        else:
            print("+ Discovered:", url)
            with list_lock: # to not append at the same it
                discovered_domains.append(url)

        q.task_done()


def main(domain, n_threads, subdomains):
    global q

    for subdomain in subdomains:
        q.put(subdomain)

    for t in range(n_threads):
        worker = Thread(target=scan_subdomains, args=(domain,))
        worker.daemon = True
        worker.start()

if __name__ == "__main__":
    print("""
        ┌─┐┬ ┬┌┐ ┌┬┐┌─┐┌┬┐┌─┐┬┌┐┌  
        └─┐│ │├┴┐ │││ ││││├─┤││││  
        └─┘└─┘└─┘─┴┘└─┘┴ ┴┴ ┴┴┘└┘  
          ┌─┐┌─┐┌─┐┌┐┌┌┐┌┌─┐┬─┐    
          └─┐│  ├─┤││││││├┤ ├┬┘    
          └─┘└─┘┴ ┴┘└┘┘└┘└─┘┴└─    
              by ZeaCeR#5641
""")

    domain = input("? Enter the domain: ")
    num_threads = int(input("? Enter the number of threads: "))
    if "subdomain.txt" in os.listdir():
        print("+ Selected 'subdomain.txt' as subdomain list")
        wordlist = "subdomain.txt"
    elif "subdomains.txt" in os.listdir():
        wordlist = "subdomains.txt"
        print("+ Selected 'subdomains.txt' as subdomain list")
    else:
        wordlist = input("? Enter the wordlist name: ")
    output_file = f"{domain.lower()}_results.txt"

    print("\n\n")

    main(domain=domain, n_threads=num_threads, subdomains=open(wordlist).read().splitlines())
    q.join()

    try:
        with open(output_file, "w") as f:
            for url in discovered_domains:
                print(url, file=f)
            print("+ Wrote output to file:", output_file)
    except Exception as e:
        print("- Unable to create the file with output")
        tsleep(3)
        exit()
