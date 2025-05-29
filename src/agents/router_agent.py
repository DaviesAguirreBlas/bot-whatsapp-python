from langchain.llms import OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import Tool, initialize_agent
from datetime import datetime
from .base_agent import BaseAgent
from ..services.sales_service import SalesService
from ..services.insights_service import InsightsService
from ..config import get_settings
from ..db import get_db

settings = get_settings()

SYSTEM_PROMPT = """
Eres Broki, el agente principal de la tienda {store_name}. Siempre hablas en español, tono amigable e informal.
Detecta la intención del usuario (register, summary, history, edit, delete, insights, seller_sales, explore).
Recoge los datos faltantes, llama la herramienta correcta con solo los argumentos requeridos, y responde.
Nunca muestres JSON, UUIDs, ni SQL. Solo puedes operar en la tienda {store_name}.
Contexto: usuario={user_name}, rol={user_role}, fecha={now}.
Herramientas:
- register_sale: amount, payment_method, image_link
- daily_summary: target_date
- view_history: reference
- edit_sale_guided: (guiado)
- delete_sale: (guiado)
- ad_hoc_analysis: metric, target_date
- sales_by_seller: seller_name, store_name
- sales_insights: user_name, store_name, target_time
Sigue las reglas y ejemplos del prompt original.
"""

class RouterAgent(BaseAgent):
    def __init__(self, customer_phone, store_name, user_name, user_role):
        super().__init__(customer_phone)
        self.store_name = store_name
        self.user_name = user_name
        self.user_role = user_role
        self.now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.llm = OpenAI(temperature=0, api_key=settings.OPENAI_API_KEY)
        db = get_db()
        sales_service = SalesService(db)
        insights_service = InsightsService(sales_service)
        self.tools = [
            Tool("register_sale", sales_service.register_sale, "Registrar una venta nueva"),
            Tool("daily_summary", sales_service.daily_summary, "Resumen diario de ventas"),
            Tool("view_history", sales_service.history, "Historial de ventas"),
            Tool("edit_sale_guided", lambda *args, **kwargs: "Funcionalidad guiada para editar venta", "Editar venta (guiado)"),
            Tool("delete_sale", lambda *args, **kwargs: "Funcionalidad guiada para eliminar venta", "Eliminar venta (guiado)"),
            Tool("ad_hoc_analysis", insights_service.ad_hoc_analysis, "Exploración manual"),
            Tool("sales_by_seller", lambda seller_name, store_name: sales_service.history(customer_phone=None, limit=100), "Ventas por vendedor"),
            Tool("sales_insights", insights_service.last_30_days_kpis, "KPIs últimos 30 días"),
        ]
        self.prompt = ChatPromptTemplate.from_messages([
            {"role": "system", "content": SYSTEM_PROMPT.format(
                store_name=self.store_name,
                user_name=self.user_name,
                user_role=self.user_role,
                now=self.now
            )}
        ])
        self.agent = initialize_agent(
            self.tools, self.llm, agent="chat-conversational-react-description", verbose=settings.DEBUG
        )

    async def process_message(self, message: str) -> str:
        self._add_message_to_history(message)
        try:
            response = await self.agent.arun(input=message)
            self._add_message_to_history(response, is_user=False)
            return response
        except Exception as e:
            error_msg = "Lo siento, algo salió mal. Intenta de nuevo o contacta al administrador."
            self._add_message_to_history(error_msg, is_user=False)
            return error_msg 