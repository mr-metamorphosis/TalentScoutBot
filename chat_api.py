from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import requests
import databutton as db

router = APIRouter()

# Base models
class CandidateInfo(BaseModel):
    name: str
    experience_years: int
    tech_stack: List[str]
    position: str

class ChatMessage(BaseModel):
    role: str
    content: str

# Request/Response models
class ChatRequest(BaseModel):
    candidate_info: CandidateInfo
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    message: str
    interview_id: Optional[str] = None

# Interview models
class Interview(BaseModel):
    id: str
    candidate_info: CandidateInfo
    messages: List[ChatMessage]
    timestamp: str
    evaluation_scores: Optional[Dict[str, float]] = None

class ListInterviewsResponse(BaseModel):
    interviews: List[Interview]

class CompareInterviewsRequest(BaseModel):
    interview_ids: List[str]

class CompareInterviewsResponse(BaseModel):
    comparison: Dict[str, Dict[str, float]]
    recommendations: Dict[str, str]


@router.get("/interviews", response_model=ListInterviewsResponse)
def list_all_interviews() -> ListInterviewsResponse:
    """List all interviews."""
    return ListInterviewsResponse(interviews=list_interviews())

@router.post("/compare", response_model=CompareInterviewsResponse)
def compare_interviews(request: CompareInterviewsRequest) -> CompareInterviewsResponse:
    """Compare multiple interviews."""
    comparison = {}
    recommendations = {}
    
    # Get interviews
    interviews = [get_interview(id) for id in request.interview_ids]
    valid_interviews = [i for i in interviews if i is not None]
    
    for interview in valid_interviews:
        # Get scores
        scores = interview.evaluation_scores or evaluate_responses(interview.messages)
        comparison[interview.id] = scores
        
        # Generate recommendation
        avg_score = sum(scores.values()) / len(scores)
        if avg_score >= 0.8:
            recommendation = "Strong candidate with excellent technical skills and communication"
        elif avg_score >= 0.6:
            recommendation = "Good candidate with solid foundation, some areas for improvement"
        else:
            recommendation = "May need more experience, consider for junior positions"
        
        recommendations[interview.id] = recommendation
    
    return CompareInterviewsResponse(
        comparison=comparison,
        recommendations=recommendations
    )

class Interview(BaseModel):
    id: str
    candidate_info: CandidateInfo
    messages: List[ChatMessage]
    timestamp: str
    evaluation_scores: Optional[Dict[str, float]] = None

class ListInterviewsResponse(BaseModel):
    interviews: List[Interview]

class CompareInterviewsRequest(BaseModel):
    interview_ids: List[str]

class CompareInterviewsResponse(BaseModel):
    comparison: Dict[str, Dict[str, float]]
    recommendations: Dict[str, str]

def create_system_prompt(candidate_info: CandidateInfo) -> str:
    """Create a detailed system prompt for the Llama model."""
    return f"""You are an experienced technical interviewer conducting an interview for a {candidate_info.position} position. 
    The candidate, {candidate_info.name}, has {candidate_info.experience_years} years of experience and is skilled in {', '.join(candidate_info.tech_stack)}.

    Interview Guidelines:
    1. Ask one question at a time
    2. Focus on technical questions related to their tech stack
    3. Ask follow-up questions based on their responses
    4. Keep responses concise and professional
    5. Progress naturally through different interview stages:
       - Start with experience and background
       - Move to technical questions about their stack
       - Include some behavioral questions
       - End with opportunity for candidate questions
    6. Evaluate answers for technical accuracy and depth

    Remember to:
    - Stay focused on their tech stack: {', '.join(candidate_info.tech_stack)}
    - Ask for specific examples
    - Probe deeper when answers lack detail
    - Maintain a professional and encouraging tone"""

def format_messages_for_llama(system_prompt: str, messages: List[ChatMessage]) -> List[dict]:
    """Format the conversation history for Llama API."""
    formatted_messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history
    for msg in messages:
        # Convert 'assistant' role to 'assistant' for Llama
        role = "assistant" if msg.role == "assistant" else "user"
        formatted_messages.append({"role": role, "content": msg.content})
    
    return formatted_messages

