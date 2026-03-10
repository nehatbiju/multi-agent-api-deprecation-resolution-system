"""Main LLM client for Google Gemini"""
import google.generativeai as genai

def get_openai_response(prompt: str) -> str:
    """Get response from Google Gemini using gemini-2.0-flash-exp-vision"""
    genai.configure(api_key="sk-xxx")
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp-vision')
    
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=2048
        )
    )
    
    return response.text