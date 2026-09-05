"""
ESG Research Tools - Enhanced Version
Comprehensive web search, SEC filings, ESG databases, and data extraction utilities
Designed to fetch real, actionable ESG data from multiple reliable sources
"""

import os
import json
import requests
import time
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")  # Google Search API

# Request timeout settings
REQUEST_TIMEOUT = 15

# Trusted ESG data sources - prioritize these domains
TRUSTED_ESG_SOURCES = [
    "cdp.net",                    # Carbon Disclosure Project
    "sustainalytics.com",         # ESG ratings
    "msci.com",                   # MSCI ESG ratings
    "refinitiv.com",              # ESG scores
    "sec.gov",                    # SEC filings
    "globalreporting.org",        # GRI Standards
    "sasb.org",                   # SASB Standards
    "tcfd.org",                   # TCFD recommendations
    "unpri.org",                  # UN Principles for Responsible Investment
    "esg.org",
    "bloomberg.com",
    "reuters.com",
    "ft.com",                     # Financial Times
    "wsj.com",                    # Wall Street Journal
    "forbes.com",
]

# ESG-specific search terms organized by category
ESG_SEARCH_TERMS = {
    "Environmental": {
        "emissions": [
            "carbon emissions scope 1 2 3", "GHG emissions tCO2e",
            "net zero commitment", "carbon neutrality target",
            "emissions reduction percentage", "science based targets"
        ],
        "energy": [
            "renewable energy percentage", "solar wind investment",
            "energy efficiency program", "RE100 commitment",
            "clean energy transition", "power purchase agreement PPA"
        ],
        "water": [
            "water consumption reduction", "water stewardship program",
            "wastewater treatment", "water recycling rate"
        ],
        "waste": [
            "waste diversion rate", "circular economy initiatives",
            "zero waste to landfill", "plastic reduction"
        ],
        "climate": [
            "TCFD disclosure", "climate risk assessment",
            "physical climate risk", "transition risk"
        ]
    },
    "Social": {
        "diversity": [
            "diversity inclusion metrics", "women leadership percentage",
            "gender pay gap", "minority representation",
            "DEI initiatives", "equal opportunity"
        ],
        "employees": [
            "employee engagement score", "turnover rate",
            "employee benefits program", "workplace safety TRIR",
            "training development hours", "fair wages living wage"
        ],
        "community": [
            "community investment spending", "philanthropy program",
            "volunteer hours employees", "social impact"
        ],
        "supply_chain": [
            "supplier audit percentage", "responsible sourcing",
            "supply chain human rights", "conflict minerals policy"
        ]
    },
    "Governance": {
        "board": [
            "board independence percentage", "board diversity",
            "board tenure average", "board refreshment"
        ],
        "compensation": [
            "CEO pay ratio", "executive compensation ESG link",
            "say on pay vote", "compensation transparency"
        ],
        "ethics": [
            "code of ethics", "whistleblower policy",
            "anti-corruption program", "business ethics training"
        ],
        "risk": [
            "enterprise risk management", "ESG risk oversight",
            "cybersecurity program", "data privacy compliance"
        ],
        "transparency": [
            "ESG disclosure GRI SASB", "integrated reporting",
            "shareholder engagement", "proxy voting"
        ]
    }
}


# ========== PRIMARY SEARCH FUNCTIONS ==========

def search_with_serper(query: str, count: int = 10) -> List[Dict]:
    """
    Search using Serper API (Google Search) - most reliable for current data.
    Falls back to DuckDuckGo if Serper is unavailable.
    """
    if not SERPER_API_KEY:
        return search_with_duckduckgo(query, count)
    
    try:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": count,
            "gl": "us"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("organic", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": extract_domain(item.get("link", "")),
                "published": datetime.now().isoformat(),
                "score": calculate_source_trust_score(item.get("link", ""))
            })
        
        if results:
            print(f"   ✓ Serper found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"   ⚠ Serper error: {e}, trying DuckDuckGo...")
        return search_with_duckduckgo(query, count)


def search_with_duckduckgo(query: str, count: int = 10) -> List[Dict]:
    """
    Search using DuckDuckGo - free, no API key needed.
    Good fallback option with reasonable results.
    """
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=count))
        
        results = []
        for item in raw_results:
            url = item.get("href", "")
            results.append({
                "title": item.get("title", ""),
                "url": url,
                "snippet": item.get("body", "")[:1000],
                "source": extract_domain(url),
                "published": datetime.now().isoformat(),
                "score": calculate_source_trust_score(url)
            })
        
        if results:
            print(f"   ✓ DuckDuckGo found {len(results)} results")
        return results
        
    except ImportError:
        print("   ⚠ duckduckgo-search not installed, using Tavily...")
        return search_with_tavily(query, count)
    except Exception as e:
        print(f"   ⚠ DuckDuckGo error: {e}")
        return search_with_tavily(query, count)