def save_interview(interview: Interview) -> None:
    """Save interview to storage."""
    # Get existing interviews or initialize empty dict
    try:
        interviews = db.storage.json.get("interviews", default={})
    except Exception as e:
        print(f"Error reading interviews: {str(e)}")
        interviews = {}
    
    # Save interview
    interviews[interview.id] = interview.dict()
    db.storage.json.put("interviews", interviews)

def get_interview(interview_id: str) -> Optional[Interview]:
    """Get interview from storage."""
    try:
        interviews = db.storage.json.get("interviews", default={})
        if interview_id in interviews:
            return Interview(**interviews[interview_id])
    except Exception as e:
        print(f"Error getting interview {interview_id}: {str(e)}")
        pass
    return None

def list_interviews() -> List[Interview]:
    """List all interviews."""
    try:
        interviews = db.storage.json.get("interviews", default={})
        return [Interview(**interview) for interview in interviews.values()]
    except Exception as e:
        print(f"Error listing interviews: {str(e)}")
        return []

def evaluate_responses(messages: List[ChatMessage]) -> Dict[str, float]:
    """Evaluate candidate responses for different criteria."""
    scores = {
        "technical_depth": 0.0,
        "communication": 0.0,
        "problem_solving": 0.0,
        "experience": 0.0
    }
    
    # Count words and technical terms in candidate responses
    total_responses = 0
    total_words = 0
    technical_terms = 0
    
    for msg in messages:
        if msg.role == "user":
            response = msg.content.lower()
            words = response.split()
            total_words += len(words)
            total_responses += 1
            
            # Count technical terms (expand this list based on needs)
            tech_terms = ["api", "function", "class", "database", "algorithm", 
                         "framework", "architecture", "deployment", "testing", 
                         "debug", "optimize", "scalable", "concurrent", "async"]
            technical_terms += sum(1 for term in tech_terms if term in response)
    
    if total_responses > 0:
        # Technical depth based on technical terms per response
        scores["technical_depth"] = min(1.0, technical_terms / (total_responses * 3))
        
        # Communication based on average response length
        avg_words = total_words / total_responses
        scores["communication"] = min(1.0, avg_words / 50)  # Normalize to 0-1
        
        # Problem solving based on response structure and keywords
        problem_solving_terms = ["because", "therefore", "however", "solution", 
                                "approach", "method", "strategy", "implement"]
        problem_solving_count = sum(1 for msg in messages if msg.role == "user" and 
                                  any(term in msg.content.lower() for term in problem_solving_terms))
        scores["problem_solving"] = min(1.0, problem_solving_count / total_responses)
        
        # Experience based on concrete examples and past projects
        experience_terms = ["project", "worked", "implemented", "developed", 
                           "team", "company", "production", "deployed"]
        experience_count = sum(1 for msg in messages if msg.role == "user" and 
                             any(term in msg.content.lower() for term in experience_terms))
        scores["experience"] = min(1.0, experience_count / total_responses)
    
    return scores

def get_llama_response(messages: List[dict]) -> str:
    """Get response from Llama API."""
    api_key = db.secrets.get("LLAMA_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": messages,
        "stream": False,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    
    response = requests.post(
        "https://api.llama.ai/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error from Llama API: {response.text}")

@router.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    # Check if this is a continuation of an existing interview
    existing_interviews = list_interviews()
    current_interview = next(
        (interview for interview in existing_interviews 
         if interview.candidate_info.dict() == request.candidate_info.dict()),
        None
    )
    
    # Get or create interview ID
    if current_interview:
        interview_id = current_interview.id
    else:
        interview_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # Create system prompt based on candidate info
    system_prompt = create_system_prompt(request.candidate_info)
    
    # Format messages for Llama
    formatted_messages = format_messages_for_llama(system_prompt, request.messages)
    
    # Get response from Llama
    try:
        response = get_llama_response(formatted_messages)
        # Create or update interview record
        interview = Interview(
            id=interview_id,
            candidate_info=request.candidate_info,
            messages=request.messages + [ChatMessage(role="assistant", content=response)],
            timestamp=datetime.now().isoformat(),
            evaluation_scores=evaluate_responses(request.messages)
        )
        save_interview(interview)
        
        return ChatResponse(message=response, interview_id=interview_id)
    except Exception as e:
        print(f"Error getting response from Llama: {str(e)}")
        return ChatResponse(
            message="I apologize, but I'm having trouble processing your response. Could you please try again?"
        )
