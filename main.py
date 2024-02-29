from sub.subscriber import Subscriber
from metagpt.schema import logger
import asyncio

async def main():
    subscriber = Subscriber()
    logger.info("Cake start")
    result = await subscriber._act()
    logger.info(result)

if __name__ == "__main__":
    asyncio.run(main())