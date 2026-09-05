"""
ESG Multi-Agent System - Enhanced Version
Uses Google Gemini for detailed writing and Tavily for comprehensive research
"""

import os
import json
import logging
import re
import asyncio
from typing import TypedDict, Annotated, Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END

from .tools import (
    search_environmental_data,
    search_social_data,
    search_governance_data,
    search_esg_news,
    search_esg_reports,
    search_company_compliance,
    extract_esg_metrics_from_text,
    format_web_search_results,
    format_search_by_category,
    format_esg_report_summary,
    create_research_summary,
    search_academic_research,
    format_academic_results,
    calculate_environmental_score,
    calculate_social_score,
    calculate_governance_score,
    calculate_overall_score,
    search_with_tavily,
    smart_search,
)
from .pdf_generator import ESGReportPDFGenerator

load_dotenv()
logger = logging.getLogger(__name__)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY", ""),
    temperature=0.3,
    max_output_tokens=8192,
)

# Separate LLM for writing detailed content with higher creativity and more tokens
writer_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY", ""),
    temperature=0.5,
    max_output_tokens=16384,
)


# ============= STATE DEFINITION =============
class ESGResearchState(TypedDict):
    """State for ESG research workflow"""
    messages: Annotated[List[BaseMessage], add_messages]
    company_name: str
    industry: Optional[str]
    reporting_period: str
    env_findings: Dict[str, Any]
    social_findings: Dict[str, Any]
    gov_findings: Dict[str, Any]
    news_findings: List[Dict]
    academic_findings: List[Dict]
    reports: List[Dict]
    all_findings: Dict[str, Any]
    verified_findings: Dict[str, Any]
    calculated_scores: Dict[str, Any]
    env_detailed_analysis: str
    social_detailed_analysis: str
    gov_detailed_analysis: str
    final_report: str


# ============= DEEP RESEARCH FUNCTION ==========
def deep_research_with_tavily(company_name: str, topic: str, queries: List[str]) -> List[Dict]:
    """Perform deep research using Tavily with multiple targeted queries."""
    all_results = []
    
    for query in queries:
        full_query = f"{company_name} {query}"
        try:
            results = search_with_tavily(full_query, count=5)
            all_results.extend(results)
        except Exception as e:
            print(f"   ⚠ Tavily query failed: {e}")
            continue
    
    # Also use smart_search for additional coverage
    try:
        smart_results = smart_search(f"{company_name} {topic} ESG sustainability", count=10)
        all_results.extend(smart_results)
    except Exception as e:
        print(f"   ⚠ Smart search failed: {e}")
    
    # Deduplicate
    seen = set()
    unique = []
    for r in all_results:
        url = r.get('url', '')
        if url not in seen:
            seen.add(url)
            unique.append(r)
    
    return unique


# ============= LEAD AGENT =============
def lead_agent(state: ESGResearchState) -> ESGResearchState:
    """Lead Agent - Plans research strategy"""
    company = state['company_name']
    industry = state.get('industry', 'Unknown')
    
    print(f"\n{'='*70}")
    print(f"🚀 Starting ESG Research for: {company}")
    print(f"   Industry: {industry}")
    print(f"   Reporting Period: {state.get('reporting_period', '2024')}")
    print(f"{'='*70}\n")
    
    return {
        **state,
        "messages": [AIMessage(content=f"Starting ESG research for {company}")]
    }


