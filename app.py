from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gorsel', methods=['GET'])
def gorsel_cek():
    kod = request.args.get('kod')
    pixel = request.args.get('pixel', '1100')
    headers = {"User-Agent": "Mozilla/5.0"}

    arama_url = f"https://www.boyner.com.tr/search?q={kod}"
    print(f"[1] Arama URL: {arama_url}")
    r1 = requests.get(arama_url, headers=headers)
    print(f"[2] Arama sayfası uzunluğu: {len(r1.text)}")

    soup1 = BeautifulSoup(r1.text, 'html.parser')
    product_div = soup1.find("div", class_="product-item_image__3pPPu")
    if not product_div:
        print("[3] Ürün divi bulunamadı")
        return jsonify({"hata": "Ürün divi bulunamadı"}), 404
    print("[3] Ürün divi bulundu")

    a_tag = product_div.find("a", href=True)
    if not a_tag:
        print("[4] Ürün linki bulunamadı")
        return jsonify({"hata": "Ürün linki bulunamadı"}), 404
    print(f"[4] Ürün linki bulundu: {a_tag['href']}")

    urun_href = a_tag['href']
    urun_link = "https://www.boyner.com.tr" + urun_href
    print(f"[5] Ürün detay linki: {urun_link}")

    r2 = requests.get(urun_link, headers=headers)
    print(f"[6] Ürün detay sayfası uzunluğu: {len(r2.text)}")

    soup2 = BeautifulSoup(r2.text, 'html.parser')
    image_div = soup2.find("div", class_="product-image-layout_imageBig__3FR1P product-image-layout_lbEnabled__rVMcJ")
    if not image_div:
        print("[7] İstenen image div bulunamadı")
        return jsonify({"hata": "İstenen image div bulunamadı"}), 404

    img_tags = image_div.find_all("img", src=True)
    base_img_src = None
    for img in img_tags:
        if not img['src'].startswith("data:image/svg+xml"):
            base_img_src = img['src']
            break

    if not base_img_src:
        print("[8] Geçerli görsel bulunamadı")
        return jsonify({"hata": "Geçerli görsel bulunamadı"}), 404

    print(f"[7] İlk görsel bulundu: {base_img_src}")
    match = re.match(r"(.*/)([^/_]+_[^/_]+_)\d+\.jpg.*", base_img_src)
    if not match:
        return jsonify({"hata": "Görsel URL'si beklenen formatta değil"}), 500

    prefix, image_id = match.groups()
    print(f"[9] Görsel prefix: {prefix}, image_id: {image_id}")

    # milattansonra
    img_list = []
    for i in range(1, 10):  # Max resim adeti
        img_url = f"{prefix}{image_id}{str(i).zfill(2)}.jpg?v=1"
        test_url = img_url.replace('/mnresize/200/', f'/mnresize/{pixel}/')
        response = requests.head(test_url, headers=headers)
        if response.status_code == 200:
            print(f"[10] Görsel bulundu: {test_url}")
            img_list.append(test_url)
        else:
            print(f"[10] Görsel bulunamadı, durduruluyor: {test_url}")
            break

    if not img_list:
        return jsonify({"hata": "Hiçbir görsel bulunamadı"}), 404

    return jsonify({"resimler": img_list})


if __name__ == '__main__':
    app.run(debug=True)
