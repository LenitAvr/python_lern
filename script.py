import asyncio
import random
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Game, Provider
import os
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

# Инициализация Faker для генерации случайных данных
fake = Faker()
Faker.seed(42)  # Фиксируем seed для воспроизводимости


async def seed_database():
    # Создаем подключение к базе данных
    database_url = os.getenv("DATABASE_URL")
    engine = create_async_engine(database_url)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        try:
            # 1. Создаем 200 случайных провайдеров
            print("Creating 200 providers...")
            providers = []
            for _ in range(200):
                provider = Provider(
                    name=fake.company() + " " + fake.company_suffix(),
                    email=fake.company_email()
                )
                providers.append(provider)

            session.add_all(providers)
            await session.flush()  # Получаем ID для использования в играх
            await session.commit()

            print("✅ Providers created successfully!")
            print(f"Added {len(providers)} providers")

            # 2. Получаем все ID провайдеров
            result = await session.execute(select(Provider.id))
            provider_ids = result.scalars().all()

            # 3. Создаем 100,000 случайных игр
            print("Creating 100,000 games...")
            total_games = 100000
            batch_size = 5000  # Размер пакета для вставки

            # Списки для генерации случайных названий игр
            game_prefixes = ["Ultimate", "Epic", "Legendary", "Super", "Mega", "Extreme", "Pro", "Final", "Battle",
                             "Shadow"]
            game_suffixes = ["Adventure", "Quest", "Chronicles", "Legends", "Wars", "Heroes", "Kingdom", "Realm",
                             "Online", "Tactics"]
            game_nouns = ["Dragon", "Knight", "Wizard", "Spaceship", "Dungeon", "Castle", "Warrior", "Empire", "Galaxy",
                          "Creature"]

            for i in range(0, total_games, batch_size):
                games_batch = []
                current_batch_size = min(batch_size, total_games - i)

                for j in range(current_batch_size):
                    # Генерация случайного названия игры
                    title = " ".join([
                        random.choice(game_prefixes),
                        random.choice(game_nouns),
                        random.choice(game_suffixes)
                    ])

                    # Добавляем случайные слова для разнообразия
                    if random.random() > 0.7:
                        title += ": " + fake.catch_phrase()

                    # Создаем игру со случайными параметрами
                    game = Game(
                        title=title,
                        price=round(random.uniform(1.99, 99.99), 2),
                        is_published=random.random() > 0.1,  # 90% опубликованы
                        provider_id=random.choice(provider_ids)
                    )
                    games_batch.append(game)

                session.add_all(games_batch)
                await session.commit()
                print(f"Batch {i // batch_size + 1}/{(total_games // batch_size) + 1}: Added {len(games_batch)} games")

            print(f"✅ Successfully added {total_games} games!")
            print("Database seeding completed!")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding database: {e}")
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())