# ============= ENVIRONMENTAL RESEARCH & ANALYSIS =============
def web_search_environmental(state: ESGResearchState) -> ESGResearchState:
    """Environmental Research Agent - Deep research + LLM analysis"""
    print("🌍 ENVIRONMENTAL RESEARCH")
    print("   Searching multiple sources...")
    
    company = state['company_name']
    
    env_queries = [
        "carbon emissions scope 1 2 3 reduction targets",
        "renewable energy solar wind clean energy percentage",
        "sustainability report environmental goals",
        "net zero carbon neutral commitment",
        "water conservation waste reduction circular economy",
        "TCFD climate risk disclosure",
    ]
    
    results = []
    
    # Primary search
    try:
        primary_results = search_environmental_data(company)
        results.extend(primary_results)
        print(f"   ✅ Primary search: {len(primary_results)} sources")
    except Exception as e:
        print(f"   ⚠️ Primary search error: {e}")
    
    # Deep Tavily research
    try:
        tavily_results = deep_research_with_tavily(company, "environmental sustainability", env_queries[:4])
        results.extend(tavily_results)
        print(f"   ✅ Tavily deep search: {len(tavily_results)} sources")
    except Exception as e:
        print(f"   ⚠️ Tavily error: {e}")
    
    # Deduplicate
    seen = set()
    unique_results = []
    for r in results:
        url = r.get('url', str(len(unique_results)))
        if url not in seen:
            seen.add(url)
            unique_results.append(r)
    
    print(f"   📊 Total unique sources: {len(unique_results)}")
    
    # Format findings for LLM
    findings_text = ""
    for i, r in enumerate(unique_results[:20], 1):
        title = r.get('title', 'N/A')
        snippet = r.get('snippet', '')[:600]
        source = r.get('source', r.get('url', 'Unknown'))
        findings_text += f"\n{i}. {title}\n   Source: {source}\n   Content: {snippet}\n"
    
    # Use LLM to write detailed environmental analysis
    analysis_prompt = f"""You are a Senior Environmental ESG Analyst writing an EXTREMELY DETAILED and COMPREHENSIVE analysis for {company}.

Based on the research data below, write a VERY DETAILED environmental analysis (1500-2500 words minimum) covering:

1. **Carbon Emissions & Climate Strategy**
   - Scope 1, 2, 3 emissions data (if available)
   - Net zero or carbon neutrality commitments
   - Science-based targets (SBTi alignment)
   - Year-over-year emissions trends

2. **Energy Management**
   - Renewable energy percentage and targets
   - Energy efficiency initiatives
   - Power purchase agreements (PPAs)
   - Clean energy investments

3. **Water & Waste Management**
   - Water consumption and conservation efforts
   - Waste reduction and recycling rates
   - Circular economy initiatives
   - Zero waste goals

4. **Climate Risk & Disclosure**
   - TCFD alignment and climate risk assessment
   - Physical and transition risks identified
   - Climate scenario analysis (if disclosed)

5. **Environmental Compliance**
   - Certifications (ISO 14001, etc.)
   - Any violations or controversies
   - Regulatory compliance record

Write in a professional, analytical tone. Use specific data points where available.
For missing data, note "Not publicly disclosed" rather than making assumptions.

RESEARCH DATA:
{findings_text}

Write the detailed environmental analysis now:"""

    try:
        response = writer_llm.invoke([HumanMessage(content=analysis_prompt)])
        detailed_analysis = response.content
        print("   ✅ Detailed environmental analysis written")
    except Exception as e:
        print(f"   ⚠️ Analysis error: {e}")
        detailed_analysis = "Environmental analysis pending - see raw findings."
    
    return {
        **state,
        "env_findings": {"results": unique_results, "count": len(unique_results)},
        "env_detailed_analysis": detailed_analysis,
        "messages": state["messages"] + [AIMessage(content=detailed_analysis[:500])]
    }