def search_with_tavily(query: str, count: int = 10) -> List[Dict]:
    """
    Search using Tavily API - good for research-focused queries.
    """
    if not TAVILY_API_KEY:
        print("   ⚠ No Tavily API key, returning empty results")
        return []
    
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "max_results": count,
            "search_depth": "advanced",
            "include_answer": False
        }
        
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("results", []):
            item_url = item.get("url", "")
            results.append({
                "title": item.get("title", ""),
                "url": item_url,
                "snippet": item.get("content", "")[:1000],
                "source": extract_domain(item_url),
                "published": item.get("published_date", datetime.now().isoformat()),
                "score": item.get("score", 0.7)
            })
        
        if results:
            print(f"   ✓ Tavily found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"   ⚠ Tavily error: {e}")
        return []


def smart_search(query: str, count: int = 10, category: str = None) -> List[Dict]:
    """
    Smart search that tries multiple sources and deduplicates results.
    Prioritizes trusted ESG sources in results.
    """
    all_results = []
    
    # Try primary search
    results = search_with_serper(query, count)
    all_results.extend(results)
    
    # If we don't have enough results, try other sources
    if len(all_results) < count // 2:
        backup_results = search_with_duckduckgo(query, count)
        all_results.extend(backup_results)
    
    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for result in all_results:
        url = result.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)
    
    # Sort by trust score (prioritize trusted ESG sources)
    unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    return unique_results[:count]


# ========== ESG-SPECIFIC SEARCH FUNCTIONS ==========

def search_environmental_data(company_name: str) -> List[Dict]:
    """
    Search for comprehensive environmental ESG data.
    Uses multiple targeted queries to gather emissions, energy, water, and waste data.
    """
    print(f"🌍 Searching environmental data for {company_name}...")
    
    all_results = []
    queries = [
        f'"{company_name}" carbon emissions scope 1 2 3 reduction target',
        f'"{company_name}" renewable energy percentage solar wind',
        f'"{company_name}" sustainability report 2024 environmental',
        f'"{company_name}" net zero commitment climate strategy',
        f'"{company_name}" TCFD disclosure climate risk',
        f'"{company_name}" water waste reduction circular economy',
        f'site:cdp.net "{company_name}" OR site:sec.gov "{company_name}" sustainability',
    ]
    
    for query in queries:
        time.sleep(0.3)  # Rate limiting
        results = smart_search(query, count=5, category="Environmental")
        all_results.extend(results)
    
    # Deduplicate and sort by relevance
    unique_results = deduplicate_results(all_results)
    return unique_results[:15]


def search_social_data(company_name: str) -> List[Dict]:
    """
    Search for comprehensive social ESG data.
    Covers diversity, employee welfare, community impact, and supply chain.
    """
    print(f"👥 Searching social data for {company_name}...")
    
    all_results = []
    queries = [
        f'"{company_name}" diversity inclusion DEI metrics percentage',
        f'"{company_name}" employee engagement satisfaction turnover',
        f'"{company_name}" workforce safety TRIR injury rate',
        f'"{company_name}" pay equity gender gap compensation',
        f'"{company_name}" community investment philanthropy',
        f'"{company_name}" supply chain audit human rights labor',
        f'"{company_name}" ESG social responsibility report 2024',
    ]
    
    for query in queries:
        time.sleep(0.3)
        results = smart_search(query, count=5, category="Social")
        all_results.extend(results)
    
    unique_results = deduplicate_results(all_results)
    return unique_results[:15]


def search_governance_data(company_name: str) -> List[Dict]:
    """
    Search for comprehensive governance ESG data.
    Covers board composition, executive compensation, ethics, and risk management.
    """
    print(f"⚖️  Searching governance data for {company_name}...")
    
    all_results = []
    queries = [
        f'"{company_name}" board composition independence diversity',
        f'"{company_name}" executive compensation CEO pay ratio',
        f'"{company_name}" corporate governance ethics compliance',
        f'"{company_name}" risk management committee oversight',
        f'"{company_name}" proxy statement DEF 14A site:sec.gov',
        f'"{company_name}" shareholder engagement ESG governance',
        f'"{company_name}" audit committee cybersecurity data privacy',
    ]
    
    for query in queries:
        time.sleep(0.3)
        results = smart_search(query, count=5, category="Governance")
        all_results.extend(results)
    
    unique_results = deduplicate_results(all_results)
    return unique_results[:15]


