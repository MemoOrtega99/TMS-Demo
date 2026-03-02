import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import AsyncSessionLocal
from src.api.v1.endpoints.ai import build_rich_context

async def main():
    async with AsyncSessionLocal() as session:
        try:
            print("--- Intentando construir contexto ---")
            ctx = await build_rich_context(session)
            print("EXITO. Contexto generado:")
            print(ctx)
        except Exception as e:
            import traceback
            print("ERROR:")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