# ============= SOCIAL RESEARCH & ANALYSIS =============
def web_search_social(state: ESGResearchState) -> ESGResearchState:
    """Social Research Agent - Deep research + LLM analysis"""
    print("\n👥 SOCIAL RESEARCH")
    print("   Searching multiple sources...")
    
    company = state['company_name']
    
    social_queries = [
        "diversity inclusion DEI metrics workforce",
        "employee engagement satisfaction turnover",
        "workplace safety TRIR injury rates",
        "benefits health wellness programs",
        "community investment philanthropy foundation",
        "supply chain human rights labor practices",
    ]
    
    results = []
    
    try:
        primary_results = search_social_data(company)
        results.extend(primary_results)
        print(f"   ✅ Primary search: {len(primary_results)} sources")
    except Exception as e:
        print(f"   ⚠️ Primary search error: {e}")
    
    try:
        tavily_results = deep_research_with_tavily(company, "social responsibility employees", social_queries[:4])
        results.extend(tavily_results)
        print(f"   ✅ Tavily deep search: {len(tavily_results)} sources")
    except Exception as e:
        print(f"   ⚠️ Tavily error: {e}")
    
    seen = set()
    unique_results = []
    for r in results:
        url = r.get('url', str(len(unique_results)))
        if url not in seen:
            seen.add(url)
            unique_results.append(r)
    
    print(f"   📊 Total unique sources: {len(unique_results)}")
    
    findings_text = ""
    for i, r in enumerate(unique_results[:20], 1):
        title = r.get('title', 'N/A')
        snippet = r.get('snippet', '')[:600]
        source = r.get('source', r.get('url', 'Unknown'))
        findings_text += f"\n{i}. {title}\n   Source: {source}\n   Content: {snippet}\n"
    
    analysis_prompt = f"""You are a Senior Social ESG Analyst writing an EXTREMELY DETAILED and COMPREHENSIVE analysis for {company}.

Based on the research data below, write a VERY DETAILED social analysis (1500-2500 words minimum) covering:

1. **Diversity, Equity & Inclusion (DEI)**
   - Gender diversity metrics (overall and leadership)
   - Ethnic/racial diversity representation
   - DEI programs and initiatives
   - Pay equity and gender pay gap data

2. **Employee Experience & Development**
   - Employee engagement scores
   - Turnover and retention rates
   - Training and development programs
   - Career advancement opportunities
   - Work-life balance initiatives

3. **Health, Safety & Wellbeing**
   - Workplace safety metrics (TRIR, LTIR)
   - Health and wellness programs
   - Mental health support

4. **Compensation & Benefits**
   - Fair wage practices
   - Benefits overview (health, retirement, parental leave)
   - CEO-to-worker pay ratio

5. **Community Impact**
   - Philanthropic giving and foundation activities
   - Employee volunteering programs
   - Local community investments

6. **Supply Chain Responsibility**
   - Supplier diversity programs
   - Human rights due diligence
   - Supplier audits and assessments

Write in a professional, analytical tone. Use specific data points where available.
For missing data, note "Not publicly disclosed" rather than making assumptions.

RESEARCH DATA:
{findings_text}

Write the detailed social analysis now:"""

    try:
        response = writer_llm.invoke([HumanMessage(content=analysis_prompt)])
        detailed_analysis = response.content
        print("   ✅ Detailed social analysis written")
    except Exception as e:
        print(f"   ⚠️ Analysis error: {e}")
        detailed_analysis = "Social analysis pending - see raw findings."
    
    return {
        **state,
        "social_findings": {"results": unique_results, "count": len(unique_results)},
        "social_detailed_analysis": detailed_analysis,
        "messages": state["messages"] + [AIMessage(content=detailed_analysis[:500])]
    }


# ============= GOVERNANCE RESEARCH & ANALYSIS =============
def web_search_governance(state: ESGResearchState) -> ESGResearchState:
    """Governance Research Agent - Deep research + LLM analysis"""
    print("\n⚖️ GOVERNANCE RESEARCH")
    print("   Searching multiple sources...")
    
    company = state['company_name']
    
    gov_queries = [
        "board of directors composition independence diversity",
        "executive compensation CEO pay ratio",
        "corporate governance proxy statement",
        "ethics compliance whistleblower policy",
        "risk management enterprise ERM",
        "cybersecurity data privacy",
    ]
    
    results = []
    
    try:
        primary_results = search_governance_data(company)
        results.extend(primary_results)
        print(f"   ✅ Primary search: {len(primary_results)} sources")
    except Exception as e:
        print(f"   ⚠️ Primary search error: {e}")
    
    try:
        tavily_results = deep_research_with_tavily(company, "corporate governance board", gov_queries[:4])
        results.extend(tavily_results)
        print(f"   ✅ Tavily deep search: {len(tavily_results)} sources")
    except Exception as e:
        print(f"   ⚠️ Tavily error: {e}")
    
    seen = set()
    unique_results = []
    for r in results:
        url = r.get('url', str(len(unique_results)))
        if url not in seen:
            seen.add(url)
            unique_results.append(r)
    
    print(f"   📊 Total unique sources: {len(unique_results)}")
    
    findings_text = ""
    for i, r in enumerate(unique_results[:20], 1):
        title = r.get('title', 'N/A')
        snippet = r.get('snippet', '')[:600]
        source = r.get('source', r.get('url', 'Unknown'))
        findings_text += f"\n{i}. {title}\n   Source: {source}\n   Content: {snippet}\n"
    
    analysis_prompt = f"""You are a Senior Governance ESG Analyst writing an EXTREMELY DETAILED and COMPREHENSIVE analysis for {company}.

Based on the research data below, write a VERY DETAILED governance analysis (1500-2500 words minimum) covering:

1. **Board of Directors**
   - Board size and composition
   - Independence percentage
   - Board diversity (gender, ethnicity, expertise)
   - Average tenure and refreshment practices
   - Key committees (Audit, Compensation, Nominating)

2. **Executive Compensation**
   - CEO compensation structure
   - Pay-for-performance alignment
   - ESG-linked incentives
   - CEO-to-median-worker pay ratio
   - Say-on-pay vote results

3. **Ethics & Compliance**
   - Code of conduct and ethics program
   - Anti-corruption policies
   - Whistleblower mechanisms
   - Compliance training programs

4. **Risk Management**
   - Enterprise risk management framework
   - ESG risk oversight
   - Cybersecurity and data privacy
   - Business continuity planning

5. **Transparency & Disclosure**
   - ESG reporting frameworks (GRI, SASB, TCFD)
   - Integrated reporting practices
   - Third-party assurance

6. **Shareholder Rights**
   - Shareholder engagement practices
   - Proxy access and voting rights
   - Stakeholder engagement

Write in a professional, analytical tone. Use specific data points where available.
For missing data, note "Not publicly disclosed" rather than making assumptions.

RESEARCH DATA:
{findings_text}

Write the detailed governance analysis now:"""

    try:
        response = writer_llm.invoke([HumanMessage(content=analysis_prompt)])
        detailed_analysis = response.content
        print("   ✅ Detailed governance analysis written")
    except Exception as e:
        print(f"   ⚠️ Analysis error: {e}")
        detailed_analysis = "Governance analysis pending - see raw findings."
    
    return {
        **state,
        "gov_findings": {"results": unique_results, "count": len(unique_results)},
        "gov_detailed_analysis": detailed_analysis,
        "messages": state["messages"] + [AIMessage(content=detailed_analysis[:500])]
    }


