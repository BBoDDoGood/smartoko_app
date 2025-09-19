from typing import Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.core.database import Base


class BaseRepository:
    """모든 레파지토리가 상속받을 기본 클래스"""
    
    DEFAULT_LIMIT = 1000  # 기본 조회 개수
    MAX_LIMIT = 5000  # 최대 조회 개수
    DEFAULT_PAGE_SIZE = 20  #페이지네이션 기본 크기
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def find_by_id(self, model: Type[Base], id: int) -> Optional[Any]:
        """ id(user_seq)로 데이터 하나 조회
        - model: 조회할 테이블 모델 (User, Device, DetectionResult 등)
        - id: 기본키 값 (user_seq, device_seq 등)
        """
        try:
            result = await self.db.execute(select(model).where(getattr(model, self._get_primary_key_name(model)) == id))
            return result.scalar_one_or_none()
        
        except SQLAlchemyError as e:
            self.logger.error(f"find_by_id 오류 [{model.__name__}:{id}]: {str(e)}")
            return None
    
    async def find_all(self, model: Type[Base], limit: int = None, offset: int = 0) -> List[Any]:
        """전체 데이터 조회
        - model: 조회할 테이블 모델
        - limit: 최대 조회 개수(기본: 1000개)
        - offset: 페이지네이션용
        """
        if limit is None:
            limit = self.DEFAULT_LIMIT
        elif limit > self.MAX_LIMIT:
            limit = self.MAX_LIMIT
            self.logger.warning(f"최대 조회 개수 초과: {limit} -> {self.MAX_LIMIT}")
            
        try:
            result = await self.db.execute(select(model).offset(offset).limit(limit))
            return result.scalars().all()
        
        except SQLAlchemyError as e:
            self.logger.error(f"find_all 오류 [{model.__name__}]: {str(e)}")
            return []
        
    async def find_paginated(self, model: Type[Base], page: int = 1, per_page: Optional[int] = None) -> Dict[str, Any]:
        """페이지네이션으로 데이터 조회
        - model: SQLAlchemy 모델 클래스
        - page: 페이지 번호 (1부터 시작)
        - per_page: 페이지당 조회 개수 (기본: 20개)
        """
        if per_page is None:
            per_page = self.DEFAULT_PAGE_SIZE
            
        # 최대 페이지 크기 제한
        if per_page > self.MAX_LIMIT:
            per_page = self.MAX_LIMIT
            
        offset = (page - 1) * per_page
        
        try:
            # 전체 개수 조회
            count_result = await self.db.execute(select(func.count()).select_from(model))
            total = count_result.scalar()
            
            # 데이터 조회
            data_result = await self.db.execute(select(model).offset(offset).limit(per_page))
            data = data_result.scalars().all()
            
            # 페이지 정보 계산
            total_pages = (total + per_page -1) // per_page
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                'data': data,
                'total': total,
                'page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev,
                'total_pages': total_pages,
            }
            
        except SQLAlchemyError as e:
            self.logger.error(f"find_paginated 오류 [{model.__name__}]: {str(e)}")
            return {
                'data': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'has_next': False,
                'has_prev': False,
                'total_pages': 0,
            }
            
    async def find_by_criteria(self, model: Type[Base], **criteria) -> List[Any]:
        """조건으로 레코드 조회"""
        try:
            query = select(model)

            # 조건 추가
            for field, value in criteria.items():
                if hasattr(model, field):
                    query = query.where(getattr(model, field) == value)
                else:
                    self.logger.warning(f"모델 {model.__name__}에 '{field}' 필드가 없습니다.")

            result = await self.db.execute(query.limit(self.DEFAULT_LIMIT))
            return result.scalars().all()

        except SQLAlchemyError as e:
            self.logger.error(f"find_by_criteria 오류 [{model.__name__}]: {str(e)}")
            return []
        
    async def create(self, model: Type[Base], **data) -> Optional[Any]:
        """새 레코드 생성
        - 나중에 필요할 수도 있으니깐 작성해둠
        """
        try:
            new_record = model(**data)
            self.db.add(new_record)
            await self.db.flush() # ID 생성을 위해 flush
            await self.db.refresh(new_record) #최신 데이터 로드
            
            self.logger.info(f"레코드 생성됨[{model.__name__}]: {new_record}")
            return new_record
        
        except SQLAlchemyError as e:
            self.logger.error(f"create 오류 [{model.__name__}]: {str(e)}")
            await self.db.rollback()
            return None
    
    # 수정 기능 update
    async def update(self, model: Type[Base], id: int, **data) -> bool:
        """id로 레코드 수정
        - 나중에 사용할 수도 있으니깐 작성해둠
        """
        try:
            primary_key = self._get_primary_key_name(model)
            
            result = await self.db.execute(update(model).where(getattr(model, primary_key) == id).values(**data))
            
            success = result.rowcount > 0
            if success:
                self.logger.info(f"레코드 수정됨[{model.__name__}: {id}]: {data}")
                
            return success
        
        except SQLAlchemyError as e:
            self.logger.error(f"update 오류 [{model.__name__}: {id}]: {str(e)}")
            await self.db.rollback()
            return False
        
    async def delete_by_id(self, model: Type[Base], id: int) -> bool:
        """id로 레코드 삭제
        - 나중에 사용할 수도 있으니깐 작성해둠
        """
        try:
            primary_key = self._get_primary_key_name(model)
            result = await self.db.execute(delete(model).where(getattr(model, primary_key) == id))
            
            success = result.rowcount > 0
            if success:
                self.logger.info(f"레코드 삭제됨[{model.__name__}: {id}]")
                
            return success
        
        except SQLAlchemyError as e:
            self.logger.error(f"delete_by_id 오류 [{model.__name__}: {id}]: {str(e)}")
            await self.db.rollback()
            return False
        
    async def count(self, model: Type[Base], **criteria) -> int:
        """조건에 맞는 레코드 개수 조회"""
        try:
            query = select(func.count()).select_from(model)
            
            # 조건 추가
            for field, value in criteria.items():
                if hasattr(model, field):
                    query = query.where(getattr(model, field) == value)
                    
            result = await self.db.execute(query)
            return result.scalar() or 0
        
        except SQLAlchemyError as e:
            self.logger.error(f"count 오류 [{model.__name__}]: {str(e)}")
            return 0
        
    # 유틸리티 함수들
    def _get_primary_key_name(self, model: Type[Base]) -> str:
        """기본키 컬럼명 추출
        - User -> user_seq
        - Device -> device_seq
        - DetectionResult -> detection_result_seq
        """
        # primary_key 컬럼 찾기
        primary_keys = model.__table__.primary_key.columns
        
        if len(primary_keys) == 1:
            return list(primary_keys)[0].name
        else:
            # 복합 기본키인 경우
            raise ValueError(f"모델 {model.__name__}이 복합 Primary Key를 가지고 있습니다")
        
    async def exists_by_id(self, model: Type[Base], id: int) -> bool:
        """id로 레코드 존재 여부 확인"""
        try:
            primary_key = self._get_primary_key_name(model)
            
            result = await self.db.execute(select(func.count()).select_from(model)
                                           .where(getattr(model, primary_key) == id))
            count = result.scalar()
            return count > 0
        
        except SQLAlchemyError as e:
            self.logger.error(f"exists_by_id 오류 [{model.__name__}: {id}]: {str(e)}")
            return False
        
    # 트랜젝션 관리
    async def commit(self) -> bool:
        """변경사항 커밋"""
        try:
            await self.db.commit()
            return True
        
        except SQLAlchemyError as e:
            self.logger.error(f"commit 오류: {str(e)}")
            await self.db.rollback()
            return False
        
    async def rollback(self) -> bool:
        """변경사항 롤백"""
        try:
            await self.db.rollback()
            return True
        except SQLAlchemyError as e:
            self.logger.error(f"rollback 오류: {str(e)}")
            return False