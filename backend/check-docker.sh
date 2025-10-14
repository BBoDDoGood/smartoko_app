#!/bin/bash

echo "🐳 Docker 컨테이너 상태 확인"
echo "================================"
echo ""

# 1. 실행 중인 컨테이너 확인
echo "1️⃣ 실행 중인 컨테이너:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# 2. 컨테이너 로그 확인 (최근 20줄)
echo "2️⃣ 최근 로그:"
docker-compose logs --tail=20
echo ""

# 3. 컨테이너 헬스체크
echo "3️⃣ 헬스체크:"
if docker ps | grep -q smartoko-backend; then
    echo "✅ 컨테이너 실행 중"
    
    # API 헬스체크
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API 응답 정상"
        curl -s http://localhost:8000/health | python3 -m json.tool
    else
        echo "❌ API 응답 없음"
    fi
else
    echo "❌ 컨테이너 실행 안 됨"
fi
echo ""

# 4. 이미지 확인
echo "4️⃣ Docker 이미지:"
docker images | grep smartoko
echo ""

# 5. 네트워크 확인
echo "5️⃣ 네트워크:"
docker network ls | grep smartoko || echo "네트워크 없음"
echo ""

# 6. 볼륨 확인
echo "6️⃣ 볼륨:"
docker volume ls | grep smartoko || echo "볼륨 없음"
echo ""

echo "================================"
echo "✨ 확인 완료!"
