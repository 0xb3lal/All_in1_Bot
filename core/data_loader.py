import requests
import hashlib
import hmac
from bs4 import BeautifulSoup
from config import Username, Password

base_url = "http://10.0.0.254/radiusmanager"
login_url = f"{base_url}/user.php?cont=login"
lang_url = f"{base_url}/user.php?cont=change_lang&lang=English"

md5_pass = hashlib.md5(Password.encode()).hexdigest()
md5_hmac = hmac.new(Username.encode(), md5_pass.encode(), hashlib.md5).hexdigest()

data = {
    'username': Username,
    'password': '',
    'md5': md5_hmac,
    'lang': 'English',
    'Submit': 'Login'
}

session = requests.Session()
session.get(lang_url)
r = session.post(login_url, data=data)
soup = BeautifulSoup(r.text, "html.parser")
meta = soup.find('meta', attrs={'http-equiv': 'refresh'})

if meta and 'URL' in meta.get('content', ''):
    redirect_url = meta['content'].split('URL=')[-1]
    if not redirect_url.startswith('http'):
        redirect_url = f"{base_url}/{redirect_url}"
    r = session.get(redirect_url)
soup = BeautifulSoup(r.text, "html.parser")

info = {}
for row in soup.find_all("tr"):
    key_cell = row.find("td", class_="td1")
    value_cell = row.find("td", class_="b1")
    if key_cell and value_cell:
        key = key_cell.text.strip().rstrip(':')
        value = value_cell.text.strip()
        info[key] = value

