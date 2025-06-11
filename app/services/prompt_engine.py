"""
TraintiQ Prompt Engineering Engine
Modular system for generating context-aware AI prompts
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class PromptEngine:
    def __init__(self):
        self.company_context = self._load_company_context()
        self.templates = self._load_prompt_templates()
        self.conversation_context = {}
    
    def _load_company_context(self) -> Dict[str, Any]:
        """Load comprehensive company information"""
        return {
            "company_info": {
                "name": "TraintiQ",
                "founded": "2020",
                "industry": "HR Technology / AI Solutions",
                "mission": "Revolutionize employee training and development through AI-powered solutions",
                "vision": "To be the leading AI-driven platform for talent optimization and workforce development",
                "headquarters": "Silicon Valley, California",
                "team_size": "50-200 employees"
            },
            "core_services": {
                "ai_cv_analysis": {
                    "name": "AI-Powered CV Analysis",
                    "description": "Advanced resume screening using GPT-4 technology",
                    "features": ["Skill extraction", "Experience mapping", "Compatibility scoring"],
                    "use_cases": ["Recruitment", "Talent acquisition", "HR automation"]
                },
                "profile_generation": {
                    "name": "Employee Profile Generation",
                    "description": "Automated creation of comprehensive employee profiles",
                    "features": ["Skills assessment", "Career trajectory analysis", "Performance prediction"],
                    "use_cases": ["HR management", "Career development", "Team optimization"]
                },
                "skills_matching": {
                    "name": "Skills Assessment & Matching",
                    "description": "Intelligent matching of candidates to roles",
                    "features": ["Competency mapping", "Gap analysis", "Training recommendations"],
                    "use_cases": ["Role placement", "Internal mobility", "Skills development"]
                },
                "training_optimization": {
                    "name": "Training Program Optimization",
                    "description": "AI-driven personalization of learning paths",
                    "features": ["Adaptive learning", "Progress tracking", "ROI measurement"],
                    "use_cases": ["Employee development", "Compliance training", "Leadership development"]
                }
            },
            "pricing_tiers": {
                "starter": {
                    "price": "$29/month",
                    "target": "Small teams and startups",
                    "features": ["Basic CV Analysis (up to 100 profiles)", "Standard reporting", "Email support"],
                    "limits": {"profiles": 100, "users": 5, "storage": "5GB"}
                },
                "professional": {
                    "price": "$99/month", 
                    "target": "Growing companies",
                    "features": ["Advanced AI Analysis (unlimited profiles)", "Custom reporting", "Priority support", "API access"],
                    "limits": {"profiles": "unlimited", "users": 25, "storage": "50GB"}
                },
                "enterprise": {
                    "price": "Custom pricing",
                    "target": "Large organizations", 
                    "features": ["Full platform access", "Custom AI training", "Dedicated support", "On-premise deployment"],
                    "limits": {"profiles": "unlimited", "users": "unlimited", "storage": "unlimited"}
                }
            },
            "contact_info": {
                "main_email": "contact@traintiq.com",
                "support_email": "support@traintiq.com", 
                "sales_email": "sales@traintiq.com",
                "phone": "1-800-TRAINTIQ",
                "website": "https://traintiq.com"
            },
            "company_culture": {
                "core_values": ["Innovation & Excellence", "Collaboration & Teamwork", "Continuous Learning", "Work-Life Balance"],
                "work_environment": "Remote-first with flexible office spaces",
                "benefits": ["Competitive salary", "Health insurance", "Unlimited PTO", "Professional development budget"]
            }
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load modular prompt templates for different conversation types"""
        return {
            "system_base": """You are Alex, an intelligent AI assistant for {company_name}, a leading HR technology company. You are powered by GPT-4 and provide helpful, professional, and engaging responses.

Company Information:
- Founded: {founded}
- Industry: {industry}
- Mission: {mission}

Your Guidelines:
- Be professional yet friendly and approachable
- Provide accurate information about {company_name}
- Use emojis appropriately to make conversations engaging
- Offer relevant follow-up suggestions
- Keep responses concise but informative (2-3 sentences unless detailed explanation needed)
- Use bullet points for lists when appropriate
- Always end with a helpful question or call-to-action when relevant

Remember: You represent {company_name}'s cutting-edge AI technology, so demonstrate intelligence and sophistication while maintaining a professional yet approachable tone.""",

            "greeting_template": """Welcome! 👋 I'm Alex, your AI assistant for {company_name}. 

I'm here to help you learn about:
• Our AI-powered HR solutions
• Pricing plans and features  
• Getting started with our platform
• Technical support and demos

How can I assist you today?""",

            "services_template": """🚀 **{company_name} Services Overview**

We offer comprehensive AI-powered HR solutions:

{services_list}

Each service leverages cutting-edge AI technology to streamline your HR processes and improve decision-making.

Would you like to learn more about any specific service or see how they can benefit your organization?""",

            "pricing_template": """💰 **{company_name} Pricing Plans**

{pricing_details}

All plans include:
✅ 24/7 customer support
✅ Regular feature updates  
✅ Data security & compliance
✅ Integration support

Would you like to start with a free trial or schedule a demo?""",

            "contact_template": """📞 **Get in Touch with {company_name}**

{contact_details}

**Response Times:**
- Support: Within 4 hours
- Sales: Within 1 hour  
- General inquiries: Within 24 hours

How else can I help you today?"""
        }
    
    def generate_system_prompt(self) -> str:
        """Generate the main system prompt with company context"""
        info = self.company_context["company_info"]
        
        return self.templates["system_base"].format(
            company_name=info["name"],
            founded=info["founded"],
            industry=info["industry"],
            mission=info["mission"]
        )
    
    def generate_response_prompt(self, message_type: str, **kwargs) -> str:
        """Generate specific response prompts based on message type"""
        if message_type == "greeting":
            return self._generate_greeting_prompt()
        elif message_type == "services":
            return self._generate_services_prompt()
        elif message_type == "pricing":
            return self._generate_pricing_prompt()
        elif message_type == "contact":
            return self._generate_contact_prompt()
        else:
            return self._generate_general_prompt()
    
    def _generate_services_prompt(self) -> str:
        """Generate services overview prompt"""
        services_list = ""
        for key, service in self.company_context["core_services"].items():
            services_list += f"• **{service['name']}**: {service['description']}\n"
        
        return self.templates["services_template"].format(
            company_name=self.company_context["company_info"]["name"],
            services_list=services_list
        )
    
    def _generate_pricing_prompt(self) -> str:
        """Generate pricing information prompt"""
        pricing_details = ""
        for tier, details in self.company_context["pricing_tiers"].items():
            pricing_details += f"""
**{tier.title()} Plan - {details['price']}**
Target: {details['target']}
Key Features: {', '.join(details['features'][:3])}

"""
        
        return self.templates["pricing_template"].format(
            company_name=self.company_context["company_info"]["name"],
            pricing_details=pricing_details
        )
    
    def _generate_contact_prompt(self) -> str:
        """Generate contact information prompt"""
        contact = self.company_context["contact_info"]
        contact_details = f"""
**Email Contacts:**
• General: {contact['main_email']}
• Support: {contact['support_email']}
• Sales: {contact['sales_email']}

**Phone:** {contact['phone']}
**Website:** {contact['website']}
"""
        
        return self.templates["contact_template"].format(
            company_name=self.company_context["company_info"]["name"],
            contact_details=contact_details
        )
    
    def _generate_greeting_prompt(self) -> str:
        """Generate greeting prompt"""
        return self.templates["greeting_template"].format(
            company_name=self.company_context["company_info"]["name"]
        )
    
    def _generate_general_prompt(self) -> str:
        """Generate general response prompt"""
        return f"Please provide a helpful response about {self.company_context['company_info']['name']} based on the company information provided."
    
    def analyze_message_intent(self, message: str) -> str:
        """Analyze user message to determine intent"""
        message_lower = message.lower()
        
        intent_keywords = {
            "greeting": ["hello", "hi", "hey", "good morning", "start"],
            "services": ["service", "offer", "product", "solution", "feature"],
            "pricing": ["price", "cost", "plan", "pricing", "fee", "subscription"],
            "contact": ["contact", "support", "help", "phone", "email", "reach"],
            "demo": ["demo", "trial", "test", "try", "preview"],
            "company": ["about", "company", "team", "history", "culture"]
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
                
        return "general"
    
    def get_contextual_quick_replies(self, intent: str) -> List[str]:
        """Generate contextual quick reply options based on intent"""
        quick_replies_map = {
            "greeting": ["Our Services", "Pricing Plans", "Request Demo", "Contact Sales"],
            "services": ["CV Analysis", "Skills Matching", "Pricing", "Book Demo"],
            "pricing": ["Starter Plan", "Professional Plan", "Enterprise", "Free Trial"],
            "contact": ["Email Support", "Phone Call", "Sales Team", "Technical Help"],
            "demo": ["Schedule Demo", "Free Trial", "Product Tour", "Contact Sales"],
            "company": ["Our Team", "Company Values", "Success Stories", "Career Opportunities"],
            "general": ["Our Services", "Pricing", "Contact Us", "Learn More"]
        }
        
        return quick_replies_map.get(intent, quick_replies_map["general"])
    
    def update_conversation_context(self, session_id: str, message: str, response: str, intent: str):
        """Update conversation context for better continuity"""
        if session_id not in self.conversation_context:
            self.conversation_context[session_id] = {
                "start_time": datetime.now(),
                "message_count": 0,
                "topics_discussed": [],
                "user_interests": []
            }
        
        context = self.conversation_context[session_id]
        context["message_count"] += 1
        context["last_intent"] = intent
        context["last_message_time"] = datetime.now()
        
        # Track topics of interest
        if intent not in context["topics_discussed"]:
            context["topics_discussed"].append(intent)
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation summary for analytics"""
        if session_id not in self.conversation_context:
            return {"error": "Session not found"}
        
        context = self.conversation_context[session_id]
        duration = (datetime.now() - context["start_time"]).total_seconds()
        
        return {
            "session_id": session_id,
            "duration_seconds": duration,
            "message_count": context["message_count"],
            "topics_discussed": context["topics_discussed"],
            "engagement_level": self._calculate_engagement_level(context)
        }
    
    def _calculate_engagement_level(self, context: Dict) -> str:
        """Calculate user engagement level based on conversation data"""
        message_count = context["message_count"]
        topics_count = len(context["topics_discussed"])
        
        if message_count >= 10 and topics_count >= 3:
            return "high"
        elif message_count >= 5 and topics_count >= 2:
            return "medium"
        else:
            return "low" 