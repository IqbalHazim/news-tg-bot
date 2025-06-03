from typing import List, Dict, Optional
import json
from openai import OpenAI
# from anthropic import Anthropic
# import cohere

class CryptoNewsSummarizer:
    def __init__(self, llm_provider: str, llm_config: Dict, model_name: Optional[str] = None):
        """
        Initialize the AI news summarizer service.
        
        Args:
            llm_provider (str): Name of the LLM provider (e.g., "openai", "anthropic", "cohere")
            llm_config (Dict): Configuration dictionary for the LLM (API keys, etc.)
            model_name (str, optional): Specific model name to use. Defaults to provider's default.
        """
        self.llm_provider = llm_provider.lower()
        self.llm_config = llm_config
        self.model_name = model_name
        self.context = []  # To store news articles
        self._setup_llm_client()
        
    def _setup_llm_client(self):
        """Initialize the LLM client based on the provider."""
        if self.llm_provider == "openai":
            
            self.client = OpenAI(api_key=self.llm_config.get("api_key"), base_url="https://api.deepseek.com")
            if not self.model_name:
                self.model_name = "gpt-4-turbo"
                
        # elif self.llm_provider == "anthropic":
        #     self.client = Anthropic(api_key=self.llm_config.get("api_key"))
        #     if not self.model_name:
        #         self.model_name = "claude-3-opus-20240229"
                
        # elif self.llm_provider == "cohere":
        #     self.client = cohere.Client(api_key=self.llm_config.get("api_key"))
        #     if not self.model_name:
        #         self.model_name = "command"
                
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def add_articles(self, articles: List[Dict]):
        """
        Add news articles to the context for summarization.
        
        Args:
            articles (List[Dict]): List of article dictionaries with keys like:
                                   'title', 'source', 'date', 'content', 'url'
        """
        self.context.extend(articles)
    
    def clear_context(self):
        """Clear all stored articles from the context."""
        self.context = []
    
    def generate_summary_prompt(self) -> str:
        """
        Generate a detailed prompt for summarizing cryptocurrency news.
        
        Returns:
            str: The formatted prompt with context.
        """
        articles_info = "\n\n".join(
            f"ARTICLE {i+1}:\n"
            f"Source: {article.get('website_name', 'Unknown')}\n"
            f"Title: {article.get('main_headline', 'No title')}\n"
            f"Date: {article.get('written_datetime', 'Unknown date')}\n"
            f"URL: {article.get('url', 'No URL')}\n"
            f"Content:\n{article.get('content', 'No content')}"
            for i, article in enumerate(self.context))
        
        prompt = f"""
        You are an expert AI assistant specialized in analyzing and summarizing cryptocurrency news.
        Your task is to carefully read through each provided news article and create a concise yet 
        comprehensive summary in key point form.
        
        INSTRUCTIONS:
        1. Analyze each article INDIVIDUALLY first before creating the summary.
        2. Focus on the most important and relevant information for cryptocurrency investors.
        3. Identify key events, price movements, regulatory changes, partnerships, or technological developments.
        4. Note any significant figures, percentages, or statistics mentioned.
        5. Highlight potential market impacts or analyst opinions when available.
        6. Maintain an objective tone and avoid speculation unless clearly labeled as such.
        7. Group related information from different articles together in your summary.
        8. Include the source for each key point when relevant.
        9. If multiple articles cover the same event, provide a unified but detailed point.
        
        FORMAT REQUIREMENTS:
        - Begin with an overall summary paragraph (2-3 sentences)
        - Follow with bullet points of key information
        - For each bullet point, include [Source X] reference when applicable
        - End with potential market implications if discernible from the articles
        
        ARTICLES TO SUMMARIZE:
        {articles_info}
        
        Now, please provide your detailed cryptocurrency news summary following the above instructions.
        """
        
        return prompt.strip()
    
    def summarize(self, temperature: float = 0.3, max_tokens: int = 1500) -> str:
        """
        Generate a summary of the current context articles.
        
        Args:
            temperature (float): Controls randomness (0.0-1.0). Lower for more deterministic.
            max_tokens (int): Maximum length of the summary response.
            
        Returns:
            str: The generated summary text.
        """
        if not self.context:
            raise ValueError("No articles in context to summarize. Add articles first.")
        
        prompt = self.generate_summary_prompt()
        
        if self.llm_provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        # elif self.llm_provider == "anthropic":
        #     response = self.client.messages.create(
        #         model=self.model_name,
        #         messages=[{"role": "user", "content": prompt}],
        #         temperature=temperature,
        #         max_tokens=max_tokens
        #     )
        #     return response.content[0].text
            
        # elif self.llm_provider == "cohere":
        #     response = self.client.generate(
        #         model=self.model_name,
        #         prompt=prompt,
        #         temperature=temperature,
        #         max_tokens=max_tokens
        #     )
        #     return response.generations[0].text
            
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def summarize_to_file(self, file_path: str, **kwargs):
        """
        Generate a summary and save it to a file.
        
        Args:
            file_path (str): Path to save the summary.
            **kwargs: Arguments to pass to the summarize method.
        """
        summary = self.summarize(**kwargs)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(summary)