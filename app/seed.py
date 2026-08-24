import asyncio

from .database import tasks
from .seed_tasks import SEED_TASKS


async def seed_tasks_if_empty() -> None:
    count = await tasks.count_documents({})
    if count == 0:
        await tasks.insert_many(SEED_TASKS)
        print(f"Seeded {len(SEED_TASKS)} tasks")


def main() -> None:
    asyncio.run(seed_tasks_if_empty())


if __name__ == "__main__":
    main()