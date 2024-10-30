from bs4 import BeautifulSoup as bs
import requests

url = "https://www.kariyer.net/is-ilanlari?kw=python"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
}
response = requests.get(url, headers=headers)
print(f"Status code is {response.status_code}")

if response.status_code == 200:
    print("Succesful")
    html_text = response.text
    soup = bs(html_text, "html.parser")
    # print(soup.prettify())

    # job = soup.find("div", class_ = "list-items").text # to see better it's content
    # job = soup.find("div", class_ = "list-items").prettify() # to see better it's content
    job = soup.find("div", class_ = "list-items")
    company_name = job.find("a", class_ = "k-ad-card" ).text
    print(job.prettify())
    print(company_name)


    # <div data-v-cb46de94="" class="list-items">




elif response.status_code == 404:
    print("Error: Resource not found.")
elif response.status_code == 403:
    print("Error: Access forbidden.")
else:
    print(f"Unexpected error: {response.status_code}")




