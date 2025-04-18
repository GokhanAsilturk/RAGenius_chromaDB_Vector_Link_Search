"""
Proje: Link Tabanlı Soru-Cevap Sistemi
Bu proje, kullanıcıdan alınan web linklerinden içeriği çekerek, sorulara yanıt verebilen
bir Retrieval-Augmented Generation (RAG) sistemi oluşturur.
"""

import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import chromadb
from typing import List, Dict, Optional, Any
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sabit değerler
class Config:
    """Uygulama yapılandırma sabitleri"""
    EMBEDDING_MODEL = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
    LLM_MODEL = "gemma3:1b"
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    OLLAMA_TIMEOUT = 30
    COLLECTION_NAME = "link_data"
    RELEVANCE_THRESHOLD = 0.5
    MAX_RESULTS = 10
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    STOPWORDS = {'nedir', 'nasıl', 'ne', 'için', 'ile', 've', 'bir', 'bu', 'şu', 'zaman'}


class ContentFetcher:
    """Web sayfalarından içerik çekme işlemlerini yönetir"""

    @staticmethod
    def fetch_from_url(url: str) -> Optional[str]:
        """Verilen URL'den içeriği çeker ve döndürür"""
        headers = {"User-Agent": Config.USER_AGENT}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            content = " ".join([para.get_text() for para in paragraphs])

            if not content.strip():
                logger.warning(f"URL'den içerik çekilemedi: {url}")
                return None

            logger.info(f"İçerik başarıyla çekildi: {url}")
            return content

        except Exception as e:
            logger.error(f"İçerik çekme hatası - {url}: {str(e)}")
            return None


