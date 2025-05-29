from langchain.agents import Tool, initialize_agent
from langchain.llms import OpenAI
import yaml
from typing import List, Dict, Any

from .base_agent import BaseAgent
from ..services.sales import SalesService
from ..services.insights import InsightsService
from ..services.nlp import NLPService
from ..db import get_db
from ..config import get_settings

settings = get_settings()

class GeneralAgent(BaseAgent):
    def __init__(self, customer_phone: str):
        super().__init__(customer_phone)
        
        # Initialize services
        db = get_db()
        sales_service = SalesService(db)
        insights_service = InsightsService(sales_service)
        nlp_service = NLPService()
        
        # Define tools
        self.tools = [
            Tool(
                name="register_sale",
                func=sales_service.register_sale,
                description="Registrar una nueva venta dados amount, payment_method y seller"
            ),
            Tool(
                name="daily_summary",
                func=sales_service.daily_summary,
                description="Obtener resumen diario de ventas para una fecha"
            ),
            Tool(
                name="view_history",
                func=sales_service.history,
                description="Ver historial de ventas"
            ),
            Tool(
                name="sales_insights",
                func=insights_service.last_30_days_kpis,
                description="Obtener KPIs de los últimos 30 días"
            ),
            Tool(
                name="ad_hoc_analysis",
                func=insights_service.ad_hoc_analysis,
                description="Análisis ad-hoc según métrica y fecha"
            ),
            Tool(
                name="ocr_image",
                func=nlp_service.ocr_image,
                description="Extraer montos y método de pago de una imagen"
            ),
            Tool(
                name="transcribe_audio",
                func=nlp_service.transcribe_audio,
                description="Transcribir audio a texto"
            )
        ]
        
        # Initialize LLM
        self.llm = OpenAI(
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Load prompt template
        with open("src/templates/prompts/sales_prompt.yaml", "r") as f:
            prompt_template = yaml.safe_load(f)
        
        # Initialize agent
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent="chat-conversational-react-description",
            verbose=settings.DEBUG
        )
    
    async def process_message(self, message: str) -> str:
        """Process message using the agent."""
        self._add_message_to_history(message)
        
        try:
            response = await self.agent.arun(input=message)
            self._add_message_to_history(response, is_user=False)
            return response
        except Exception as e:
            error_msg = f"Lo siento, hubo un error procesando tu mensaje: {str(e)}"
            self._add_message_to_history(error_msg, is_user=False)
            return error_msg 