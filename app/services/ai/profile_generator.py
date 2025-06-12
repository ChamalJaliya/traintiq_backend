import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import os

from langchain_openai import OpenAI, ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document

from app.services.data.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class ProfileGenerator:
    """LangChain-powered profile generation service"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found. Profile generation will be limited.")
        
        self.document_processor = DocumentProcessor()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize LangChain models"""
        if self.openai_api_key:
            try:
                self.llm = ChatOpenAI(
                    temperature=0.7,
                    model_name="gpt-3.5-turbo",
                    openai_api_key=self.openai_api_key
                )
                self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI models: {e}")
                self.llm = None
                self.embeddings = None
        else:
            self.llm = None
            self.embeddings = None
    
    def generate_profile(
        self,
        documents_content: List[str],
        profile_type: str,
        custom_instructions: Optional[str] = None,
        template: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a profile from document content
        
        Args:
            documents_content: List of extracted text from documents
            profile_type: Type of profile to generate
            custom_instructions: Custom instructions from user
            template: Profile template configuration
            
        Returns:
            Tuple of (generated_profile, metadata)
        """
        if not self.llm:
            raise ValueError("OpenAI API not available. Cannot generate profile.")
        
        start_time = datetime.now()
        
        try:
            # Combine all document content
            combined_content = "\n\n".join(documents_content)
            
            # Analyze content first
            content_analysis = self.document_processor.analyze_content(combined_content)
            
            # Create documents for processing
            documents = [Document(page_content=combined_content)]
            
            # Split documents if too large
            if len(combined_content) > 8000:
                documents = self.text_splitter.split_documents(documents)
            
            # Generate summary if multiple documents
            summary = ""
            if len(documents) > 1:
                summary = self._generate_summary_sync(documents)
            else:
                summary = combined_content[:2000] + "..." if len(combined_content) > 2000 else combined_content
            
            # Generate the profile
            profile_content = self._generate_profile_content_sync(
                summary,
                content_analysis,
                profile_type,
                custom_instructions,
                template
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                profile_content,
                content_analysis,
                len(documents_content)
            )
            
            metadata = {
                'generation_time': (datetime.now() - start_time).total_seconds(),
                'input_documents_count': len(documents_content),
                'total_input_length': len(combined_content),
                'content_analysis': content_analysis,
                'model_used': 'gpt-3.5-turbo',
                'template_used': template['name'] if template else 'default',
                'confidence_score': confidence_score
            }
            
            return profile_content, metadata
            
        except Exception as e:
            logger.error(f"Error generating profile: {e}")
            raise e
    
    def _generate_summary_sync(self, documents: List[Document]) -> str:
        """Generate a summary of multiple documents (synchronous)"""
        try:
            summarize_chain = load_summarize_chain(
                self.llm,
                chain_type="map_reduce",
                verbose=False
            )
            
            summary = summarize_chain.run(documents)
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fallback: concatenate first 1000 chars of each document
            return "\n\n".join([doc.page_content[:1000] for doc in documents])
    
    async def _generate_summary(self, documents: List[Document]) -> str:
        """Generate a summary of multiple documents (async version)"""
        return self._generate_summary_sync(documents)
    
    def _generate_profile_content_sync(
        self,
        content_summary: str,
        content_analysis: Dict[str, Any],
        profile_type: str,
        custom_instructions: Optional[str] = None,
        template: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate the actual profile content (synchronous)"""
        
        # Create the prompt based on profile type
        if template and template.get('prompt_template'):
            prompt_template = template['prompt_template']
            system_instructions = template.get('system_instructions', '')
        else:
            prompt_template, system_instructions = self._get_default_template(profile_type)
        
        # Extract key information for the prompt
        key_entities = [ent['text'] for ent in content_analysis.get('entities', [])[:10]]
        key_keywords = [kw['word'] for kw in content_analysis.get('keywords', [])[:15]]
        
        # Build the context
        context = {
            'content_summary': content_summary,
            'key_entities': ', '.join(key_entities),
            'key_keywords': ', '.join(key_keywords),
            'profile_type': profile_type,
            'custom_instructions': custom_instructions or 'None provided',
            'word_count': content_analysis.get('summary_stats', {}).get('total_words', 0),
            'document_structure': json.dumps(content_analysis.get('content_structure', {}), indent=2)
        }
        
        # Create the prompt
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=list(context.keys())
        )
        
        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Generate the profile (synchronous)
        try:
            result = chain.run(**context)
            return result.strip()
        except Exception as e:
            logger.error(f"Error in LLM chain execution: {e}")
            # Fallback response
            return f"Profile generation failed: {str(e)}"
    
    async def _generate_profile_content(
        self,
        content_summary: str,
        content_analysis: Dict[str, Any],
        profile_type: str,
        custom_instructions: Optional[str] = None,
        template: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate the actual profile content (async version)"""
        return self._generate_profile_content_sync(
            content_summary, content_analysis, profile_type, custom_instructions, template
        )
    
    def _get_default_template(self, profile_type: str) -> Tuple[str, str]:
        """Get default template for different profile types"""
        
        templates = {
            'job_profile': {
                'system': "You are an expert HR professional and career consultant specializing in creating comprehensive job profiles.",
                'prompt': """
Based on the provided content, create a comprehensive job profile.

Content Summary:
{content_summary}

Key Entities Found: {key_entities}
Key Keywords: {key_keywords}
Document Structure: {document_structure}
Custom Instructions: {custom_instructions}

Please create a professional job profile that includes:

1. **Job Title & Overview**
   - Clear, specific job title
   - Brief role overview (2-3 sentences)

2. **Key Responsibilities**
   - 5-8 main responsibilities
   - Action-oriented bullet points

3. **Required Qualifications**
   - Education requirements
   - Years of experience
   - Essential skills and competencies

4. **Preferred Qualifications**
   - Additional skills that would be beneficial
   - Nice-to-have experiences

5. **Skills & Competencies**
   - Technical skills
   - Soft skills
   - Industry-specific knowledge

6. **Performance Expectations**
   - Key performance indicators
   - Success metrics

Format the response in a clear, professional manner suitable for job postings or internal documentation.
"""
            },
            
            'project_profile': {
                'system': "You are an experienced project manager and business analyst who creates detailed project profiles.",
                'prompt': """
Based on the provided content, create a comprehensive project profile.

Content Summary:
{content_summary}

Key Entities Found: {key_entities}
Key Keywords: {key_keywords}
Document Structure: {document_structure}
Custom Instructions: {custom_instructions}

Please create a detailed project profile that includes:

1. **Project Overview**
   - Project name and description
   - Project objectives and goals
   - Scope and deliverables

2. **Project Requirements**
   - Functional requirements
   - Technical requirements
   - Business requirements

3. **Stakeholders**
   - Key stakeholders identified
   - Roles and responsibilities

4. **Resources & Skills Needed**
   - Team composition
   - Required skills and expertise
   - Tools and technologies

5. **Timeline & Milestones**
   - Key project phases
   - Major milestones
   - Dependencies

6. **Risk Assessment**
   - Potential risks identified
   - Mitigation strategies

7. **Success Criteria**
   - Key performance indicators
   - Acceptance criteria
   - Quality metrics

Format the response professionally for project documentation and planning purposes.
"""
            },
            
            'company_profile': {
                'system': "You are a business analyst specializing in creating comprehensive company profiles for market research and partnership analysis.",
                'prompt': """
Based on the provided content, create a comprehensive company profile.

Content Summary:
{content_summary}

Key Entities Found: {key_entities}
Key Keywords: {key_keywords}
Document Structure: {document_structure}
Custom Instructions: {custom_instructions}

Please create a detailed company profile that includes:

1. **Company Overview**
   - Company name and brief description
   - Industry and sector
   - Mission and values

2. **Business Model**
   - Primary products/services
   - Target market and customers
   - Revenue streams

3. **Market Position**
   - Market share and competitive position
   - Key differentiators
   - Competitive advantages

4. **Operations**
   - Key operational areas
   - Geographic presence
   - Distribution channels

5. **Financial Highlights**
   - Revenue information (if available)
   - Growth trends
   - Financial stability indicators

6. **Key Personnel**
   - Leadership team
   - Key decision makers
   - Organizational structure

7. **Strategic Focus**
   - Current strategic initiatives
   - Future growth plans
   - Investment priorities

Format the response professionally for business intelligence and partnership evaluation purposes.
"""
            },
            
            'skills_profile': {
                'system': "You are a talent assessment expert who creates detailed skills profiles for individuals or roles.",
                'prompt': """
Based on the provided content, create a comprehensive skills profile.

Content Summary:
{content_summary}

Key Entities Found: {key_entities}
Key Keywords: {key_keywords}
Document Structure: {document_structure}
Custom Instructions: {custom_instructions}

Please create a detailed skills profile that includes:

1. **Skills Overview**
   - Summary of skill areas
   - Proficiency levels where identifiable

2. **Technical Skills**
   - Programming languages and frameworks
   - Software and tools
   - Technical certifications

3. **Professional Skills**
   - Industry-specific competencies
   - Methodologies and processes
   - Domain expertise

4. **Soft Skills**
   - Communication and interpersonal skills
   - Leadership and management abilities
   - Problem-solving and analytical skills

5. **Experience Level**
   - Years of experience in key areas
   - Complexity of projects handled
   - Leadership experience

6. **Learning and Development**
   - Areas for skill enhancement
   - Recommended certifications
   - Growth opportunities

7. **Application Areas**
   - Suitable roles and positions
   - Industry applications
   - Project types

Format the response to be useful for talent management, recruitment, and career development purposes.
"""
            }
        }
        
        default_template = {
            'system': "You are an expert analyst who creates comprehensive profiles from document content.",
            'prompt': """
Based on the provided content, create a comprehensive profile.

Content Summary:
{content_summary}

Key Entities Found: {key_entities}
Key Keywords: {key_keywords}
Document Structure: {document_structure}
Profile Type: {profile_type}
Custom Instructions: {custom_instructions}

Please create a detailed profile that extracts and organizes the most relevant information from the content. 
Structure the profile logically with clear sections and bullet points where appropriate.
Focus on actionable insights and key information that would be valuable for decision-making.

The profile should be professional, comprehensive, and well-organized.
"""
        }
        
        template = templates.get(profile_type, default_template)
        return template['prompt'], template['system']
    
    def _calculate_confidence_score(
        self,
        generated_profile: str,
        content_analysis: Dict[str, Any],
        num_documents: int
    ) -> float:
        """Calculate confidence score for the generated profile"""
        
        score = 0.0
        
        # Base score from content quality
        total_words = content_analysis.get('summary_stats', {}).get('total_words', 0)
        if total_words > 1000:
            score += 0.3
        elif total_words > 500:
            score += 0.2
        elif total_words > 100:
            score += 0.1
        
        # Score from entity extraction
        entities_count = len(content_analysis.get('entities', []))
        if entities_count > 10:
            score += 0.2
        elif entities_count > 5:
            score += 0.15
        elif entities_count > 0:
            score += 0.1
        
        # Score from keywords
        keywords_count = len(content_analysis.get('keywords', []))
        if keywords_count > 15:
            score += 0.2
        elif keywords_count > 10:
            score += 0.15
        elif keywords_count > 5:
            score += 0.1
        
        # Score from document structure
        structure = content_analysis.get('content_structure', {})
        if structure.get('bullet_points', 0) > 0 or structure.get('numbered_items', 0) > 0:
            score += 0.1
        
        # Score from number of input documents
        if num_documents > 3:
            score += 0.1
        elif num_documents > 1:
            score += 0.05
        
        # Score from generated profile length and structure
        profile_words = len(generated_profile.split())
        if profile_words > 500:
            score += 0.1
        elif profile_words > 200:
            score += 0.05
        
        # Normalize to 0-1 range
        return min(1.0, score)
    
    async def generate_profile_suggestions(
        self,
        content_analysis: Dict[str, Any],
        profile_type: str
    ) -> List[str]:
        """Generate suggestions for profile improvement"""
        
        suggestions = []
        
        # Check content quality
        stats = content_analysis.get('summary_stats', {})
        if stats.get('total_words', 0) < 100:
            suggestions.append("Consider providing more detailed content for better profile generation")
        
        # Check for entities
        entities = content_analysis.get('entities', [])
        if len(entities) < 3:
            suggestions.append("Add more specific names, organizations, or technical terms for richer profiles")
        
        # Check document structure
        structure = content_analysis.get('content_structure', {})
        if structure.get('bullet_points', 0) == 0 and structure.get('numbered_items', 0) == 0:
            suggestions.append("Structured content (bullet points, lists) helps create better organized profiles")
        
        # Profile-specific suggestions
        if profile_type == 'job_profile':
            if not any(keyword in ' '.join([kw['word'] for kw in content_analysis.get('keywords', [])]) 
                      for keyword in ['experience', 'skill', 'qualification', 'responsibility']):
                suggestions.append("Include more details about required skills, experience, and responsibilities")
        
        elif profile_type == 'project_profile':
            if not any(keyword in ' '.join([kw['word'] for kw in content_analysis.get('keywords', [])]) 
                      for keyword in ['project', 'requirement', 'deliverable', 'timeline']):
                suggestions.append("Add more information about project requirements, deliverables, and timelines")
        
        return suggestions 