from typing import List

from loguru import logger
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from db.models.card import Card
from schemas import card_schema


class CardDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_card(self, card: card_schema.Card):
        new_card = Card(**card.dict())
        self.db_session.add(new_card)
        try:
            await self.db_session.commit()
        except IntegrityError as ex:
            await self.db_session.rollback()
            logger.warning(f"Card {new_card.card_id} already exists!")

    async def create_cards(self, cards: List[card_schema.Card]):
        # new_card = Card(**card.dict())
        stmt = insert(Card).values([card.dict() for card in cards]).on_conflict_do_nothing()
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def get_card(self, card_id: str):
        q = await self.db_session.execute(select(Card).where(Card.card_id == card_id))
        return q.scalars().first()

    async def get_all_cards(self) -> List[Card]:
        q = await self.db_session.execute(select(Card).order_by(Card.id))
        return q.scalars().all()
