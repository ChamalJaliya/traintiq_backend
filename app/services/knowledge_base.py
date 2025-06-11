"""
TraintiQ Knowledge Base - 10 Sample Q&A with Knowledge Graph
"""

from typing import Dict, List, Any, Optional
import json

class KnowledgeBase:
    def __init__(self):
        self.qa_database = self._load_qa_database()
        self.knowledge_graph = self._build_knowledge_graph()
    
    def _load_qa_database(self) -> List[Dict[str, Any]]:
        """Load 10 curated Q&A pairs for TraintiQ"""
        return [
            {
                "id": 1,
                "question": "What services does TraintiQ offer?",
                "intent": "services",
                "answer": """🚀 **TraintiQ offers comprehensive AI-powered HR solutions:**

• **AI-Powered CV Analysis** - Advanced resume screening using GPT-4 technology
• **Employee Profile Generation** - Automated creation of comprehensive employee profiles  
• **Skills Assessment & Matching** - Intelligent matching of candidates to roles
• **Training Program Optimization** - AI-driven personalization of learning paths

Our platform streamlines recruitment, enhances employee development, and optimizes talent management through cutting-edge artificial intelligence.

*Would you like to learn more about any specific service?*""",
                "quick_replies": ["CV Analysis", "Skills Matching", "Pricing", "Demo"],
                "keywords": ["services", "offer", "solutions", "products"],
                "category": "services"
            },
            {
                "id": 2,
                "question": "Tell me about your pricing plans",
                "intent": "pricing", 
                "answer": """💰 **TraintiQ Pricing Plans:**

**Starter Plan - $29/month**
• Basic CV Analysis (up to 100 profiles)
• Standard reporting
• Email support

**Professional Plan - $99/month**
• Unlimited CV Analysis
• Advanced analytics
• Priority support
• API access

**Enterprise Plan - Custom Pricing**
• Full platform access
• Custom AI training
• Dedicated support
• On-premise deployment

*Ready to start with a free trial?*""",
                "quick_replies": ["Free Trial", "Compare Plans", "Enterprise", "Contact Sales"],
                "keywords": ["pricing", "plans", "cost", "price"],
                "category": "pricing"
            },
            {
                "id": 3,
                "question": "How can I contact support?",
                "intent": "contact",
                "answer": """📞 **TraintiQ Support:**

**Contact Methods:**
• **Support Email:** support@traintiq.com
• **Sales:** sales@traintiq.com  
• **Phone:** 1-800-TRAINTIQ
• **Website:** https://traintiq.com

**Response Times:**
• Support: Within 4 hours
• Sales: Within 1 hour

*What type of assistance do you need?*""",
                "quick_replies": ["Technical Support", "Sales Inquiry", "Live Chat", "Documentation"],
                "keywords": ["contact", "support", "help", "email"],
                "category": "contact"
            },
            {
                "id": 4,
                "question": "What makes TraintiQ different?",
                "intent": "differentiation",
                "answer": """🌟 **What Sets TraintiQ Apart:**

• **Advanced AI:** Powered by GPT-4 and custom models
• **Comprehensive Solution:** End-to-end HR automation
• **Proven Results:** 40% reduction in hiring time
• **Security First:** SOC 2 and GDPR compliant
• **Industry Expertise:** Built by HR technology veterans

*Ready to see the difference? Let's schedule a demo!*""",
                "quick_replies": ["Schedule Demo", "Case Studies", "Security Info", "Customer Reviews"],
                "keywords": ["different", "unique", "better", "advantage"],
                "category": "differentiation"
            },
            {
                "id": 5,
                "question": "Can I get a demo?",
                "intent": "demo",
                "answer": """🎯 **Demo Options:**

**Live Demo (Recommended)**
• 30-minute guided tour
• Customized to your needs
• Q&A with product expert

**Free Trial**
• 14-day full access
• 50 CV analyses included
• No credit card required

**Self-Guided Tour**
• Interactive product walkthrough
• Available immediately

*Which option works best for you?*""",
                "quick_replies": ["Live Demo", "Free Trial", "Self-Guided", "Contact Sales"],
                "keywords": ["demo", "trial", "test", "preview"],
                "category": "demo"
            },
            {
                "id": 6,
                "question": "What industries do you serve?",
                "intent": "industries",
                "answer": """🏢 **Industries We Serve:**

**Primary Sectors:**
• Technology Companies
• Healthcare Organizations
• Financial Services  
• Manufacturing
• Education

**Success Examples:**
• Tech company: 45% faster hiring
• Hospital system: 30% better retention
• Financial firm: 200% recruitment scale

*What industry are you in? I can share specific examples!*""",
                "quick_replies": ["Technology", "Healthcare", "Financial", "Manufacturing"],
                "keywords": ["industries", "sectors", "companies"],
                "category": "industries"
            },
            {
                "id": 7,
                "question": "How does your AI work?",
                "intent": "technology",
                "answer": """🔬 **TraintiQ AI Technology:**

**Core Components:**
• **GPT-4 Foundation** - Latest OpenAI technology
• **Custom Models** - Fine-tuned for HR tasks
• **ML Pipeline** - Continuous learning

**Process:**
1. Document processing & text extraction
2. Skill identification using NLP
3. Experience mapping & analysis
4. Compatibility scoring & matching

**Security:** End-to-end encryption and privacy protection

*Want technical details? Our engineering team can help!*""",
                "quick_replies": ["Technical Demo", "API Docs", "Security", "Integration"],
                "keywords": ["AI", "technology", "how", "work"],
                "category": "technology"
            },
            {
                "id": 8,
                "question": "What are your company values?",
                "intent": "culture",
                "answer": """🌟 **TraintiQ Values & Culture:**

**Core Values:**
• Innovation & Excellence
• Collaboration & Teamwork
• Continuous Learning
• Work-Life Balance

**Work Environment:**
• Remote-first culture
• Flexible hours
• Unlimited PTO
• $3,000 learning budget

**Benefits:**
• Competitive salary + equity
• Comprehensive healthcare
• Latest technology equipment

*Interested in joining our team?*""",
                "quick_replies": ["Careers", "Benefits", "Team", "Mission"],
                "keywords": ["culture", "values", "company", "team"],
                "category": "culture"
            },
            {
                "id": 9,
                "question": "Do you offer integrations?",
                "intent": "integrations",
                "answer": """🔗 **Integration & API Solutions:**

**Pre-built Integrations:**
• ATS Systems (Workday, BambooHR)
• HRIS Platforms (SAP, Oracle)
• Communication (Slack, Teams)

**API Access:**
• RESTful API endpoints
• Real-time webhooks
• SDKs for Python, JavaScript
• Comprehensive documentation

**Custom Development:**
• Enterprise solutions
• Legacy system support
• Dedicated engineering team

*Need a specific integration?*""",
                "quick_replies": ["API Docs", "Integration List", "Custom Dev", "Technical Support"],
                "keywords": ["integration", "API", "connect", "sync"],
                "category": "integrations"
            },
            {
                "id": 10,
                "question": "How secure is my data?",
                "intent": "security",
                "answer": """🔒 **Enterprise Security:**

**Compliance:**
• SOC 2 Type II certified
• GDPR compliant
• ISO 27001 standards

**Data Protection:**
• AES-256 encryption
• Zero-knowledge architecture
• Multi-factor authentication
• Regular security audits

**Privacy:**
• You own your data
• No data mining
• Right to delete
• Transparent policies

*Need security documentation for your team?*""",
                "quick_replies": ["Security Docs", "Compliance", "Data Agreement", "Privacy Policy"],
                "keywords": ["security", "data", "privacy", "safe"],
                "category": "security"
            }
        ]
    
    def _build_knowledge_graph(self) -> Dict[str, Any]:
        """Knowledge graph mapping concepts and relationships"""
        return {
            "entities": {
                "TraintiQ": {
                    "type": "company",
                    "attributes": ["HR Technology", "AI Solutions", "Founded 2020"],
                    "connects_to": ["services", "pricing", "technology"]
                },
                "AI_Technology": {
                    "type": "technology", 
                    "attributes": ["GPT-4", "Machine Learning", "NLP"],
                    "connects_to": ["services", "security", "integrations"]
                },
                "Services": {
                    "type": "offerings",
                    "attributes": ["CV Analysis", "Skills Matching", "Training"],
                    "connects_to": ["pricing", "technology", "industries"]
                },
                "Security": {
                    "type": "compliance",
                    "attributes": ["SOC 2", "GDPR", "Encryption"],
                    "connects_to": ["data", "privacy", "technology"]
                }
            },
            "relationships": {
                "services_powered_by_technology": 0.9,
                "pricing_includes_services": 0.8, 
                "technology_ensures_security": 0.9,
                "security_enables_compliance": 0.8
            }
        }
    
    def find_best_match(self, question: str, intent: str = None) -> Optional[Dict[str, Any]]:
        """Find best matching Q&A for user question"""
        question_lower = question.lower()
        best_match = None
        highest_score = 0
        
        for qa in self.qa_database:
            score = 0
            
            # Intent match (high weight)
            if intent and intent == qa["intent"]:
                score += 40
            
            # Keyword matching
            for keyword in qa["keywords"]:
                if keyword in question_lower:
                    score += 20
            
            # Question similarity
            qa_words = qa["question"].lower().split()
            question_words = question_lower.split()
            common_words = set(qa_words) & set(question_words)
            if common_words:
                score += len(common_words) * 5
            
            if score > highest_score and score > 30:
                highest_score = score
                best_match = qa
        
        return best_match
    
    def get_related_questions(self, category: str) -> List[str]:
        """Get related questions from same category"""
        related = []
        for qa in self.qa_database:
            if qa["category"] == category:
                related.append(qa["question"])
        return related[:3]
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories"""
        return list(set(qa["category"] for qa in self.qa_database)) 