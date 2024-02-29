from metagpt.roles import Role
from metagpt.schema import Message, logger
from sub.subactions import CrawlOSSTrending, CrawHuggingPaper, Summary
from typing import Any
import asyncio


class Subscriber(Role):
    def __init__(
            self,
            name: str = "Cake",
            age: int = 20,
            profile: str = "I am a subscriber and analysis reporter of Github Trending and Huggingface Papers.",
            goal: str = "Generate report for Github Trending and Huggingface Papers.",
    ):
        super().__init__(name=name, age=age, profile=profile, goal=goal)
        # actions_l = [CrawlOSSTrending, Summary, CrawHuggingPaper, Summary]
        # self.set_actions(actions=actions_l)
        self.set_actions(actions=[CrawlOSSTrending, Summary, CrawHuggingPaper, Summary])
        # logger.info(type(Action))
        self._set_react_mode(react_mode="by_order")

    async def _act(self) -> Message:
        logger.info(f"{self.rc}")
        logger.info(f"{self._setting}: ready to {self.rc.todo}{self.rc.todo.name}")
        todo = self.rc.todo

        try:
            msg = self.get_memories(k=1)[0]  # find the most recent messages
        except IndexError:
            msg = Message(content="No message in memory.", role=self)
            logger.info("No message in memory.")
        result = await todo.run(msg.content)
        self.rc.memory.add(msg)
        msg = Message(content=result, role=self)

        return msg
    
async def main():
    subscriber = Subscriber()
    logger.info("Cake start")
    result = await subscriber._act()
    logger.info(result)

if __name__ == "__main__":
    asyncio.run(main())
    

    
        
