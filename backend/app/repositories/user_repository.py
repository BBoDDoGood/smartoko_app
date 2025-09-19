from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
import os

from app.repositories.base_repository import BaseRepository
from app.models.user import User, LoginLog
from app.core.auth import verify_password

class UserRepository(BaseRepository):
    """사용자 관련 데이터 접근 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회 - 로그인용"""
        try:
            result = await self.db.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            
            if user:
                self.logger.info(f"사용자 조회 성공: {username}")
            else:
                self.logger.warning(f"사용자 조회 실패: {username}")
            return user
        except SQLAlchemyError as e:
            self.logger.error(f"사용자명 조회 오류 [{username}]: {str(e)}")
            return None
        
    async def verify_user_credentials(self, username: str, password: str) -> Optional[User]:
        """사용자 인증 - 로그인 검증"""
        try:
            # 사용자 존재 여부 확인
            user = await self.find_by_username(username)
            if not user:
                self.logger.warning(f"로그인 실패 - 사용자 없음: {username}")
                return None
            
            # 비밀번호 검증
            if verify_password(password, user.password):
                # 계정 상태 확인 -> enabled = 1: 활성화 , enabled = 0: 비활성화
                if user.enabled == '1':
                    self.logger.info(f"로그인 성공: {username}")
                    return user
                else:
                    self.logger.warning(f"비활성 계정 로그인 시도: {username}")
                    return None
            else:
                self.logger.warning(f"비밀번호 불일치: {username}")
                return None
        except SQLAlchemyError as e:
            self.logger.error(f"인증 처리 오류 [{username}]: {str(e)}")
            return None
        
    async def get_user_devices_count(self, user_seq: int) -> int:
        """사용자의 등록된 디바이스 개수 조회"""
        try:
            from app.models.device import Device
            
            device_count = await self.count(Device, user_seq=user_seq)
            self.logger.info(f"사용자 {user_seq}의 디바이스 개수: {device_count}")
            return device_count
        
        except Exception as e:
            self.logger.error(f"디바이스 개수 조회 오류 [user_seq={user_seq}]: {str(e)}")
            return 0
        
    async def get_user_with_basic_info(self, user_seq: int) -> Optional[User]:
        """사용자 기본 정보 조회"""
        try:
            user = await self.find_by_id(User, user_seq)
            
            if user:
                self.logger.info(f"사용자 기본 정보 조회 성공: {user_seq}")
            else:
                self.logger.warning(f"사용자 기본 정보 없음: {user_seq}")
            return user
        except Exception as e:
            self.logger.error(f"사용자 기본 정보 조회 오류 [user_seq={user_seq}]: {str(e)}")
            return None
        
    async def save_login_log(self, user_seq: int, ip_address: str, device_type: str) -> bool:
        """로그인 로그 저장 -  ip로 국가 코드 자동 추출"""
        try:
            from datetime import datetime
            
            # ip 주소로 국가 코드 자동 추출
            country_code = self._get_country_code_from_ip(ip_address)
            
            login_log = LoginLog(
                user_seq=user_seq,
                ip_addr=ip_address,
                country_code=country_code,
                device_type=device_type[:3],
                reg_dt=datetime.now()
            )
            
            self.db.add(login_log)
            await self.db.commit()
            
            self.logger.info(f"로그인 로그 저장 성공 [user_seq={user_seq}, ip={ip_address}, country={country_code}]")
            return True
        
        except SQLAlchemyError as e:
            await self.db.rollback()
            self.logger.error(f"로그인 로그 저장 실패 [user_seq={user_seq}]: {str(e)}")
            return False
        
    def _get_country_code_from_ip(self, ip_address: str) -> str:
        """ ip 주소로 국가 코드 조회 - GeoLite2 데이터베이스 사용"""
        try:
            import geoip2.database
            import geoip2.errors
            
            # 로컬/개발 환경 처리
            local_addresses = ["127.0.0.1", "localhost", "::1", "0:0:0:0:0:0:0:1"]
            if ip_address in local_addresses:
                self.logger.info(f"로컬 ip 감지 [{ip_address}] -> 한국으로 처리")
                return "KR"
            
            # GeoLite2 데이터베이스 파일 경로
            project_root = Path(__file__).parent.parent.parent.parent
            db_path = project_root / "backend" / "data" / "GeoLite2-Country.mmdb"
            
            # 파일 존재 확인
            if not db_path.exists():
                self.logger.error(f"GeoLite2 데이터베이스 파일 없음: {db_path}")
                self.logger.error(f"현재 작업 디렉토리: {os.getcwd()}")
                self.logger.error(f"파일 경로 계산: {Path(__file__)} -> {project_root}")
                return "99"
            
            # GeoIP 데이터베이스로 국가 코드 조회
            with geoip2.database.Reader(str(db_path)) as reader:
                response = reader.country(ip_address)
                country_code = response.country.iso_code
                
                if country_code:
                    self.logger.info(f"IP 국가 조회 성공: {ip_address} -> {country_code}")
                    return country_code
                else:
                    self.logger.warning(f"IP {ip_address} -> 국가 코드 없음, 기본값 99")
                    return "99"
                
        except geoip2.errors.AddressNotFoundError:
            self.logger.warning(f"유효하지 않은 IP 주소: {ip_address}")
            return "99"
        
        except FileNotFoundError:
            self.logger.error(f"GeoIP 데이터베이스 파일 접근 실패: {db_path if 'db_path' in locals() else '경로 계산 실패'}")
            return "99"
        
        except ImportError as e:
            self.logger.error(f"geoip2 라이브러리 import 실패: {str(e)}")
            self.logger.error(f"pip install geoip2 명령어로 설치해주세요")
            return "99"
        
        except Exception as e:
            self.logger.error(f"IP 국가 조회 오류 [{ip_address}]: {str(e)}")
            self.logger.error(f"오류 타입: {type(e).__name__}")
            return "99"