class TextProcessor:
    """Metin işleme fonksiyonlarını içerir"""

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Metni cümlelere ayırır"""
        if not text:
            return []
        sentences = text.split('. ')
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def extract_keywords(query: str) -> List[str]:
        """Sorgudan anahtar kelimeleri çıkarır"""
        words = query.lower().split()
        keywords = [word for word in words if word not in Config.STOPWORDS]
        return keywords

    @staticmethod
    def is_sentence_relevant(sentence: str, query_keywords: List[str]) -> bool:
        """Cümlenin sorguya uygunluğunu kontrol eder"""
        sentence_lower = sentence.lower()
        return any(keyword in sentence_lower for keyword in query_keywords)


class VectorStore:
    """Vektör tabanı işlemlerini yönetir"""

    def __init__(self, model_name: str):
        """Vektör deposunu başlatır ve embedding modelini yükler"""
        self.model = SentenceTransformer(model_name)
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            Config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Vektör deposu başlatıldı: {Config.COLLECTION_NAME}")

    def add_sentences(self, sentences: List[str]) -> None:
        """Cümleleri vektörlere çevirip depoya ekler"""
        if not sentences:
            logger.warning("Eklenecek cümle bulunamadı")
            return

        embeddings = self.model.encode(sentences, normalize_embeddings=True)

        for i, (sentence, embedding) in enumerate(zip(sentences, embeddings)):
            self.collection.add(
                ids=[str(i)],
                embeddings=[embedding.tolist()],
                metadatas=[{"text": sentence}]
            )

        logger.info(f"{len(sentences)} cümle vektör deposuna eklendi")

    def query_similar(self, query: str, n_results: int = Config.MAX_RESULTS) -> Dict[str, Any]:
        """Sorguya benzer cümleleri bulur"""
        query_embedding = self.model.encode([query], normalize_embeddings=True)[0]

        return self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )


class LLMService:
    """Dil modeli hizmetini yönetir"""

    @staticmethod
    def generate_answer(question: str, context_sentences: List[str]) -> str:
        """Soru ve bağlam cümleleriyle Ollama'dan yanıt üretir"""
        if not context_sentences:
            return "Bunu bulamadım."

        context = " ".join(context_sentences)
        prompt = f"Soru: {question}\nBağlam: {context}\nYanıt:"

        try:
            response = requests.post(
                Config.OLLAMA_API_URL,
                json={
                    "model": Config.LLM_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=Config.OLLAMA_TIMEOUT
            )
            response.raise_for_status()

            result = response.json()
            answer = result.get("response", "Bunu bulamadım.")
            return answer.strip()

        except requests.exceptions.ConnectionError:
            logger.error("Ollama sunucusuna bağlanılamadı. 'ollama serve' komutunu çalıştırın.")
            return "Ollama sunucusuna bağlanılamadı. Lütfen 'ollama serve' komutunu çalıştırarak sunucuyu başlatın."

        except Exception as e:
            logger.error(f"LLM yanıt üretme hatası: {str(e)}")
            return "Yanıt üretilirken bir hata oluştu."


class RAGSystem:
    """Ana RAG sistemi sınıfı"""

    def __init__(self):
        """RAG sistemini başlatır"""
        self.content_fetcher = ContentFetcher()
        self.text_processor = TextProcessor()
        self.vector_store = VectorStore(Config.EMBEDDING_MODEL)
        self.llm_service = LLMService()

    def load_content_from_links(self, links: List[str]) -> List[str]:
        """Linklerden içerikleri çeker ve cümlelere ayırır"""
        all_sentences = []

        for link in links:
            content = self.content_fetcher.fetch_from_url(link)
            if content:
                sentences = self.text_processor.split_into_sentences(content)
                all_sentences.extend(sentences)

        logger.info(f"Toplam {len(all_sentences)} cümle yüklendi")
        return all_sentences

    def process_query(self, query: str) -> str:
        """Kullanıcı sorgusunu işler ve yanıt döndürür"""
        # Sorguya en benzer cümleleri bul
        query_results = self.vector_store.query_similar(query)

        # Sonuçları işle
        distances = query_results['distances'][0] if query_results['distances'] else []
        selected_sentences = [metadata['text'] for metadata in query_results['metadatas'][0]] if query_results['metadatas'] else []

        logger.debug(f"Mesafeler: {distances}")
        logger.debug(f"Seçilen cümleler: {selected_sentences}")

        # Anahtar kelimeleri çıkar ve filtreleme yap
        query_keywords = self.text_processor.extract_keywords(query)

        relevant_sentences = []
        for sentence, distance in zip(selected_sentences, distances):
            if (self.text_processor.is_sentence_relevant(sentence, query_keywords) and
                    distance <= Config.RELEVANCE_THRESHOLD):
                relevant_sentences.append(sentence)

        logger.debug(f"Filtrelenmiş cümleler: {relevant_sentences}")

        # Yanıt üret
        if not relevant_sentences or (distances and distances[0] > Config.RELEVANCE_THRESHOLD):
            return "Bunu bulamadım."

        return self.llm_service.generate_answer(query, relevant_sentences)


def get_links_from_user() -> List[str]:
    """Kullanıcıdan web linklerini alır"""
    print("Lütfen içerik linklerini girin. Her linki ayrı bir satıra yazın. Bittiğinde 'bitti' yazın.")
    links = []

    while True:
        link = input("Link (veya 'bitti' yazın): ")
        if link.lower() == "bitti":
            break
        if link.startswith("http"):
            links.append(link)
        else:
            print("Geçersiz link, lütfen 'http' ile başlayan bir link girin.")

    return links


def main():
    """Ana program fonksiyonu"""
    # Kullanıcıdan linkler alınır
    links = get_links_from_user()
    if not links:
        print("Hiç link girilmedi, program sona eriyor.")
        return

    # RAG sistemini başlat
    rag_system = RAGSystem()

    # Linklerden içerikleri yükle
    all_sentences = rag_system.load_content_from_links(links)
    if not all_sentences:
        print("Hiçbir içerikten cümle çekilemedi, program sona eriyor.")
        return

    # Cümleleri vektör deposuna ekle
    rag_system.vector_store.add_sentences(all_sentences)

    # Kullanıcı sorgu döngüsü
    print("\nŞimdi sorularınızı sorabilirsiniz:")
    while True:
        user_query = input("Sorunuz (Çıkmak için 'çık' yazın): ")
        if user_query.lower() == "çık":
            print("Programdan çıkılıyor...")
            break

        # Sorguyu işle ve yanıt üret
        print("\nYanıt:")
        answer = rag_system.process_query(user_query)
        print(answer)


if __name__ == "__main__":
    main()