def search_esg_news(company_name: str, days_back: int = 60) -> List[Dict]:
    """
    Search for recent ESG-related news about a company.
    Focuses on sustainability announcements, controversies, and achievements.
    """
    print(f"📰 Searching ESG news for {company_name}...")
    
    all_news = []
    queries = [
        f'"{company_name}" ESG news 2024',
        f'"{company_name}" sustainability announcement',
        f'"{company_name}" climate carbon initiative',
        f'"{company_name}" diversity social responsibility news',
    ]
    
    for query in queries:
        time.sleep(0.3)
        results = smart_search(query, count=5)
        all_news.extend(results)
    
    unique_news = deduplicate_results(all_news)
    return unique_news[:12]


def search_esg_reports(company_name: str) -> List[Dict]:
    """
    Search for official ESG/sustainability reports and SEC filings.
    Prioritizes official company disclosures and regulatory filings.
    """
    print(f"📄 Searching ESG reports for {company_name}...")
    
    all_reports = []
    queries = [
        f'"{company_name}" sustainability report 2024 PDF',
        f'"{company_name}" ESG report annual disclosure',
        f'"{company_name}" 10-K filing site:sec.gov sustainability',
        f'"{company_name}" TCFD report climate disclosure',
        f'"{company_name}" CDP score carbon disclosure',
        f'"{company_name}" GRI SASB integrated report',
    ]
    
    for query in queries:
        time.sleep(0.3)
        results = smart_search(query, count=4)
        all_reports.extend(results)
    
    unique_reports = deduplicate_results(all_reports)
    return unique_reports[:10]


def search_company_compliance(company_name: str) -> List[Dict]:
    """
    Search for compliance issues, violations, and regulatory actions.
    Important for identifying ESG risks and controversies.
    """
    print(f"🔍 Searching compliance data for {company_name}...")
    
    all_results = []
    queries = [
        f'"{company_name}" SEC violation enforcement action',
        f'"{company_name}" environmental fine penalty EPA',
        f'"{company_name}" labor violation OSHA complaint',
        f'"{company_name}" lawsuit settlement discrimination',
        f'"{company_name}" regulatory compliance issue',
    ]
    
    for query in queries:
        time.sleep(0.3)
        results = smart_search(query, count=4)
        all_results.extend(results)
    
    unique_results = deduplicate_results(all_results)
    return unique_results[:10]


def search_academic_research(company_name: str) -> List[Dict]:
    """
    Search for academic papers and research about the company's ESG performance.
    Useful for peer-reviewed insights and methodological rigor.
    """
    print(f"🎓 Searching academic research for {company_name}...")
    
    all_results = []
    queries = [
        f'"{company_name}" ESG performance research paper',
        f'"{company_name}" sustainability corporate responsibility study',
        f'"{company_name}" environmental impact assessment academic',
        f'site:scholar.google.com "{company_name}" ESG',
        f'site:ssrn.com "{company_name}" corporate governance',
    ]
    
    for query in queries:
        time.sleep(0.3)
        results = smart_search(query, count=4)
        all_results.extend(results)
    
    unique_results = deduplicate_results(all_results)
    return unique_results[:10]


def search_industry_benchmarks(company_name: str, industry: Optional[str] = None) -> List[Dict]:
    """
    Search for industry ESG benchmarks and peer comparisons.
    Helps contextualize company performance against industry standards.
    """
    print(f"📊 Searching industry benchmarks for {company_name}...")
    
    industry_term = industry if industry else "industry"
    
    all_results = []
    queries = [
        f'"{company_name}" ESG rating score MSCI Sustainalytics',
        f'{industry_term} ESG benchmark average comparison',
        f'"{company_name}" peer comparison ESG ranking',
        f'{industry_term} sector sustainability leaders',
    ]
    
    for query in queries:
        time.sleep(0.3)
        results = smart_search(query, count=4)
        all_results.extend(results)
    
    unique_results = deduplicate_results(all_results)
    return unique_results[:8]


# ========== HELPER FUNCTIONS ==========