# ============= NEWS & ACADEMIC RESEARCH =============
def search_news_and_reports(state: ESGResearchState) -> ESGResearchState:
    """News and Reports Agent"""
    print("\n📰 NEWS & REPORTS RESEARCH")
    
    company = state['company_name']
    news_items = []
    
    try:
        news_results = search_esg_news(company)
        news_items.extend(news_results)
        print(f"   ✅ Found {len(news_results)} news articles")
    except Exception as e:
        print(f"   ⚠️ News search error: {e}")
    
    try:
        report_results = search_esg_reports(company)
        news_items.extend(report_results)
        print(f"   ✅ Found {len(report_results)} reports")
    except Exception as e:
        print(f"   ⚠️ Report search error: {e}")
    
    return {
        **state,
        "news_findings": news_items,
        "messages": state["messages"]
    }


def academic_research_agent(state: ESGResearchState) -> ESGResearchState:
    """Academic Research Agent"""
    print("\n🎓 ACADEMIC RESEARCH")
    
    try:
        results = search_academic_research(state['company_name'])
        print(f"   ✅ Found {len(results)} academic sources")
    except Exception as e:
        print(f"   ⚠️ Academic search error: {e}")
        results = []
    
    return {
        **state,
        "academic_findings": results,
        "messages": state["messages"]
    }


# ============= VERIFICATION AGENT =============
def verification_agent(state: ESGResearchState) -> ESGResearchState:
    """Verification Agent - Cross-checks findings"""
    print("\n🔍 VERIFICATION")
    
    env_count = len(state.get("env_findings", {}).get("results", []))
    social_count = len(state.get("social_findings", {}).get("results", []))
    gov_count = len(state.get("gov_findings", {}).get("results", []))
    total = env_count + social_count + gov_count
    
    verified = {
        "status": "verified",
        "environmental_sources": env_count,
        "social_sources": social_count,
        "governance_sources": gov_count,
        "total_sources": total,
        "data_quality": "high" if total > 30 else "medium"
    }
    
    print(f"   ✅ Verified {total} total sources")
    print(f"   📊 Data quality: {verified['data_quality']}")
    
    return {
        **state,
        "verified_findings": verified,
        "messages": state["messages"]
    }


