from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ara', methods=['GET'])
def ara():
    kod = request.args.get("kod")
    if not kod:
        return jsonify({"hata": "Kod girilmedi"}), 400

    headers = {"User-Agent": "Mozilla/5.0"}
    arama_url = f"https://www.boyner.com.tr/search?q={kod}"

    # Arama sayfasını çek
    r = requests.get(arama_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    # İlk ürünün resim DIV'ini bul (Boyner'in güncel sınıfları)
    product = soup.find("div", class_="product-item_image__3pPPu")
    if not product:
        return jsonify({"hata": "Ürün bulunamadı"}), 404

    img = product.find("img")
    if not img or not img.get("src"):
        return jsonify({"hata": "Görsel bulunamadı"}), 404

    img_url = img["src"]

    # Boyner görsel URL’leri bazen düşük kalite olabilir → orijinalini alma
    if img_url.startswith("//"):
        img_url = "https:" + img_url

    return jsonify({"resim": img_url})


if __name__ == "__main__":
    app.run(debug=True)
