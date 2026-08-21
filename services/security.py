# services/security.py — Rate limiting, IP blocking, suspicious request detection

import time
import threading
import logging
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

from config import (
    RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW,
    SUSPICIOUS_UA_PATTERNS, SUSPICIOUS_PATHS,
    WHITELISTED_IPS, MAX_ATTACK_ATTEMPTS, BLOCK_DURATION
)

logger = logging.getLogger("security")

# Хранилище rate limiting: IP -> список временных меток
rate_limit_store: Dict[str, List[float]] = defaultdict(list)
rate_limit_lock = threading.Lock()

# Хранилище атак: IP -> счётчик попыток
attack_store: Dict[str, int] = defaultdict(int)
attack_lock = threading.Lock()

# Чёрный список IP (автоматически пополняется)
blocked_ips: Dict[str, datetime] = {}  # IP -> время блокировки


def check_rate_limit(client_ip: str) -> bool:
    """Проверяет rate limit для IP.
    :return: True если запрос разрешён, False если превышен лимит
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    with rate_limit_lock:
        # Очищаем старые записи
        rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if t > window_start]
        
        # Проверяем лимит
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
            return False
        
        # Добавляем текущую метку
        rate_limit_store[client_ip].append(now)
        return True


def is_suspicious_request(request) -> Tuple[bool, str]:
    """Проверяет запрос на подозрительную активность.
    :return: (is_suspicious, reason)
    """
    ua = request.headers.get("User-Agent", "").lower()
    path = request.url.path.lower()
    client_ip = request.client.host if request.client else "unknown"
    
    # Проверка User-Agent
    for suspicious in SUSPICIOUS_UA_PATTERNS:
        if suspicious in ua:
            return True, f"Подозрительный UA: {suspicious}"
    
    # Проверка путей
    for suspicious in SUSPICIOUS_PATHS:
        if suspicious in path:
            # Увеличиваем счётчик атак
            with attack_lock:
                attack_store[client_ip] += 1
                if attack_store[client_ip] >= MAX_ATTACK_ATTEMPTS:
                    # Бан IP
                    blocked_ips[client_ip] = datetime.now() + BLOCK_DURATION
                    logger.warning(f"🚫 IP забанен за многократные атаки: {client_ip} ({attack_store[client_ip]} попыток)")
                    return True, f"IP забанен за атаки ({attack_store[client_ip]} попыток)"
            return True, f"Подозрительный путь: {suspicious}"
    
    return False, ""


def is_ip_blocked(client_ip: str) -> Tuple[bool, str]:
    """Проверяет, заблокирован ли IP.
    :return: (is_blocked, message)
    """
    if client_ip in blocked_ips:
        block_time = blocked_ips[client_ip]
        if datetime.now() < block_time + BLOCK_DURATION:
            remaining = (block_time + BLOCK_DURATION - datetime.now()).seconds // 60
            return True, f"IP заблокирован. Осталось минут: {remaining}"
        else:
            # Снимаем блокировку
            del blocked_ips[client_ip]
            logger.info(f"✅ Снята блокировка с IP {client_ip}")
    return False, ""


def block_ip(client_ip: str, reason: str = ""):
    """Блокирует IP."""
    blocked_ips[client_ip] = datetime.now()
    logger.warning(f"🚫 Блокировка IP {client_ip}: {reason}")


def unblock_ip(client_ip: str):
    """Разблокирует IP."""
    if client_ip in blocked_ips:
        del blocked_ips[client_ip]
    with attack_lock:
        if client_ip in attack_store:
            del attack_store[client_ip]
    logger.info(f"🔓 IP разблокирован: {client_ip}")


def get_security_status() -> dict:
    """Возвращает статус безопасности."""
    now = datetime.now()
    active_blocks = {}
    for ip, block_time in blocked_ips.items():
        expires = block_time + BLOCK_DURATION
        if now < expires:
            remaining = (expires - now).seconds // 60
            active_blocks[ip] = f"{remaining} мин"
    
    return {
        "status": "ok",
        "rate_limit": {
            "requests_per_minute": RATE_LIMIT_REQUESTS,
            "window_seconds": RATE_LIMIT_WINDOW
        },
        "blocked_ips": {
            "count": len(active_blocks),
            "active_blocks": active_blocks
        },
        "attacks": {
            "total_blocked": sum(attack_store.values()),
            "active_attackers": {ip: count for ip, count in attack_store.items() if count > 0}
        },
        "suspicious_patterns": {
            "ua_patterns": len(SUSPICIOUS_UA_PATTERNS),
            "path_patterns": len(SUSPICIOUS_PATHS)
        }
    }
