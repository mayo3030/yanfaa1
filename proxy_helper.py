"""
مساعد البروكسي للطلبات HTTP
"""
import httpx
import config
from typing import Optional, Dict, Any

def get_httpx_client(**kwargs) -> httpx.Client:
    """
    إنشاء عميل httpx مع البروكسي
    
    Args:
        **kwargs: معاملات إضافية لـ httpx.Client
        
    Returns:
        httpx.Client: عميل httpx مع البروكسي المكون
    """
    proxy = None
    if config.PROXY_ENABLED and config.PROXY_URL:
        proxy = config.PROXY_URL
        print(f"🌐 استخدام البروكسي: {config.PROXY_HOST}:{config.PROXY_PORT}")
    
    # إضافة verify=False للبروكسي BrightData
    if proxy:
        kwargs.setdefault('verify', False)
        kwargs.setdefault('timeout', 60.0)
    
    return httpx.Client(
        proxy=proxy,
        **kwargs
    )

def get_async_httpx_client(**kwargs) -> httpx.AsyncClient:
    """
    إنشاء عميل httpx غير متزامن مع البروكسي
    
    Args:
        **kwargs: معاملات إضافية لـ httpx.AsyncClient
        
    Returns:
        httpx.AsyncClient: عميل httpx غير متزامن مع البروكسي المكون
    """
    proxy = None
    if config.PROXY_ENABLED and config.PROXY_URL:
        proxy = config.PROXY_URL
        print(f"🌐 استخدام البروكسي: {config.PROXY_HOST}:{config.PROXY_PORT}")
    
    # إضافة verify=False للبروكسي BrightData
    if proxy:
        kwargs.setdefault('verify', False)
        kwargs.setdefault('timeout', 60.0)
    
    return httpx.AsyncClient(
        proxy=proxy,
        **kwargs
    )

def get_proxy_dict() -> Optional[Dict[str, str]]:
    """
    الحصول على قاموس البروكسي للاستخدام مع مكتبات أخرى
    
    Returns:
        Dict أو None: قاموس البروكسي أو None إذا كان معطلاً
    """
    if config.PROXY_ENABLED and config.PROXY_URL:
        return {
            "http": config.PROXY_URL,
            "https": config.PROXY_URL,
        }
    return None

