# Vector Link Search Projesi

Web linklerinden içerik çekerek sorulara doğal dilde yanıt veren bir Retrieval-Augmented Generation (RAG) sistemidir. `ChromaDB` ile vektör tabanlı bilgi alma ve `Ollama` ile yerel LLM kullanarak hızlı ve doğru yanıtlar sunar.

## Özellikler

*   Web linklerinden içerik çekme ve cümlelere ayırma
*   Soruya en yakın cümleleri bulma (`ChromaDB` ile)
*   Yerel LLM ile doğal dilde yanıt üretme (`Ollama`)
*   Seçilen cümlelerin mesafelerini (cosine distance) görüntüleme

## Kullanılan Teknolojiler

*   Python 3.8+
*   Sentence Transformers (`paraphrase-multilingual-mpnet-base-v2`)
*   `ChromaDB`
*   `Ollama` (`Gemma3:1b` veya `LLaMA 3`)
*   `BeautifulSoup` ve `Requests`

## Kurulum

### 🔧 Ortak Adımlar

1. **Depoyu klonlayın:**
    ```bash
    git clone https://github.com/GokhanAsilturk/VectorDB_Link_Search.git
    cd RAGenius
    ```

2. **Python bağımlılıklarını yükleyin:**
    ```bash
    pip install requests beautifulsoup4 sentence-transformers chromadb
    ```

---

### 🍏 Mac için Ek Adımlar

1. **Ollama’yı Homebrew ile yükleyin:**
    ```bash
    brew install ollama
    ```

2. **Ollama'yı başlatın ve model indirin:**
    ```bash
    ollama pull gemma3:1b
    ollama serve
    ```

    > `gemma3:1b` çalışmazsa, alternatif olarak:
    ```bash
    ollama pull llama3
    ```

---

### 🪟 Windows için Ek Adımlar

1. [https://ollama.com/download](https://ollama.com/download) adresinden Ollama’yı indirip kurun.

2. Komut istemcisini (CMD, PowerShell ya da Windows Terminal) açın ve aşağıdakileri çalıştırın:
    ```bash
    ollama pull gemma3:1b
    ollama serve
    ```

    > `gemma3:1b` çalışmazsa, alternatif olarak:
    ```bash
    ollama pull llama3
    ```

3. `Config.LLM_MODEL` değişkenini `linkBasedQASystem.py` dosyasında ilgili modele göre güncelleyin.

---

## Projeyi Çalıştırma
Direkt IDE'niz ile start verebilirsiniz veya:
```bash
python linkBasedQASystem.py
```
## Kullanım

1.  **Web linklerini girin** (her satıra bir link, bitirdiğinizde `bitti` yazın):
    ```
    Link: https://tr.wikipedia.org/wiki/Osmanlı_İmparatorluğu
    Link: bitti
    ```

2.  **Sorunuzu sorun** (çıkmak için `çık` yazın):
    ```
    Soru: Osmanlı İmparatorluğu’nun kurucusu kimdir?
    ```

3.  **Yanıtı ve mesafeleri görün:**
    ```
    Yanıt:
    Osmanlı İmparatorluğu’nun kurucusu Osman Gazi’dir.

    Seçilen cümlelerin mesafeleri:
    - Cümle: Osmanlı İmparatorluğu, Osman Gazi tarafından... (Mesafe: 0.1200)
    - Cümle: Osman Gazi, Osmanlı Devleti’nin kurucusu... (Mesafe: 0.1500)
    ```

## Notlar

*   `gemma3:1b` yerine `llama3` gibi başka bir model kullanılabilir.
*   Daha iyi yanıtlar ve bir UI eklemek için geliştirme devam ediyor.

## Katkıda Bulunma

Projeyi geliştirmek için Pull Request (PR) açabilirsiniz:

1.  Depoyu fork edin.
2.  Yeni bir branch oluşturun: `git checkout -b feature/yeni-ozellik`.
3.  Değişikliklerinizi yapın ve commit edin: `git commit -m "Yeni özellik eklendi"`.
4.  Push edin: `git push origin feature/yeni-ozellik`.
5.  PR açın.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır.

## İletişim

Sorularınız veya önerileriniz için:

*   **GitHub:** [https://github.com/GokhanAsilturk](https://github.com/GokhanAsilturk)
*   **LinkedIn:** [https://www.linkedin.com/in/gokhanasilturk](https://www.linkedin.com/in/gokhanasilturk)