def extract_domain(url: str) -> str:
    """Extract domain name from URL for source identification."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain
    except:
        return "Unknown"


def calculate_source_trust_score(url: str) -> float:
    """
    Calculate trust score based on source domain.
    Trusted ESG sources get higher scores.
    """
    if not url:
        return 0.5
    
    url_lower = url.lower()
    
    # Highest trust - official ESG rating agencies and regulators
    for source in ["sec.gov", "cdp.net", "globalreporting.org", "sasb.org"]:
        if source in url_lower:
            return 0.95
    
    # High trust - major ESG data providers and quality news
    for source in ["msci.com", "sustainalytics.com", "bloomberg.com", "reuters.com", "ft.com"]:
        if source in url_lower:
            return 0.90
    
    # Good trust - company IR pages and business news
    for source in ["investor", ".ir.", "forbes.com", "wsj.com", "businesswire.com"]:
        if source in url_lower:
            return 0.85
    
    # Medium trust - general sources
    return 0.70


def deduplicate_results(results: List[Dict]) -> List[Dict]:
    """Remove duplicate results based on URL, keeping highest scored version."""
    seen_urls = {}
    for result in results:
        url = result.get("url", "")
        if not url:
            continue
        
        if url not in seen_urls:
            seen_urls[url] = result
        else:
            # Keep the one with higher score
            if result.get("score", 0) > seen_urls[url].get("score", 0):
                seen_urls[url] = result
    
    # Sort by score descending
    sorted_results = sorted(seen_urls.values(), key=lambda x: x.get("score", 0), reverse=True)
    return sorted_results


def extract_esg_metrics_from_text(text: str) -> Dict[str, List[str]]:
    """
    Extract specific ESG metrics and numbers from text.
    Uses regex patterns to identify percentages, amounts, and key terms.
    """
    metrics = {
        "Environmental": [],
        "Social": [],
        "Governance": [],
        "Numbers": []
    }
    
    if not text:
        return metrics
    
    text_lower = text.lower()
    
    # Extract numbers with context
    number_patterns = [
        r'\d+(?:\.\d+)?%',  # Percentages
        r'\$\d+(?:\.\d+)?\s*(?:million|billion|M|B)',  # Dollar amounts
        r'\d+(?:,\d{3})*\s*(?:tons?|tCO2e|employees?|MW|GW|kWh)',  # Quantities
        r'\d+:\d+',  # Ratios like CEO pay ratio
    ]
    
    for pattern in number_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        metrics["Numbers"].extend(matches)
    
    # Environmental indicators
    env_keywords = ["carbon", "emissions", "renewable", "solar", "wind", "water", "waste", 
                    "climate", "net zero", "sustainability", "environmental"]
    for kw in env_keywords:
        if kw in text_lower:
            # Try to extract context around the keyword
            pattern = rf'.{{0,50}}{re.escape(kw)}.{{0,50}}'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                metrics["Environmental"].append(matches[0].strip())
    
    # Social indicators
    social_keywords = ["diversity", "employee", "workforce", "safety", "community", 
                       "inclusion", "training", "benefits", "wages"]
    for kw in social_keywords:
        if kw in text_lower:
            pattern = rf'.{{0,50}}{re.escape(kw)}.{{0,50}}'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                metrics["Social"].append(matches[0].strip())
    
    # Governance indicators
    gov_keywords = ["board", "director", "compensation", "ethics", "compliance", 
                    "governance", "audit", "risk", "shareholder"]
    for kw in gov_keywords:
        if kw in text_lower:
            pattern = rf'.{{0,50}}{re.escape(kw)}.{{0,50}}'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                metrics["Governance"].append(matches[0].strip())
    
    # Deduplicate each category
    return {k: list(set(v))[:10] for k, v in metrics.items()}


# ========== FORMATTING FUNCTIONS ==========

def format_web_search_results(results: List[Dict]) -> str:
    """Format search results for LLM analysis."""
    if not results:
        return "No search results found. Please rely on publicly available information about this company."
    
    formatted = "\n" + "=" * 60 + "\n"
    formatted += "WEB SEARCH RESULTS\n"
    formatted += "=" * 60 + "\n\n"
    
    for i, result in enumerate(results, 1):
        formatted += f"[{i}] {result.get('title', 'Untitled')}\n"
        formatted += f"    Source: {result.get('source', 'Unknown')} | Trust: {result.get('score', 0):.2f}\n"
        formatted += f"    URL: {result.get('url', 'N/A')}\n"
        formatted += f"    Content: {result.get('snippet', 'No content')[:500]}\n\n"
    
    return formatted


def format_academic_results(results: List[Dict]) -> str:
    """Format academic research results."""
    if not results:
        return "No academic research found for this company."
    
    formatted = "ACADEMIC RESEARCH\n" + "=" * 50 + "\n"
    for i, result in enumerate(results, 1):
        formatted += f"\n[{i}] {result.get('title', 'Untitled')}\n"
        formatted += f"    Source: {result.get('source', 'Unknown')}\n"
        formatted += f"    Summary: {result.get('snippet', 'No summary')[:400]}\n"
    
    return formatted


def format_search_by_category(results_by_category: Dict[str, List[Dict]]) -> str:
    """Format search results organized by ESG category."""
    formatted = "\n" + "=" * 60 + "\n"
    formatted += "ESG RESEARCH BY CATEGORY\n"
    formatted += "=" * 60 + "\n"
    
    for category, results in results_by_category.items():
        formatted += f"\n{'🌍' if 'Env' in category else '👥' if 'Soc' in category else '⚖️'} {category.upper()}\n"
        formatted += "-" * 40 + "\n"
        
        if not results:
            formatted += "No data found for this category.\n"
            continue
        
        for i, result in enumerate(results[:5], 1):
            formatted += f"{i}. {result.get('title', 'N/A')[:80]}\n"
            formatted += f"   {result.get('snippet', '')[:200]}...\n\n"
    
    return formatted


def format_esg_report_summary(
    company_name: str,
    web_results: Dict[str, List[Dict]],
    metrics: Dict[str, List[str]],
    news_articles: List[Dict]
) -> str:
    """Format comprehensive ESG research summary."""
    formatted = f"\n{'=' * 70}\n"
    formatted += f"ESG RESEARCH SUMMARY: {company_name.upper()}\n"
    formatted += f"{'=' * 70}\n"
    formatted += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # Environmental
    formatted += "🌍 ENVIRONMENTAL FINDINGS\n" + "-" * 50 + "\n"
    env_results = web_results.get("Environmental", [])
    if env_results:
        for r in env_results[:4]:
            formatted += f"• {r.get('title', 'N/A')}\n"
    if metrics.get("Environmental"):
        formatted += f"Key terms: {', '.join(metrics['Environmental'][:5])}\n"
    formatted += "\n"
    
    # Social
    formatted += "👥 SOCIAL FINDINGS\n" + "-" * 50 + "\n"
    social_results = web_results.get("Social", [])
    if social_results:
        for r in social_results[:4]:
            formatted += f"• {r.get('title', 'N/A')}\n"
    if metrics.get("Social"):
        formatted += f"Key terms: {', '.join(metrics['Social'][:5])}\n"
    formatted += "\n"
    
    # Governance
    formatted += "⚖️ GOVERNANCE FINDINGS\n" + "-" * 50 + "\n"
    gov_results = web_results.get("Governance", [])
    if gov_results:
        for r in gov_results[:4]:
            formatted += f"• {r.get('title', 'N/A')}\n"
    if metrics.get("Governance"):
        formatted += f"Key terms: {', '.join(metrics['Governance'][:5])}\n"
    formatted += "\n"
    
    # News
    if news_articles:
        formatted += "📰 RECENT NEWS\n" + "-" * 50 + "\n"
        for article in news_articles[:3]:
            formatted += f"• {article.get('title', 'N/A')}\n"
    
    return formatted


def create_research_summary(company_name: str, industry: Optional[str] = None) -> Dict:
    """
    Create a complete research summary for a company.
    Gathers data from all sources and organizes by ESG category.
    """
    print(f"\n🔍 Starting comprehensive ESG research for {company_name}...")
    
    # Gather data from all sources
    env_results = search_environmental_data(company_name)
    social_results = search_social_data(company_name)
    gov_results = search_governance_data(company_name)
    news_results = search_esg_news(company_name)
    reports = search_esg_reports(company_name)
    compliance = search_company_compliance(company_name)
    
    # Extract metrics from all text
    all_text = " ".join([
        r.get('snippet', '') 
        for r in env_results + social_results + gov_results
    ])
    metrics = extract_esg_metrics_from_text(all_text)
    
    total_results = len(env_results) + len(social_results) + len(gov_results)
    print(f"✅ Research complete: {total_results} total results found")
    
    return {
        "company_name": company_name,
        "industry": industry,
        "timestamp": datetime.now().isoformat(),
        "environmental": {"results": env_results, "count": len(env_results)},
        "social": {"results": social_results, "count": len(social_results)},
        "governance": {"results": gov_results, "count": len(gov_results)},
        "news": {"articles": news_results, "count": len(news_results)},
        "reports": {"official_reports": reports, "count": len(reports)},
        "compliance": {"issues": compliance, "count": len(compliance)},
        "metrics": metrics,
    }


# ========== SCORING FUNCTIONS ==========

def calculate_environmental_score(findings: Dict) -> Dict:
    """
    Calculate environmental ESG score based on evidence found.
    Uses a weighted scoring system that recognizes positive ESG efforts.
    
    Scoring Philosophy:
    - Large companies with sustainability programs typically score 60-80
    - Leaders in sustainability score 80-95
    - Companies with violations or no programs score 30-55
    
    Max points:
    - Emissions/Climate: 30 pts
    - Energy/Renewables: 25 pts
    - Water/Waste/Circular: 20 pts
    - Disclosure/Reporting: 15 pts
    - Compliance/Certifications: 10 pts
    """
    factors = {}
    bonus = 0
    
    # Get results from findings
    if isinstance(findings, dict):
        results = findings.get("results", [])
    elif isinstance(findings, list):
        results = findings
    else:
        results = []
    
    # Base score for having data at all
    if not results:
        return {
            "score": 55,
            "factors": {
                "emissions_climate": 14,
                "energy_renewables": 12,
                "water_waste": 11,
                "disclosure": 10,
                "compliance": 8
            },
            "methodology": "Baseline score applied due to limited publicly available data. Score reflects industry average expectations."
        }
    
    # Combine all text for analysis
    text = " ".join([
        str(r.get("snippet", "")) + " " + str(r.get("title", ""))
        for r in results if isinstance(r, dict)
    ]).lower()
    
    # Check for severe violations (significant penalty only for major issues)
    major_violations = text.count("epa violation") + text.count("environmental disaster") + text.count("major spill")
    minor_issues = text.count("fine") + text.count("penalty")
    penalty = (major_violations * 10) + (minor_issues * 2)
    
    # Emissions/Climate scoring (0-30)
    emissions_score = 12  # Base score
    if "net zero" in text or "carbon neutral" in text:
        emissions_score = 26 if ("achieved" in text or "2030" in text or "2040" in text) else 22
    elif "science based target" in text or "sbti" in text:
        emissions_score = 24
    elif "emissions reduction" in text or "ghg reduction" in text or "carbon reduction" in text:
        emissions_score = 20 if "%" in text else 17
    elif "emissions" in text or "carbon footprint" in text or "greenhouse" in text:
        emissions_score = 15
    elif "sustainability" in text or "environmental" in text:
        emissions_score = 13
    factors["emissions_climate"] = emissions_score
    
    # Energy/Renewables scoring (0-25)
    energy_score = 10  # Base score
    if "100% renewable" in text or "fully renewable" in text:
        energy_score = 23
    elif "renewable energy" in text and ("%" in text or "target" in text):
        energy_score = 20
    elif "solar" in text or "wind" in text or "clean energy" in text:
        energy_score = 17
    elif "energy efficiency" in text or "energy reduction" in text:
        energy_score = 15
    elif "renewable" in text or "energy" in text:
        energy_score = 12
    factors["energy_renewables"] = energy_score
    
    # Water/Waste/Circular Economy scoring (0-20)
    water_waste_score = 8  # Base score
    circular = "circular economy" in text or "zero waste" in text
    water = "water management" in text or "water stewardship" in text or "water reduction" in text
    waste = "waste reduction" in text or "recycling" in text or "waste management" in text
    
    if circular:
        water_waste_score = 18
    elif water and waste:
        water_waste_score = 16
    elif water or waste:
        water_waste_score = 13
    elif "water" in text or "waste" in text:
        water_waste_score = 10
    factors["water_waste"] = water_waste_score
    
    # Disclosure/Reporting scoring (0-15)
    disclosure_score = 7  # Base score
    if "tcfd" in text or "gri" in text or "sasb" in text:
        disclosure_score = 14
    elif "sustainability report" in text or "esg report" in text or "climate disclosure" in text:
        disclosure_score = 12
    elif "disclosure" in text or "reporting" in text or "transparency" in text:
        disclosure_score = 10
    factors["disclosure"] = disclosure_score
    
    # Compliance/Certifications scoring (0-10)
    compliance_score = 6  # Base score
    if major_violations > 0:
        compliance_score = max(2, 6 - (major_violations * 3))
    elif "iso 14001" in text or "leed" in text or "certified" in text:
        compliance_score = 9
    elif "compliance" in text or "certified" in text:
        compliance_score = 7
    factors["compliance"] = compliance_score
    
    # Bonus for leadership indicators
    if "leader" in text or "award" in text or "recognition" in text:
        bonus += 3
    if "innovation" in text and "environmental" in text:
        bonus += 2
    
    # Calculate total
    total = sum(factors.values()) + bonus
    total = max(0, total - penalty)
    final_score = min(95, max(35, total))
    
    return {
        "score": round(final_score, 1),
        "factors": factors,
        "methodology": f"Weighted scoring: Emissions/Climate (30), Energy/Renewables (25), Water/Waste (20), Disclosure (15), Compliance (10). Bonus: {bonus}. Penalty: {penalty}."
    }


def calculate_social_score(findings: Dict) -> Dict:
    """
    Calculate social ESG score based on evidence found.
    
    Scoring Philosophy:
    - Companies with strong DEI and employee programs: 65-85
    - Leaders with comprehensive social programs: 80-95
    - Companies with controversies or limited programs: 35-55
    
    Max points:
    - Diversity & Inclusion: 25 pts
    - Employee Experience: 25 pts
    - Health & Safety: 20 pts
    - Community Impact: 15 pts
    - Supply Chain: 15 pts
    """
    factors = {}
    bonus = 0
    
    if isinstance(findings, dict):
        results = findings.get("results", [])
    elif isinstance(findings, list):
        results = findings
    else:
        results = []
    
    if not results:
        return {
            "score": 55,
            "factors": {
                "diversity_inclusion": 13,
                "employee_experience": 13,
                "health_safety": 11,
                "community": 9,
                "supply_chain": 9
            },
            "methodology": "Baseline score applied due to limited publicly available data. Score reflects industry average expectations."
        }
    
    text = " ".join([
        str(r.get("snippet", "")) + " " + str(r.get("title", ""))
        for r in results if isinstance(r, dict)
    ]).lower()
    
    # Check for serious controversies
    serious_issues = text.count("lawsuit") + text.count("discrimination lawsuit") + text.count("harassment scandal")
    minor_issues = text.count("complaint") + text.count("allegation")
    penalty = (serious_issues * 8) + (minor_issues * 2)
    
    # Diversity & Inclusion scoring (0-25)
    dei_score = 11  # Base score
    if ("diversity" in text or "dei" in text) and "%" in text:
        dei_score = 22
    elif "diversity" in text and ("initiative" in text or "program" in text or "inclusion" in text):
        dei_score = 19
    elif "diversity" in text or "inclusion" in text or "equity" in text:
        dei_score = 15
    elif "equal opportunity" in text:
        dei_score = 13
    factors["diversity_inclusion"] = dei_score
    
    # Employee Experience scoring (0-25)
    emp_score = 11  # Base score
    if "employee engagement" in text and ("%" in text or "score" in text):
        emp_score = 22
    elif "employee satisfaction" in text or "great place to work" in text or "best employer" in text:
        emp_score = 20
    elif "benefits" in text and ("health" in text or "wellness" in text or "retirement" in text):
        emp_score = 17
    elif "training" in text or "development" in text or "career" in text:
        emp_score = 15
    elif "employee" in text or "workplace" in text or "workforce" in text:
        emp_score = 13
    factors["employee_experience"] = emp_score
    
    # Health & Safety scoring (0-20)
    safety_score = 10  # Base score
    if "safety record" in text and ("%" in text or "reduction" in text):
        safety_score = 18
    elif "health and safety" in text or "workplace safety" in text:
        safety_score = 15
    elif "safety" in text or "wellbeing" in text or "wellness" in text:
        safety_score = 13
    factors["health_safety"] = safety_score
    
    # Community Impact scoring (0-15)
    community_score = 8  # Base score
    if "community" in text and ("$" in text or "million" in text or "billion" in text):
        community_score = 14
    elif "philanthropy" in text or "volunteer" in text or "foundation" in text:
        community_score = 12
    elif "community" in text or "social impact" in text:
        community_score = 10
    factors["community"] = community_score
    
    # Supply Chain scoring (0-15)
    supply_score = 8  # Base score
    if "supply chain" in text and ("audit" in text or "certified" in text or "responsible" in text):
        supply_score = 14
    elif "supplier diversity" in text or "ethical sourcing" in text:
        supply_score = 12
    elif "supply chain" in text or "supplier" in text:
        supply_score = 10
    factors["supply_chain"] = supply_score
    
    # Bonus for leadership
    if "award" in text or "recognition" in text or "best" in text:
        bonus += 3
    if "leader" in text and ("social" in text or "diversity" in text):
        bonus += 2
    
    total = sum(factors.values()) + bonus
    total = max(0, total - penalty)
    final_score = min(95, max(35, total))
    
    return {
        "score": round(final_score, 1),
        "factors": factors,
        "methodology": f"Weighted scoring: DEI (25), Employee Experience (25), Health & Safety (20), Community (15), Supply Chain (15). Bonus: {bonus}. Penalty: {penalty}."
    }


def calculate_governance_score(findings: Dict) -> Dict:
    """
    Calculate governance ESG score based on evidence found.
    
    Scoring Philosophy:
    - Companies with strong governance structures: 65-85
    - Governance leaders: 80-95
    - Companies with scandals or weak governance: 35-55
    
    Max points:
    - Board Quality: 25 pts
    - Executive Compensation: 20 pts
    - Risk Management: 20 pts
    - Ethics & Compliance: 20 pts
    - Transparency/Shareholder: 15 pts
    """
    factors = {}
    bonus = 0
    
    if isinstance(findings, dict):
        results = findings.get("results", [])
    elif isinstance(findings, list):
        results = findings
    else:
        results = []
    
    if not results:
        return {
            "score": 58,
            "factors": {
                "board_quality": 14,
                "compensation": 12,
                "risk_management": 12,
                "ethics_compliance": 12,
                "transparency": 8
            },
            "methodology": "Baseline score applied due to limited publicly available data. Score reflects industry average expectations."
        }
    
    text = " ".join([
        str(r.get("snippet", "")) + " " + str(r.get("title", ""))
        for r in results if isinstance(r, dict)
    ]).lower()
    
    # Check for major scandals
    major_scandals = text.count("fraud") + text.count("corruption") + text.count("scandal")
    sec_issues = text.count("sec enforcement") + text.count("sec investigation")
    penalty = (major_scandals * 12) + (sec_issues * 6)
    
    # Board Quality scoring (0-25)
    board_score = 12  # Base score
    if "independent" in text and ("majority" in text or "%" in text):
        board_score = 22
    elif "board diversity" in text or "independent director" in text:
        board_score = 19
    elif "board" in text and ("experience" in text or "expertise" in text):
        board_score = 16
    elif "board" in text or "director" in text:
        board_score = 14
    factors["board_quality"] = board_score
    
    # Executive Compensation scoring (0-20)
    comp_score = 10  # Base score
    if "compensation" in text and ("performance" in text or "aligned" in text or "pay for performance" in text):
        comp_score = 18
    elif "executive compensation" in text or "say on pay" in text:
        comp_score = 14
    elif "compensation" in text:
        comp_score = 12
    factors["compensation"] = comp_score
    
    # Risk Management scoring (0-20)
    risk_score = 10  # Base score
    if "enterprise risk" in text or "risk management framework" in text:
        risk_score = 18
    elif "risk committee" in text or "risk oversight" in text:
        risk_score = 15
    elif "risk management" in text or "risk" in text:
        risk_score = 12
    factors["risk_management"] = risk_score
    
    # Ethics & Compliance scoring (0-20)
    ethics_score = 10  # Base score
    if major_scandals > 0:
        ethics_score = max(3, 10 - (major_scandals * 4))
    elif "ethics program" in text or "code of conduct" in text:
        ethics_score = 17
    elif "whistleblower" in text or "compliance program" in text:
        ethics_score = 15
    elif "ethics" in text or "compliance" in text:
        ethics_score = 12
    factors["ethics_compliance"] = ethics_score
    
    # Transparency/Shareholder scoring (0-15)
    transparency_score = 8  # Base score
    if "shareholder engagement" in text or "investor relations" in text:
        transparency_score = 13
    elif "transparency" in text or "disclosure" in text:
        transparency_score = 11
    elif "shareholder" in text or "stakeholder" in text:
        transparency_score = 9
    factors["transparency"] = transparency_score
    
    # Bonus for leadership
    if "governance leader" in text or "best governance" in text:
        bonus += 4
    if "award" in text and "governance" in text:
        bonus += 2
    
    total = sum(factors.values()) + bonus
    total = max(0, total - penalty)
    final_score = min(95, max(35, total))
    
    return {
        "score": round(final_score, 1),
        "factors": factors,
        "methodology": f"Weighted scoring: Board (25), Compensation (20), Risk Management (20), Ethics (20), Transparency (15). Bonus: {bonus}. Penalty: {penalty}."
    }


def calculate_overall_score(env_score: float, social_score: float, gov_score: float) -> float:
    """Calculate weighted overall ESG score (equal weights for E, S, G)."""
    overall = (env_score + social_score + gov_score) / 3
    return round(overall, 1)
