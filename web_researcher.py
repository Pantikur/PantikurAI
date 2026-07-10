"""
WebResearcher — Реальный движок интернет-поиска для Latisleane и Celesta.

Использует:
- Wikipedia API (базовые знания)
- PubMed API (медицинские статьи)
- arXiv API (научные预印本)
- Google Scholar (через SerpAPI)
- Web scraping ( BeautifulSoup )
"""

import asyncio
import json
import logging
import os
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger("web_researcher")


class WebResearcher:
    """
    Реальный исследователь интернета.
    
    Источники данных:
    1. Wikipedia — базовые знания
    2. PubMed — медицинские исследования
    3. arXiv — научные预印本
    4. Web scraping — дополнительные источники
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.search_count = 0
        self.success_count = 0
        self.failure_count = 0
        
        # Настройки
        self.timeout_seconds = 30
        self.max_retries = 3
        self.delay_between_requests = 1  # секунды
        
        logger.info("🌐 WebResearcher инициализирован")
    
    async def search_all_sources(self, query: str) -> Dict[str, Any]:
        """
        Поиск по всем источникам параллельно.
        
        :param query: Запрос для поиска
        :return: Собранные данные из всех источников
        """
        logger.info(f"🔍 Поиск: {query}")
        
        results = {
            "query": query,
            "timestamp": time.time(),
            "sources": {}
        }
        
        # Параллельный поиск по всем источникам
        tasks = [
            self._search_wikipedia(query),
            self._search_pubmed(query),
            self._search_arxiv(query),
            self._search_web(query)
        ]
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        results["sources"]["wikipedia"] = search_results[0] if not isinstance(search_results[0], Exception) else {"error": str(search_results[0])}
        results["sources"]["pubmed"] = search_results[1] if not isinstance(search_results[1], Exception) else {"error": str(search_results[1])}
        results["sources"]["arxiv"] = search_results[2] if not isinstance(search_results[2], Exception) else {"error": str(search_results[2])}
        results["sources"]["web"] = search_results[3] if not isinstance(search_results[3], Exception) else {"error": str(search_results[3])}
        
        # Подсчёт статистики
        self.search_count += 1
        has_data = any(results["sources"].get(k, {}).get("content") for k in results["sources"])
        if has_data:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        logger.info(f"✅ Поиск завершён: {sum(1 for k in results['sources'] if results['sources'][k].get('content'))}/4 источников")
        
        return results
    
    async def _search_wikipedia(self, query: str) -> Dict[str, Any]:
        """Поиск через Wikipedia API."""
        try:
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            # Wikipedia API принимает query как часть URL
            params = {
                "format": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url + query.replace(' ', '_'), params=params, timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        snippet = data.get("extract", "")
                        title = data.get("title", "")
                        
                        if snippet:
                            return {
                                "source": "wikipedia",
                                "content": snippet,
                                "title": title,
                                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                                "success": True
                            }
        except Exception as e:
            logger.debug(f"⚠️ Wikipedia поиск неудачен: {e}")
        
        return {"source": "wikipedia", "success": False}
    
    async def _search_pubmed(self, query: str) -> Dict[str, Any]:
        """Поиск через PubMed API (медицинские статьи)."""
        try:
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                "db": "pmc",
                "term": query,
                "retmax": 3,
                "usehistory": "y",
                "retmode": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as response:
                    if response.status == 200:
                        data = await response.text()
                        # PubMed возвращает XML, парсим вручную
                        ids = re.findall(r'<Id>(\d+)</Id>', data)
                        
                        if ids:
                            # Получаем абстракты
                            ids_str = ",".join(ids[:3])
                            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                            fetch_params = {
                                "db": "pmc",
                                "id": ids_str,
                                "rettype": "abstract",
                                "retmode": "xml"
                            }
                            
                            async with session.get(fetch_url, params=fetch_params, timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as response2:
                                if response2.status == 200:
                                    xml_data = await response2.text()
                                    abstracts = re.findall(r'<p>(.*?)</p>', xml_data)
                                    
                                    return {
                                        "source": "pubmed",
                                        "content": " | ".join(abstracts[:3]),
                                        "article_ids": ids[:3],
                                        "success": True
                                    }
        except Exception:
            logger.warning("⚠️ PubMed поиск неудачен")
        
        return {"source": "pubmed", "success": False}
    
    async def _search_arxiv(self, query: str) -> Dict[str, Any]:
        """Поиск через arXiv API."""
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": query,
                "start": 0,
                "max_results": 3
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        
                        # Парсим XML
                        titles = re.findall(r'<title>(.*?)</title>', xml_data)
                        summaries = re.findall(r'<summary>(.*?)</summary>', xml_data)
                        links = re.findall(r'<id>(http.*?)</id>', xml_data)
                        
                        articles = []
                        for i in range(min(len(titles), len(summaries))):
                            articles.append({
                                "title": titles[i].replace("\\n", " ").strip(),
                                "summary": summaries[i].replace("\\n", " ").strip()[:300],
                                "url": links[i] if i < len(links) else ""
                            })
                        
                        return {
                            "source": "arxiv",
                            "content": " | ".join([a["summary"] for a in articles]),
                            "articles": articles,
                            "success": True
                        }
        except Exception:
            logger.warning("⚠️ arXiv поиск неудачен")
        
        return {"source": "arxiv", "success": False}
    
    async def _search_web(self, query: str) -> Dict[str, Any]:
        """Поиск через веб-скрапинг (Wikipedia как основной источник)."""
        try:
            url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Извлекаем текст
                        paragraphs = soup.find_all("p")
                        text = " ".join([p.get_text()[:200] for p in paragraphs[:5]])
                        
                        return {
                            "source": "web",
                            "content": text[:1000],
                            "success": True
                        }
        except Exception:
            logger.warning("⚠️ Web поиск неудачен")
        
        return {"source": "web", "success": False}
    
    async def learn_from_search(self, topic: str) -> Dict[str, Any]:
        """
        Полный цикл обучения из одного поиска.
        
        :param topic: Тема для изучения
        :return: Собранные знания
        """
        results = await self.search_all_sources(topic)
        
        # Извлечение ключевых фактов
        facts = self._extract_facts(results)
        
        # Обновление кэша
        self.cache[topic] = {
            "results": results,
            "facts": facts,
            "learned_at": time.time()
        }
        
        return {
            "topic": topic,
            "facts_count": len(facts),
            "facts": facts,
            "sources_used": [k for k, v in results["sources"].items() if v.get("success")]
        }
    
    def _extract_facts(self, search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Извлечение фактов из результатов поиска."""
        facts = []
        
        for source, data in search_results["sources"].items():
            content = data.get("content", "")
            if not content or len(content) < 50:
                continue
            
            # Разбиваем на предложения
            sentences = re.split(r'[.!?]+', content)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 30 and len(sentence) < 300:
                    facts.append({
                        "text": sentence,
                        "source": source,
                        "confidence": 0.7 if source in ["pubmed", "arxiv"] else 0.5,
                        "timestamp": time.time()
                    })
        
        # Ограничиваем количество фактов
        return facts[:20]
    
    def get_cache(self, topic: str) -> Optional[Dict[str, Any]]:
        """Получить кэшированные данные по теме."""
        return self.cache.get(topic)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику поиска."""
        return {
            "total_searches": self.search_count,
            "successful": self.success_count,
            "failed": self.failure_count,
            "cache_size": len(self.cache),
            "success_rate": self.success_count / self.search_count if self.search_count > 0 else 0
        }
