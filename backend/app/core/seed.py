"""Демо-данные для свежей БД.

Запускается из lifespan() в app/main.py.
Если в таблице users уже есть записи — ничего не делает.
Иначе создаёт двух пользователей, несколько книг, авторов, жанров
и две опубликованные выставки с секциями и контент-блоками,
чтобы интерфейс не выглядел пустым после первого запуска.
"""
from datetime import datetime, timezone

from passlib.context import CryptContext
from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    Author,
    Book,
    ContentBlock,
    Exhibition,
    Genre,
    Section,
    User,
    UserRole,
)
from ..models.contentblocks import ContentBlockType
from .database import db_helper

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def _is_empty(session: AsyncSession) -> bool:
    result = await session.execute(select(func.count()).select_from(User))
    return result.scalar_one() == 0


async def seed_demo_data() -> None:
    async with db_helper.session_factory() as session:
        if not await _is_empty(session):
            print("[seed] users table not empty, skipping demo seed")
            return

        print("[seed] empty database detected, populating demo data")

        # --- Пользователи -------------------------------------------------
        admin = User(
            username="admin",
            fullname="Иванов И.В.",
            hashed_password=pwd_context.hash("admin12345"),
            role=UserRole.ADMIN,
        )
        librarian = User(
            username="librarian",
            fullname="Петрова А.С.",
            hashed_password=pwd_context.hash("librarian12345"),
            role=UserRole.LIBRARIAN,
        )
        session.add_all([admin, librarian])
        await session.flush()

        # --- Жанры и авторы ----------------------------------------------
        genre_novel = Genre(name="Роман")
        genre_story = Genre(name="Повесть")
        genre_tale = Genre(name="Сказка")

        author_verne = Author(name="Жюль Верн")
        author_pushkin = Author(name="Александр Пушкин")
        author_tolstoy = Author(name="Лев Толстой")

        session.add_all(
            [genre_novel, genre_story, genre_tale, author_verne, author_pushkin, author_tolstoy]
        )
        await session.flush()

        # --- Книги --------------------------------------------------------
        book_20k = Book(
            title="Двадцать тысяч лье под водой",
            annotations=(
                "Профессор Аронакс и его спутники оказываются на борту "
                "«Наутилуса» — подводной лодки таинственного капитана Немо."
            ),
            library_description="Приключенческий роман Жюля Верна.",
            year_of_publication="1869",
            authors=[author_verne],
            genres=[genre_novel],
        )
        book_island = Book(
            title="Таинственный остров",
            annotations=(
                "Пятеро беглецов из плена, унесённые ураганом на воздушном "
                "шаре, оказываются на необитаемом острове."
            ),
            library_description="Робинзонада Жюля Верна.",
            year_of_publication="1875",
            authors=[author_verne],
            genres=[genre_novel],
        )
        book_captain = Book(
            title="Капитанская дочка",
            annotations="Историческая повесть Пушкина о пугачёвском бунте.",
            library_description="Классика русской прозы.",
            year_of_publication="1836",
            authors=[author_pushkin],
            genres=[genre_story],
        )
        book_war = Book(
            title="Война и мир",
            annotations="Эпопея о русском обществе в эпоху наполеоновских войн.",
            library_description="Главное произведение Толстого.",
            year_of_publication="1869",
            authors=[author_tolstoy],
            genres=[genre_novel],
        )
        book_belkin = Book(
            title="Повести Белкина",
            annotations="Цикл из пяти повестей, рассказанных Иваном Петровичем Белкиным.",
            library_description="Малая проза Пушкина.",
            year_of_publication="1831",
            authors=[author_pushkin],
            genres=[genre_story],
        )
        session.add_all([book_20k, book_island, book_captain, book_war, book_belkin])
        await session.flush()

        # --- Выставка №1 --------------------------------------------------
        exhibit_classics = Exhibition(
            title="Великие романы XIX века",
            slug=slugify("Великие романы XIX века"),
            description=(
                "Подборка знаковых романов русской и зарубежной литературы "
                "девятнадцатого столетия."
            ),
            is_published=True,
            published_at=datetime.now(timezone.utc),
            author_id=librarian.id,
        )
        session.add(exhibit_classics)
        await session.flush()

        section_foreign = Section(title="Зарубежные романы", exhibition_id=exhibit_classics.id)
        section_russian = Section(title="Русские романы", exhibition_id=exhibit_classics.id)
        session.add_all([section_foreign, section_russian])
        await session.flush()

        session.add_all(
            [
                ContentBlock(
                    type=ContentBlockType.TEXT,
                    text_content=(
                        "В этом разделе представлены лучшие зарубежные романы "
                        "XIX века — приключения, наука и фантазия."
                    ),
                    section_id=section_foreign.id,
                ),
                ContentBlock(
                    type=ContentBlockType.BOOK,
                    section_id=section_foreign.id,
                    book_id=book_20k.id,
                ),
                ContentBlock(
                    type=ContentBlockType.BOOK,
                    section_id=section_foreign.id,
                    book_id=book_island.id,
                ),
                ContentBlock(
                    type=ContentBlockType.TEXT,
                    text_content="Произведения, ставшие фундаментом русской классической литературы.",
                    section_id=section_russian.id,
                ),
                ContentBlock(
                    type=ContentBlockType.BOOK,
                    section_id=section_russian.id,
                    book_id=book_war.id,
                ),
            ]
        )

        # --- Выставка №2 --------------------------------------------------
        exhibit_pushkin = Exhibition(
            title="Пушкинские повести",
            slug=slugify("Пушкинские повести"),
            description="Малая проза Александра Сергеевича Пушкина.",
            is_published=True,
            published_at=datetime.now(timezone.utc),
            author_id=librarian.id,
        )
        session.add(exhibit_pushkin)
        await session.flush()

        section_pushkin = Section(title="Проза Пушкина", exhibition_id=exhibit_pushkin.id)
        session.add(section_pushkin)
        await session.flush()

        session.add_all(
            [
                ContentBlock(
                    type=ContentBlockType.BOOK,
                    section_id=section_pushkin.id,
                    book_id=book_captain.id,
                ),
                ContentBlock(
                    type=ContentBlockType.BOOK,
                    section_id=section_pushkin.id,
                    book_id=book_belkin.id,
                ),
            ]
        )

        await session.commit()
        print("[seed] demo data created: 2 users, 5 books, 2 exhibitions")