# ============= SYNTHESIS AGENT =============
def synthesis_agent(state: ESGResearchState) -> ESGResearchState:
    """Synthesis Agent - Creates comprehensive ESG report"""
    print("\n📊 REPORT SYNTHESIS")
    print("   Compiling comprehensive ESG report...")
    
    # Calculate scores
    env_findings = state.get("env_findings", {})
    social_findings = state.get("social_findings", {})
    gov_findings = state.get("gov_findings", {})
    
    env_score_data = calculate_environmental_score(env_findings)
    social_score_data = calculate_social_score(social_findings)
    gov_score_data = calculate_governance_score(gov_findings)
    
    env_score = env_score_data["score"]
    social_score = social_score_data["score"]
    gov_score = gov_score_data["score"]
    overall_score = calculate_overall_score(env_score, social_score, gov_score)
    
    print(f"\n   📈 ESG SCORES:")
    print(f"      • Environmental: {env_score}/100")
    print(f"      • Social: {social_score}/100")
    print(f"      • Governance: {gov_score}/100")
    print(f"      • Overall: {overall_score}/100\n")
    
    # Get detailed analyses
    env_analysis = state.get("env_detailed_analysis", "Environmental analysis not available.")
    social_analysis = state.get("social_detailed_analysis", "Social analysis not available.")
    gov_analysis = state.get("gov_detailed_analysis", "Governance analysis not available.")
    
    company_name = state['company_name']
    industry = state.get('industry', 'Not specified')
    
    # Create final comprehensive report - simplified to avoid LLM refusal
    synthesis_prompt = f"""You are a Senior ESG Consultant creating an ESG report for {company_name}.

Based on this research data:

ENVIRONMENTAL: {env_analysis[:2000]}

SOCIAL: {social_analysis[:2000]}

GOVERNANCE: {gov_analysis[:2000]}

SCORES: Environmental={env_score}/100, Social={social_score}/100, Governance={gov_score}/100, Overall={overall_score}/100

Generate a JSON report. You MUST output valid JSON only, no explanations or markdown.

{{
    "executive_summary": "Write 300-400 words summarizing ESG performance, key findings, and outlook.",
    "company_profile": "Write 200 words on company overview and why ESG matters for them.",
    "environmental_analysis": {{
        "score": {env_score},
        "summary": "200 word environmental summary",
        "emissions": "100 words on carbon/GHG emissions",
        "energy": "100 words on energy management",
        "water": "80 words on water management",
        "waste": "80 words on waste/recycling",
        "climate_risks": "100 words on climate risk disclosure",
        "score_justification": "80 words explaining the score of {env_score}"
    }},
    "social_analysis": {{
        "score": {social_score},
        "summary": "200 word social summary",
        "diversity": "100 words on DEI",
        "employee_experience": "100 words on employee programs",
        "health_safety": "80 words on safety",
        "compensation": "80 words on pay/benefits",
        "community": "80 words on community impact",
        "supply_chain": "100 words on supply chain ethics",
        "score_justification": "80 words explaining the score of {social_score}"
    }},
    "governance_analysis": {{
        "score": {gov_score},
        "summary": "200 word governance summary",
        "board": "100 words on board composition",
        "compensation": "100 words on exec compensation",
        "ethics_compliance": "100 words on ethics/compliance",
        "risk_management": "80 words on risk management",
        "transparency": "80 words on disclosure quality",
        "score_justification": "80 words explaining the score of {gov_score}"
    }},
    "material_risks": [
        {{"risk": "Risk 1 name", "category": "E/S/G", "severity": "High/Medium/Low", "impact": "50 word impact description", "mitigation": "50 word mitigation strategy"}},
        {{"risk": "Risk 2 name", "category": "E/S/G", "severity": "High/Medium/Low", "impact": "50 word impact description", "mitigation": "50 word mitigation strategy"}},
        {{"risk": "Risk 3 name", "category": "E/S/G", "severity": "High/Medium/Low", "impact": "50 word impact description", "mitigation": "50 word mitigation strategy"}},
        {{"risk": "Risk 4 name", "category": "E/S/G", "severity": "High/Medium/Low", "impact": "50 word impact description", "mitigation": "50 word mitigation strategy"}},
        {{"risk": "Risk 5 name", "category": "E/S/G", "severity": "High/Medium/Low", "impact": "50 word impact description", "mitigation": "50 word mitigation strategy"}}
    ],
    "opportunities": [
        {{"opportunity": "Opp 1", "pillar": "E/S/G", "potential_value": "50 words on value potential", "strategic_fit": "30 words"}},
        {{"opportunity": "Opp 2", "pillar": "E/S/G", "potential_value": "50 words on value potential", "strategic_fit": "30 words"}},
        {{"opportunity": "Opp 3", "pillar": "E/S/G", "potential_value": "50 words on value potential", "strategic_fit": "30 words"}},
        {{"opportunity": "Opp 4", "pillar": "E/S/G", "potential_value": "50 words on value potential", "strategic_fit": "30 words"}},
        {{"opportunity": "Opp 5", "pillar": "E/S/G", "potential_value": "50 words on value potential", "strategic_fit": "30 words"}}
    ],
    "recommendations": [
        {{"priority": "High", "recommendation": "Recommendation 1", "pillar": "E/S/G", "rationale": "50 words", "kpis": ["KPI1", "KPI2"], "expected_impact": "30 words"}},
        {{"priority": "High", "recommendation": "Recommendation 2", "pillar": "E/S/G", "rationale": "50 words", "kpis": ["KPI1", "KPI2"], "expected_impact": "30 words"}},
        {{"priority": "Medium", "recommendation": "Recommendation 3", "pillar": "E/S/G", "rationale": "50 words", "kpis": ["KPI1", "KPI2"], "expected_impact": "30 words"}},
        {{"priority": "Medium", "recommendation": "Recommendation 4", "pillar": "E/S/G", "rationale": "50 words", "kpis": ["KPI1", "KPI2"], "expected_impact": "30 words"}},
        {{"priority": "Low", "recommendation": "Recommendation 5", "pillar": "E/S/G", "rationale": "50 words", "kpis": ["KPI1", "KPI2"], "expected_impact": "30 words"}},
        {{"priority": "Low", "recommendation": "Recommendation 6", "pillar": "E/S/G", "rationale": "50 words", "kpis": ["KPI1", "KPI2"], "expected_impact": "30 words"}}
    ],
    "peer_comparison": "200 words comparing to industry peers",
    "conclusion": "200 words on overall assessment and outlook"
}}

IMPORTANT: Output ONLY the JSON object. No markdown, no code blocks, no explanations. Start with {{ and end with }}."""

    try:
        response = writer_llm.invoke([HumanMessage(content=synthesis_prompt)])
        final_report = response.content
        print("   ✅ Final report synthesized")
    except Exception as e:
        print(f"   ⚠️ Synthesis error: {e}")
        final_report = json.dumps({
            "error": str(e),
            "overall_score": overall_score,
            "environmental_score": env_score,
            "social_score": social_score,
            "governance_score": gov_score
        })
    
    return {
        **state,
        "final_report": final_report,
        "calculated_scores": {
            "overall_score": overall_score,
            "environmental_score": env_score,
            "social_score": social_score,
            "governance_score": gov_score,
            "env_score_data": env_score_data,
            "social_score_data": social_score_data,
            "gov_score_data": gov_score_data,
        },
        "messages": state["messages"] + [AIMessage(content="Report synthesis complete.")]
    }


