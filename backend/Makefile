# SmartOkO Backend Makefile
# 실무에서 사용하는 표준 명령어들

.PHONY: help dev staging prod install test clean

# 기본 명령어 (make 만 입력시 도움말 표시)
help:
	@echo "🚀 SmartOkO Backend 명령어"
	@echo ""
	@echo "개발 관련:"
	@echo "  make dev      - 개발환경 서버 실행"
	@echo "  make staging  - 스테이징환경 서버 실행"
	@echo "  make prod     - 프로덕션환경 서버 실행"
	@echo ""
	@echo "설치 및 관리:"
	@echo "  make install  - 패키지 설치"
	@echo "  make test     - 테스트 실행"
	@echo "  make clean    - 캐시 파일 정리" 

# 개발환경 실행
dev:
	@echo "🚀 개발환경 서버 시작..."
	@echo "📋 환경: development"
	@echo "🌐 로컬: http://127.0.0.1:8000"
	@echo "🌐 네트워크: http://$(shell ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $$2}'):8000"
	@echo "📖 문서: http://127.0.0.1:8000/api/docs"
	ENVIRONMENT=development uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 스테이징환경 실행  
staging:
	@echo "🚀 스테이징환경 서버 시작..."
	@echo "📋 환경: staging"
	@echo "🌐 주소: http://0.0.0.0:8000"
	@echo "📖 문서: http://0.0.0.0:8000/api/docs"
	ENVIRONMENT=staging uvicorn app.main:app --host 0.0.0.0 --port 8000

# 프로덕션환경 실행
prod:
	@echo "🚀 프로덕션환경 서버 시작..."
	@echo "📋 환경: production"
	@echo "🌐 주소: http://0.0.0.0:8000"
	@echo "⚠️  프로덕션 모드: API 문서 비활성화됨"
	ENVIRONMENT=production uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 패키지 설치
install:
	@echo "📦 패키지 설치 중..."
	pip install -r requirements.txt

# 테스트 실행
test:
	@echo "🧪 테스트 실행 중..."
	pytest tests/ -v

# 캐시 및 임시 파일 정리
clean:
	@echo "🧹 정리 중..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete

# Docker 관련 명령어
docker-build:
	@echo "🐳 Docker 이미지 빌드 중..."
	docker build -t smartoko-backend:latest .

docker-run:
	@echo "🐳 Docker 컨테이너 실행 중..."
	docker run -d \
		--name smartoko-backend \
		-p 8000:8000 \
		--env-file .env.docker \
		smartoko-backend:latest

docker-stop:
	@echo "🛑 Docker 컨테이너 중지 중..."
	docker stop smartoko-backend
	docker rm smartoko-backend

docker-logs:
	@echo "📋 Docker 로그 확인..."
	docker logs -f smartoko-backend

# Docker Compose 명령어
compose-up:
	@echo "🚀 Docker Compose로 전체 스택 시작..."
	docker-compose up -d

compose-down:
	@echo "🛑 Docker Compose 스택 중지..."
	docker-compose down

compose-logs:
	@echo "📋 Docker Compose 로그 확인..."
	docker-compose logs -f

compose-rebuild:
	@echo "🔨 Docker Compose 재빌드..."
	docker-compose up -d --build

# Docker 상태 확인
compose-status:
	@echo "🔍 Docker 컨테이너 상태 확인..."
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

compose-check:
	@echo "🐳 Docker 전체 상태 확인..."
	@./check-docker.sh

compose-health:
	@echo "🏥 API 헬스체크..."
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ API 응답 없음"