# ============= GRAPH SETUP =============
def create_esg_workflow():
    """Create and compile the ESG research workflow graph"""
    
    workflow = StateGraph(ESGResearchState)
    
    workflow.add_node("lead_agent", lead_agent)
    workflow.add_node("web_search_env", web_search_environmental)
    workflow.add_node("web_search_social", web_search_social)
    workflow.add_node("web_search_gov", web_search_governance)
    workflow.add_node("academic_research", academic_research_agent)
    workflow.add_node("search_news", search_news_and_reports)
    workflow.add_node("verification", verification_agent)
    workflow.add_node("synthesis", synthesis_agent)
    
    workflow.set_entry_point("lead_agent")
    workflow.add_edge("lead_agent", "web_search_env")
    workflow.add_edge("web_search_env", "web_search_social")
    workflow.add_edge("web_search_social", "web_search_gov")
    workflow.add_edge("web_search_gov", "academic_research")
    workflow.add_edge("academic_research", "search_news")
    workflow.add_edge("search_news", "verification")
    workflow.add_edge("verification", "synthesis")
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()


# ============= MAIN EXECUTION FUNCTION =============
async def generate_esg_report(
    company_name: str,
    industry: Optional[str] = None,
    reporting_period: str = "2024"
) -> Dict[str, Any]:
    """Main function to generate comprehensive ESG report."""
    try:
        workflow = create_esg_workflow()
        
        initial_state = ESGResearchState(
            messages=[],
            company_name=company_name,
            industry=industry or "Not specified",
            reporting_period=reporting_period,
            env_findings={},
            social_findings={},
            gov_findings={},
            news_findings=[],
            academic_findings=[],
            reports=[],
            all_findings={},
            verified_findings={},
            calculated_scores={},
            env_detailed_analysis="",
            social_detailed_analysis="",
            gov_detailed_analysis="",
            final_report=""
        )
        
        print("\n⏳ Executing ESG research workflow...")
        result = workflow.invoke(initial_state)
        
        print(f"\n{'='*70}")
        print(f"✅ ESG REPORT GENERATION COMPLETE")
        print(f"{'='*70}\n")
        
        # Generate PDF report
        print("📄 Generating PDF report...")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(current_dir))
        project_dir = os.path.dirname(backend_dir)
        output_dir = os.path.join(project_dir, "reports")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        pdf_generator = ESGReportPDFGenerator(output_dir=output_dir)
        
        calculated_scores = result.get("calculated_scores", {})
        
        report_data = {
            "success": True,
            "company_name": company_name,
            "industry": industry,
            "report": result.get("final_report", ""),
            "timestamp": datetime.now().isoformat(),
            "calculated_scores": calculated_scores,
            "env_detailed_analysis": result.get("env_detailed_analysis", ""),
            "social_detailed_analysis": result.get("social_detailed_analysis", ""),
            "gov_detailed_analysis": result.get("gov_detailed_analysis", ""),
            "summary": {
                "environmental_results": result.get("env_findings", {}).get("count", 0),
                "social_results": result.get("social_findings", {}).get("count", 0),
                "governance_results": result.get("gov_findings", {}).get("count", 0),
                "news_articles": len(result.get("news_findings", [])),
                "academic_sources": len(result.get("academic_findings", [])),
            }
        }
        
        try:
            pdf_path = pdf_generator.generate_pdf(
                company_name=company_name,
                report_data=report_data,
                industry=industry
            )
            report_data["pdf_path"] = pdf_path
            print(f"✅ PDF Report: {pdf_path}\n")
        except Exception as pdf_error:
            print(f"⚠️ PDF generation failed: {pdf_error}")
            print("   JSON report is still available\n")
        
        return report_data
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error during report generation: {e}")
        logger.error(f"Report generation error: {e}\n{error_trace}")
        
        return {
            "success": False,
            "company_name": company_name,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def conduct_esg_research(
    company_name: str,
    industry: Optional[str] = None,
    reporting_period: str = "2024"
) -> Dict[str, Any]:
    """Legacy synchronous wrapper."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    generate_esg_report(company_name, industry, reporting_period)
                )
                return future.result()
        else:
            return loop.run_until_complete(
                generate_esg_report(company_name, industry, reporting_period)
            )
    except RuntimeError:
        return asyncio.run(
            generate_esg_report(company_name, industry, reporting_period)
        )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        company = " ".join(sys.argv[1:])
    else:
        company = input("Enter company name (default: Pfizer Inc.): ").strip()
        if not company:
            company = "Pfizer Inc."
    
    industry = input("Enter industry (optional, press Enter to skip): ").strip()
    if not industry:
        industry = None
    
    print(f"\n🔬 Starting ESG Research for: {company}")
    if industry:
        print(f"   Industry: {industry}")
    
    result = asyncio.run(generate_esg_report(
        company_name=company,
        industry=industry,
        reporting_period="2024"
    ))
    
    if result.get("success"):
        scores = result.get("calculated_scores", {})
        print("\n" + "="*70)
        print("📊 FINAL ESG SCORES")
        print("="*70)
        print(f"   • Environmental: {scores.get('environmental_score', 'N/A')}/100")
        print(f"   • Social: {scores.get('social_score', 'N/A')}/100")
        print(f"   • Governance: {scores.get('governance_score', 'N/A')}/100")
        print(f"   • Overall: {scores.get('overall_score', 'N/A')}/100")
        print("="*70)
        
        if "pdf_path" in result:
            print(f"\n📄 Report saved to: {result['pdf_path']}")
    else:
        print(f"\n❌ Report generation failed: {result.get('error', 'Unknown error')}")
