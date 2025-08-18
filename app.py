import os
import tempfile

# Mem0 권한 문제 해결
os.environ['MEM0_CONFIG_DIR'] = '/tmp'
os.environ['HOME'] = '/tmp'
os.environ['XDG_DATA_HOME'] = '/tmp'
os.environ['XDG_CONFIG_HOME'] = '/tmp'

import streamlit as st
st.set_page_config(
    page_title="경태의 AI 비교 비서", 
    layout="wide",
    initial_sidebar_state="expanded"
)
import requests
import copy
import json
import os
import uuid
import time
from datetime import datetime

# 🔥 Mem0 임포트를 try-except로 감싸기 (조용하게)
try:
    from mem0 import MemoryClient
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False

# ================== API 키 설정 (영구 저장) ==================
# 환경변수 API 키 비활성화 (보안상 위험)
API_KEY = ""  # 환경변수 사용 안함
MEM0_KEY = ""  # 환경변수 사용 안함

# 세션 상태 초기화
if "user_openrouter_key" not in st.session_state:
    st.session_state.user_openrouter_key = ""
if "user_mem0_key" not in st.session_state:
    st.session_state.user_mem0_key = ""
if "keys_permanently_saved" not in st.session_state:
    st.session_state.keys_permanently_saved = False

# 파일 기반 키 저장/복원 (더 확실한 방법)
KEY_FILE = "/tmp/saved_keys.json"

def save_keys_to_file(openrouter_key, mem0_key=""):
    """키를 파일에 저장"""
    try:
        import json
        data = {
            "openrouter_key": openrouter_key,
            "mem0_key": mem0_key,
            "timestamp": time.time()
        }
        with open(KEY_FILE, "w") as f:
            json.dump(data, f)
        return True
    except:
        return False

def load_keys_from_file():
    """파일에서 키 로드"""
    try:
        import json
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "r") as f:
                data = json.load(f)
            return data.get("openrouter_key", ""), data.get("mem0_key", "")
    except:
        pass
    return "", ""

# 앱 시작 시 저장된 키 자동 로드
if not st.session_state.user_openrouter_key:
    saved_or_key, saved_mem0_key = load_keys_from_file()
    if saved_or_key:
        st.session_state.user_openrouter_key = saved_or_key
        st.session_state.user_mem0_key = saved_mem0_key
        st.session_state.keys_permanently_saved = True

# 현재 키 상태 확인
current_openrouter_key = st.session_state.user_openrouter_key
current_mem0_key = st.session_state.user_mem0_key

if not current_openrouter_key:
    st.markdown("### 🔑 API 키 설정")
    st.info("💡 **보안**: 각자의 API 키를 사용하여 안전하게 AI를 이용하세요!")
    
    # 저장된 키 관리
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📂 저장된 키 확인"):
            saved_or, saved_mem0 = load_keys_from_file()
            if saved_or:
                st.success(f"✅ 저장된 OpenRouter 키: {saved_or[:8]}...")
                if saved_mem0:
                    st.success(f"✅ 저장된 Mem0 키: {saved_mem0[:8]}...")
            else:
                st.warning("❌ 저장된 키가 없습니다.")
    
    with col2:
        if st.button("🗑️ 저장된 키 삭제"):
            try:
                if os.path.exists(KEY_FILE):
                    os.remove(KEY_FILE)
                st.success("🗑️ 저장된 키를 삭제했습니다.")
            except:
                st.error("삭제 실패")
    
    remember_keys = st.checkbox("💾 API 키 영구 저장 (권장)", value=True, 
                               help="체크하면 다음에 접속할 때 자동으로 로그인됩니다.")
    
    with st.form("api_key_form"):
        st.markdown("#### 🚀 필수: OpenRouter (AI 모델)")
        st.info("💰 **예상 비용**: 가벼운 사용 시 월 $1-3 정도")
        openrouter_key = st.text_input("OpenRouter API 키", type="password", help="https://openrouter.ai 에서 발급")
        
        st.markdown("#### 🧠 선택: Mem0 (AI 개인화)")
        st.info("✨ **기능**: AI가 당신의 대화를 기억하고 학습 | 💰 **무료 플랜** 있음")
        mem0_key = st.text_input("Mem0 API 키 (선택사항)", type="password", help="https://mem0.ai 에서 발급 (없어도 기본 기능 사용 가능)")
        
        submitted = st.form_submit_button("🚀 시작하기", use_container_width=True)
        
        if submitted:
            if openrouter_key:
                st.session_state.user_openrouter_key = openrouter_key
                st.session_state.user_mem0_key = mem0_key if mem0_key else ""
                
                if remember_keys:
                    if save_keys_to_file(openrouter_key, mem0_key):
                        st.session_state.keys_permanently_saved = True
                        st.success("💾 API 키가 영구 저장되었습니다!")
                    else:
                        st.warning("⚠️ 키 저장에 실패했지만 이번 세션에서는 사용 가능합니다.")
                
                if mem0_key:
                    st.success("✅ 모든 API 키가 설정되었어요! (개인화 기능 포함)")
                else:
                    st.success("✅ OpenRouter API 키가 설정되었어요! (기본 기능)")
                    st.info("💡 나중에 Mem0 키를 추가하면 AI 개인화 기능을 사용할 수 있어요!")
                
                st.balloons()
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ OpenRouter API 키는 필수입니다!")
    
    # 가이드 표시
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🤖 OpenRouter 가입 방법:**
        1. https://openrouter.ai 접속
        2. 이메일로 회원가입
        3. Dashboard → API Keys → Create Key
        4. 키 복사해서 위에 붙여넣기
        """)
    
    with col2:
        st.markdown("""
        **🧠 Mem0 가입 방법 (선택):**
        1. https://mem0.ai 접속
        2. 이메일로 회원가입
        3. API Keys → Generate Key
        4. 키 복사해서 위에 붙여넣기
        """)
    
    st.stop()

# 현재 사용 중인 키를 환경변수에 설정 (임시)
if current_openrouter_key:
    os.environ["OPENROUTER_API_KEY"] = current_openrouter_key
if current_mem0_key:
    os.environ["MEM0_API_KEY"] = current_mem0_key

SAVE_PATH = "chat_history.json"

@st.cache_data(ttl=60)  # 1분마다 갱신
def get_available_models():
    """OpenRouter에서 사용 가능한 모델들을 자동으로 가져와서 우리가 원하는 형태로 변환"""
    
    # 일단 기본 모델들 정의 (안전장치)
    default_models = {
        "GPT-4o": ("GPT-4o", "openai/gpt-4o", True, "#f1f1f1", "left"),
        "Claude": ("Claude 3.5 Sonnet", "anthropic/claude-3.5-sonnet", True, "#ffe4e1", "right"),
        "Gemini": ("Gemini 2.0 Flash", "google/gemini-2.0-flash-exp", True, "#e6f7ff", "left"),
        "LLaMA": ("LLaMA 3.1 405B", "meta-llama/llama-3.1-405b-instruct", True, "#ede7f6", "right")
    }
    
    try:
        # OpenRouter API에서 모델 목록 가져오기
        response = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        
        if response.status_code == 200:
            api_data = response.json()
            new_models = {}
            
            # API 응답에서 data 배열 가져오기
            for model in api_data.get("data", []):
                model_id = model.get("id", "")
                model_name = model.get("name", "")
                
                if model_id and model_name:
                    # 이미지 지원 여부 확인
                    supports_vision = False
                    if "modalities" in model:
                        supports_vision = "image" in model.get("modalities", [])
                    else:
                        vision_keywords = ["vision", "gpt-4", "claude", "gemini"]
                        supports_vision = any(keyword in model_id.lower() for keyword in vision_keywords)
                    
                    # 색상과 위치 매핑
                    if "gpt" in model_id.lower() or "openai" in model_id.lower():
                        color, side = "#f1f1f1", "left"
                        brand = "GPT"
                    elif "claude" in model_id.lower() or "anthropic" in model_id.lower():
                        color, side = "#ffe4e1", "right"
                        brand = "Claude"
                    elif "gemini" in model_id.lower() or "google" in model_id.lower():
                        color, side = "#e6f7ff", "left"
                        brand = "Gemini"
                    elif "llama" in model_id.lower() or "meta" in model_id.lower():
                        color, side = "#ede7f6", "right"
                        brand = "LLaMA"
                    else:
                        color, side = "#f5f5f5", "left"
                        brand = "기타"
                    
                    # 표시용 이름 생성
                    display_name = model_name
                    if len(model_name) > 30:
                        display_name = f"{brand} {model_id.split('/')[-1][:20]}"
                    
                    new_models[display_name] = (model_name, model_id, supports_vision, color, side)
            
            # 새로운 모델이 있으면 반환
            if new_models:
                new_models["🤖 자동 선택 (OpenRouter가 최적 AI 선택)"] = ("OpenRouter Auto", "auto", True, "#e6ffe6", "center")
                return new_models
        
    except Exception as e:
        # 실패 시 사용자에게 알림
        if hasattr(st, 'warning'):
            st.warning("⚠️ 최신 모델 목록을 가져올 수 없어 기본 모델을 사용합니다.")
        pass
    
    # 모든 것이 실패하면 기본 모델들 반환
    return default_models

# 모델 정보 가져오기
models = get_available_models()

# ================== Mem0 초기화 (하이브리드 방식) ==================
@st.cache_resource
def init_mem0():
    """Mem0 클라이언트 초기화 (하이브리드 방식)"""
    if not MEM0_AVAILABLE:
        return None
    
    mem0_key = os.environ.get("MEM0_API_KEY", "") or st.session_state.get("user_mem0_key", "")
    
    if not mem0_key:
        return None
        
    try:
        return MemoryClient(api_key=mem0_key)
    except Exception as e:
        return None

memory_client = init_mem0()

# ================== 실시간 알림 시스템 ==================
def show_learning_notification(learning_type, content=""):
    """실시간 학습 알림 표시"""
    notifications = {
        "ai_preference": f"🤖 AI 선호도 기록: {content}",
        "conversation": f"💭 대화 내용 저장: {content}",
        "preference": f"❤️ 사용자 피드백 저장: {content}",
    }
    
    message = notifications.get(learning_type, f"🧠 새로운 기록: {content}")
    st.toast(message, icon="🧠")

# ================== Mem0 관련 함수들 ==================
def get_user_id():
    """사용자 ID 생성 또는 가져오기"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"
    return st.session_state.user_id

def classify_question_type(question):
    """질문 유형 분류"""
    question_lower = question.lower()
    if any(keyword in question_lower for keyword in [
        "코딩", "프로그래밍", "코드", "개발", "디버그", "함수", "알고리즘", 
        "python", "javascript", "html", "css"
    ]):
        return "coding"
    elif any(keyword in question_lower for keyword in [
        "창작", "소설", "시", "글쓰기", "스토리", "시나리오", "에세이"
    ]):
        return "creative"
    elif any(keyword in question_lower for keyword in [
        "분석", "데이터", "연구", "논문", "통계", "차트", "그래프"
    ]):
        return "analysis"
    elif any(keyword in question_lower for keyword in [
        "빠른", "간단", "요약", "짧게", "한줄로", "간략하게"
    ]):
        return "quick"
    else:
        return "general"

def learn_ai_preference_with_feedback(user_id, question, selected_ai):
    """AI 선택 패턴 학습"""
    if not memory_client:
        return
    
    try:
        question_type = classify_question_type(question)
        memory_content = f"사용자는 {question_type} 질문에 대해 {selected_ai} AI를 선택했습니다."
        
        metadata = {
            "type": "ai_preference",
            "selected_ai": selected_ai,
        }
        
        result = memory_client.add(memory_content, user_id=user_id, metadata=metadata)
        
        if result:
            show_learning_notification("ai_preference", f"{question_type} → {selected_ai}")
        
    except Exception:
        pass

def get_preferred_ai(user_id, question):
    """학습된 선호도를 바탕으로 AI 추천"""
    if not memory_client:
        return None, "메모리 비활성화"
    
    try:
        question_type = classify_question_type(question)
        memories = memory_client.search(f"{question_type} AI 선호도", user_id=user_id, limit=10)
        
        if memories:
            ai_count = {}
            for memory in memories:
                metadata = memory.get('metadata', {})
                if metadata.get('type') == 'ai_preference' and metadata.get('question_type') == question_type:
                    ai_name = metadata.get('selected_ai', '')
                    ai_count[ai_name] = ai_count.get(ai_name, 0) + 1
            
            if ai_count:
                preferred_ai = max(ai_count, key=ai_count.get)
                return preferred_ai, f"🧠 학습된 선호도 (사용횟수: {ai_count[preferred_ai]}회)"
        
        return None, "학습 데이터 없음"
    except Exception:
        return None, "메모리 검색 실패"

def smart_ai_selection_with_memory(user_id, question):
    """똑똑한 AI 선택"""
    
    # 1. Mem0가 있으면 학습된 선호도 확인
    if memory_client:
        preferred_ai, reason = get_preferred_ai(user_id, question)
        
        if preferred_ai and "claude" in preferred_ai:
            claude4_id = None
            for name, (_, model_id_check, _, _, _) in models.items():
                if "anthropic" in name.lower() and "sonnet 4" in name.lower():
                    claude4_id = model_id_check
                    break
            
            if claude4_id:
                return claude4_id, f"🧠 {reason}"
    
    # 2. 기본 로직
    question_text = question.lower()
    claude4_id = None
    for name, (_, model_id_check, _, _, _) in models.items():
        if "anthropic" in name.lower() and "sonnet 4" in name.lower():
            claude4_id = model_id_check
            break
    
    if any(keyword in question_text for keyword in [
        "코딩", "프로그래밍", "코드", "개발", "디버그", "함수", "알고리즘"
    ]):
        selected_ai = claude4_id if claude4_id else "anthropic/claude-3.5-sonnet"
        reason = "🔧 코딩 전문"
    elif any(keyword in question_text for keyword in [
        "창작", "소설", "시", "글쓰기", "스토리", "시나리오", "에세이"
    ]):
        selected_ai = "openai/gpt-4o"
        reason = "✍️ 창작 전문"
    elif any(keyword in question_text for keyword in [
        "분석", "데이터", "연구", "논문", "통계", "차트", "그래프"
    ]):
        selected_ai = claude4_id if claude4_id else "anthropic/claude-3.5-sonnet"
        reason = "📊 분석 전문"
    elif any(keyword in question_text for keyword in [
        "빠른", "간단", "요약", "짧게", "한줄로", "간략하게"
    ]):
        selected_ai = "google/gemini-2.0-flash-exp"
        reason = "⚡ 빠른 응답"
    else:
        selected_ai = claude4_id if claude4_id else "anthropic/claude-3.5-sonnet"
        reason = "🤖 범용 응답"
    
    return selected_ai, reason

def store_conversation_memory_with_feedback(user_id, question, answer, ai_model):
    """대화 내용을 장기 기억에 저장"""
    if not memory_client:
        return
    
    try:
        question_summary = question[:100] + "..." if len(question) > 100 else question
        answer_summary = answer[:150] + "..." if len(answer) > 150 else answer
        
        conversation_summary = f"Q: {question_summary} A: {answer_summary}"
        
        metadata = {
            "type": "conversation",
            "ai_model": ai_model,
        }
        
        result = memory_client.add(conversation_summary, user_id=user_id, metadata=metadata)
        
        if result:
            show_learning_notification("conversation", f"{ai_model}와의 대화")
        
    except Exception:
        pass

def get_relevant_context(user_id, current_question, limit=3):
    """현재 질문과 관련된 과거 대화 찾기"""
    if not memory_client:
        return ""
    
    try:
        memories = memory_client.search(current_question, user_id=user_id, limit=limit)
        
        if memories:
            context = "🧠 **과거 관련 대화:**\n"
            for memory in memories:
                context += f"- {memory['memory'][:100]}...\n"
            return context + "\n"
        
        return ""
    except Exception:
        return ""

def learn_user_preferences_with_feedback(user_id, feedback_type, context):
    """사용자 선호도 학습"""
    if not memory_client:
        return
    
    try:
        preference_data = f"사용자 피드백: {feedback_type} - {context}"
        
        metadata = {
            "type": "preference",
            "feedback": feedback_type,
            "timestamp": time.time()
        }
        
        result = memory_client.add(preference_data, user_id=user_id, metadata=metadata)
        
        if result:
            feedback_msg = "긍정적 피드백" if feedback_type == "like" else "개선 요청"
            show_learning_notification("preference", feedback_msg)
        
    except Exception as e:
        pass

def get_user_personality_profile(user_id):
    """사용자 성격/선호도 프로필 생성"""
    if not memory_client:
        return "일반적인 사용자"
    
    try:
        memories = memory_client.search("사용자", user_id=user_id, limit=20)
        
        if len(memories) > 5:
            return "경험이 풍부한 사용자 (맞춤형 응답 제공)"
        elif len(memories) > 2:
            return "학습 중인 사용자 (친절한 설명 제공)"
        else:
            return "새로운 사용자 (기본 도움말 제공)"
    except Exception:
        return "일반적인 사용자"

def get_all_memories(user_id, limit=50):
    """사용자의 모든 메모리 가져오기"""
    if not memory_client:
        return []
    
    try:
        memories = memory_client.search("", user_id=user_id, limit=limit)
        return memories
    except Exception:
        return []

def get_memory_stats_with_cache(user_id):
    """메모리 통계 정보"""
    if not memory_client:
        return {"total": 0, "conversation": 0, "ai_preference": 0, "preference": 0}
    
    try:
        memories = memory_client.search("사용자", user_id=user_id, limit=50)
        
        stats = {
            "total": len(memories),
            "conversation": 0,
            "ai_preference": 0,
            "preference": 0
        }
        
        for memory in memories:
            try:
                memory_content = str(memory.get('memory', '')).lower()
                
                if 'ai를 선택' in memory_content or '선호도' in memory_content:
                    stats['ai_preference'] += 1
                elif '피드백' in memory_content:
                    stats['preference'] += 1
                else:
                    stats['conversation'] += 1
            except Exception:
                stats['conversation'] += 1
        
        return stats
        
    except Exception as e:
        return {"total": 0, "conversation": 0, "ai_preference": 0, "preference": 0}

# ================== API 헤더 설정 ==================
def get_headers():
    """API 헤더 생성"""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

# ================== 크레딧 표시 ==================
@st.cache_data(ttl=300)  # 5분간 캐시
def get_credit_balance():
    try:
        res = requests.get("https://openrouter.ai/api/v1/auth/key", headers=get_headers(), timeout=3)
        if res.status_code == 200:
            data = res.json().get("data", {})
            usage = data.get("usage", 0)
            
            if isinstance(usage, (int, float)):
                return usage
            else:
                return "API 응답 오류"
        else:
            return f"HTTP {res.status_code}"
    except requests.exceptions.Timeout:
        return "연결 시간 초과"
    except requests.exceptions.ConnectionError:
        return "네트워크 연결 실패"
    except Exception as e:
        return "연결 불가"

credit = get_credit_balance()

# 크레딧 상태에 따른 표시
if isinstance(credit, (int, float)):
    if credit == 0:
        credit_display = f"💳 크레딧: 무료 사용 중"
        credit_color = "#4CAF50"
    elif credit < 1:
        credit_display = f"💳 사용 크레딧: ${credit:.3f}"
        credit_color = "#4CAF50"
    elif credit < 5:
        credit_display = f"💳 사용 크레딧: ${credit:.2f}"
        credit_color = "#FF9800"
    else:
        credit_display = f"💳 사용 크레딧: ${credit:.1f}"
        credit_color = "#F44336"
else:
    credit_display = f"💳 크레딧 확인 불가"
    credit_color = "#9E9E9E"

memory_status = "🧠 AI 개인화 활성화" if memory_client else "💻 기본 모드"

# ================== ChatGPT 스타일 ==================
st.markdown("""
    <style>
        .stApp {
            background-color: #f9f9f9 !important;
        }
        
        .main .block-container {
            max-width: 900px !important;
            padding: 2rem 1rem 1rem 1rem !important;  /* 상단 패딩 증가 */
            background: transparent !important;
        }
        
        /* 헤더 개선 */
        .chat-header {
            background: white !important;
            padding: 1.5rem !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
            margin-bottom: 1rem !important;  /* 마진 줄임 */
            text-align: center;
            border: 1px solid #e5e5e5 !important;
        }
        
        .chat-title {
            font-size: 28px;
            font-weight: 700;
            color: #202123;
            margin-bottom: 0.5rem;
        }
        
        .chat-subtitle {
            font-size: 14px;
            color: #6e6e80;
            font-weight: 400;
        }
        
        /* 입력 영역 - 새 대화 버튼 제거 */
        .input-container {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e5e5e5;
        }
        
        .stMultiSelect > div > div {
            border: 2px solid #e5e5e5 !important;
            border-radius: 12px !important;
            background: white !important;
        }
        
        .stMultiSelect > div > div:focus-within {
            border-color: #10a37f !important;
            box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1) !important;
        }
        
        .stChatInputContainer {
            border: none !important;
            background: transparent !important;
        }
        
        .stChatInputContainer > div {
            background: white !important;
            border: 2px solid #e5e5e5 !important;
            border-radius: 16px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
            display: flex !important;
            align-items: center !important;  /* 수직 중앙 정렬 */
        }
        
        .stChatInputContainer textarea {
            border: none !important;
            background: transparent !important;
            font-size: 16px !important;
            padding: 1rem 1.5rem !important;
            line-height: 1.5 !important;  /* 텍스트 라인 높이 조정 */
        }
        
        .stChatInputContainer textarea:focus {
            border-color: #10a37f !important;
            box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1) !important;
        }
        
        /* 보내기 버튼 정렬 */
        .stChatInputContainer button {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0.5rem !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background: white !important;
            border-radius: 12px !important;
            padding: 0.5rem !important;
            border: 1px solid #e5e5e5 !important;
            margin-bottom: 1.5rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border-radius: 8px !important;
            color: #6e6e80 !important;
            font-weight: 500 !important;
            padding: 0.75rem 1.5rem !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: #10a37f !important;
            color: white !important;
            box-shadow: 0 2px 4px rgba(16, 163, 127, 0.2) !important;
        }
        
        /* 사이드바 개선 */
        .css-1d391kg {
            background: #f7f7f8 !important;
            border-right: 1px solid #e5e5e5 !important;
            padding: 0 !important;
        }
        
        /* 섹션 헤더 */
        .sidebar-header {
            color: #374151;
            font-size: 13px;
            font-weight: 600;
            padding: 1rem 1rem 0.5rem 1rem;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* 메뉴 아이템 - 크기 줄임 */
        .sidebar-item {
            margin: 0 0.5rem 0.25rem 0.5rem;
            border-radius: 6px;
            overflow: hidden;
        }
        
        .sidebar-item .stButton > button {
            width: 100% !important;
            border: none !important;
            background: transparent !important;
            color: #374151 !important;
            text-align: left !important;
            padding: 0.5rem 0.75rem !important;  /* 패딩 줄임 */
            font-size: 13px !important;  /* 폰트 크기 줄임 */
            font-weight: 400 !important;
            border-radius: 6px !important;
            transition: all 0.15s ease !important;
            line-height: 1.2 !important;
        }
        
        .sidebar-item .stButton > button:hover {
            background: #e5e7eb !important;
            color: #111827 !important;
            transform: none !important;
            box-shadow: none !important;
        }
        
        /* 새 채팅 버튼 특별 스타일 */
        .new-chat-btn .stButton > button {
            background: #f3f4f6 !important;
            border: 1px solid #d1d5db !important;
            font-weight: 500 !important;
            padding: 0.75rem 1rem !important;  /* 새 채팅은 좀 더 크게 */
        }
        
        .new-chat-btn .stButton > button:hover {
            background: #e5e7eb !important;
            border-color: #9ca3af !important;
        }
        
        /* 대화 항목 특별 스타일 */
        .chat-item {
            display: flex !important;
            align-items: center !important;
            padding: 0.5rem 0.5rem !important;
        }
        
        .chat-item .stButton > button {
            font-size: 12px !important;  /* 더 작게 */
            padding: 0.4rem 0.6rem !important;  /* 더 작게 */
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            max-width: 100% !important;
        }
        
        /* 삭제 버튼 스타일 */
        .delete-btn {
            width: 28px !important;
            height: 28px !important;
            padding: 0 !important;
            min-width: 28px !important;
            margin-left: 4px !important;
        }
        
        .delete-btn .stButton > button {
            width: 28px !important;
            height: 28px !important;
            padding: 0 !important;
            font-size: 12px !important;
            border-radius: 4px !important;
            background: transparent !important;
            color: #9ca3af !important;
        }
        
        .delete-btn .stButton > button:hover {
            background: #fee2e2 !important;
            color: #dc2626 !important;
        }
        
        /* 진행도 바 */
        .progress-bar {
            background: #e5e7eb;
            height: 6px;
            border-radius: 3px;
            overflow: hidden;
            margin: 0.5rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #059669);
            transition: width 0.3s ease;
            border-radius: 3px;
        }
        
        /* 상태 아이콘 */
        .status-icon {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-active { background: #10b981; }
        .status-inactive { background: #9ca3af; }
        
        /* 구분선 */
        .sidebar-divider {
            height: 1px;
            background: #e5e7eb;
            margin: 1rem 0;
        }
        
        /* 메트릭 카드 */
        .metric-mini {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 0.6rem;  /* 패딩 줄임 */
            margin: 0.25rem 0;
            text-align: center;
        }
        
        .metric-number {
            font-size: 18px;  /* 크기 줄임 */
            font-weight: 700;
            color: #10b981;
            line-height: 1;
        }
        
        .metric-label {
            font-size: 10px;
            color: #6b7280;
            margin-top: 2px;
        }
        
        .stButton > button {
            border-radius: 8px !important;
            border: 1px solid #e5e5e5 !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        @media (max-width: 768px) {
            .main .block-container {
                padding: 0.5rem !important;
            }
            
            .chat-header {
                padding: 0.5rem 0 !important;
            }
            
            .input-container {
                padding: 1rem !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# 헤더 부분 - 더 컴팩트하게
st.markdown(f"""
<div class="chat-header">
    <div class="chat-title">🤖 AI 비교 비서</div>
    <div class="chat-subtitle">
        <span style="color: {credit_color};">{credit_display}</span> • 
        <span style="color: #10a37f;">{memory_status}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ================== 컴팩트한 통합 영역 ==================

# 안전한 기본값 설정
available_models = list(models.keys())
safe_defaults = []

# 기본값으로 자동 선택을 우선 설정
for model_key in available_models:
    if "자동 선택" in model_key:
        safe_defaults = [model_key]
        break

# 자동 선택이 없으면 기존 로직
if not safe_defaults:
    for model_key in available_models:
        if any(keyword in model_key.lower() for keyword in ["gpt", "claude"]):
            safe_defaults.append(model_key)
            if len(safe_defaults) >= 2:
                break
        if len(safe_defaults) >= 2:
            break

# 만약 아무것도 못 찾으면 첫 번째 모델 사용
if not safe_defaults and available_models:
    safe_defaults = [available_models[0]]

selected = st.multiselect(
    "🤖 AI 모델 선택", 
    available_models, 
    default=safe_defaults,
    help="비교할 AI 모델 선택",
    placeholder="AI 모델을 선택하세요"
)

st.markdown('</div>', unsafe_allow_html=True)

if not selected:
    st.warning("⚠️ AI 모델을 최소 1개는 선택해주세요!")
    st.stop()

user_input = st.chat_input("💬 무엇을 도와드릴까요? (Shift+Enter로 줄바꿈)")

# ================== 저장/불러오기 ==================
def save_logs():
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "logs": st.session_state.logs[-50:],  # 최근 50개만 저장
                "chat_log": {
                    key: value[-20:] if isinstance(value, list) else value  # 각 모델당 최근 20개만
                    for key, value in st.session_state.chat_log.items()
                }
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"⚠️ 로그 저장 실패: {e}")

def load_logs():
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.logs = data.get("logs", [])
                st.session_state.chat_log = {
                    key: data.get("chat_log", {}).get(key, []) 
                    for key in models
                }
        except Exception:
            pass

# 세션 상태 초기화 (모델 변경에 대응)
if "logs" not in st.session_state:
    st.session_state.logs = []
if "chat_log" not in st.session_state:
    st.session_state.chat_log = {}

# 새로운 모델이 추가되었을 때 대응
for key in models:
    if key not in st.session_state.chat_log:
        st.session_state.chat_log[key] = []
    
load_logs()

# ================== 채팅 거품 ==================
def render_chat_bubble(name, content, side="left", color="#f1f1f1"):
    """ChatGPT 스타일 채팅 버블"""
    
    is_user = name == "경태"
    
    if is_user:
        # 사용자 메시지 (우측)
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
            <div style="background: linear-gradient(135deg, #10a37f, #0d8f6f); 
                        color: white; padding: 0.75rem 1rem; 
                        border-radius: 1rem 1rem 0.25rem 1rem;
                        max-width: 70%; font-size: 0.9rem; line-height: 1.4;">
                <strong style="font-size: 0.75rem; opacity: 0.9;">{name}</strong><br>
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # AI 메시지 (좌측)
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start; margin-bottom: 1rem;">
            <div style="background: #f8f9fa; color: #2d3748; 
                        padding: 0.75rem 1rem; border-radius: 1rem 1rem 1rem 0.25rem;
                        max-width: 70%; font-size: 0.9rem; line-height: 1.4;
                        border: 1px solid #e2e8f0;">
                <strong style="color: #10a37f; font-size: 0.75rem;">{name}</strong><br>
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================== 응답 요청 ==================
if user_input and user_input.strip():
    user_id = get_user_id()
    
    # 과거 관련 대화 가져오기
    relevant_context = get_relevant_context(user_id, user_input) if memory_client else ""
    
    # 사용자 프로필 확인
    user_profile = get_user_personality_profile(user_id) if memory_client else "일반적인 사용자"
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, key in enumerate(selected):
        name, model_id, supports_image, color, side = models[key]
        
        progress_bar.progress((idx + 1) / len(selected))
        status_text.text(f"🤖 {name} 응답 중...")
        
        try:
            messages = st.session_state.chat_log.get(key, []).copy()

            # 메모리 기반 컨텍스트 추가 (토큰 절약)
            enhanced_input = user_input.strip()
            if relevant_context and len(relevant_context) < 500:  # 너무 긴 컨텍스트 방지
                enhanced_input = f"{relevant_context}\n**현재 질문:** {user_input.strip()}"

            messages.append(("user", enhanced_input))

            # API 호출용 포맷
            formatted_messages = []
            for role, content in messages[-8:]:  # 최근 8개만
                formatted_messages.append({"role": role, "content": content})

            # 사용자 프로필 기반 시스템 프롬프트
            system_prompt = {
                "role": "system", 
                "content": f"""너는 항상 반말을 쓰고 친구처럼 친근하게 대화해. 존댓말은 절대 사용하지 마!
사용자 프로필: {user_profile}
- 이 정보를 바탕으로 적절한 수준의 설명을 제공해줘."""
            }
            
            # AI 선택 학습
            if memory_client and model_id != "auto":
                learn_ai_preference_with_feedback(user_id, user_input, name)
            
            # 자동 라우팅
            if model_id == "auto":
                question_text = user_input.lower()
                
                # 맥락이 필요한 키워드들
                context_keywords = [
                    "이거", "그거", "저거", "여기서", "거기서", "이것", "그것", "저것",
                    "위에서", "앞에서", "이전", "방금", "아까", "계속", "더", "추가",
                    "수정", "바꿔", "고쳐", "개선", "this", "that", "here", "there",
                    "above", "previous", "continue", "more", "add", "modify", "fix"
                ]
                
                # 이전 대화가 있고, 맥락이 필요한 질문이면
                has_previous_chat = bool(st.session_state.chat_log.get(key, []))
                needs_context = any(keyword in question_text for keyword in context_keywords)
                
                if has_previous_chat and needs_context:
                    # 맥락 유지
                    claude4_id = None
                    for name_check, (_, model_id_check, _, _, _) in models.items():
                        if "anthropic" in name_check.lower() and "sonnet 4" in name_check.lower():
                            claude4_id = model_id_check
                            break
                    selected_model = claude4_id if claude4_id else "anthropic/claude-3.5-sonnet"
                    auto_reason = "🔗 대화 맥락 유지"
                else:
                    # 새로운 주제 → 스마트 AI 선택
                    selected_model, auto_reason = smart_ai_selection_with_memory(user_id, user_input)
                
                body = {
                    "model": selected_model,
                    "messages": [system_prompt] + formatted_messages,
                    "max_tokens": 1500,
                    "temperature": 0.7,
                    "stream": False
                }
                
                status_text.text(f"🎯 자동선택: {auto_reason}")
                
            else:
                body = {
                    "model": model_id,
                    "messages": [system_prompt] + formatted_messages,
                    "max_tokens": 1500,
                    "temperature": 0.7,
                    "stream": False
                }

            # API 요청
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=get_headers(),
                json=body,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and data["choices"]:
                    res_text = data["choices"][0]["message"]["content"]
                    
                    # 모든 성공적인 대화를 메모리에 저장
                    if memory_client:
                        store_conversation_memory_with_feedback(user_id, user_input, res_text, name)
                    
                    # 자동 선택일 때 실제 사용된 모델 표시
                    if model_id == "auto":
                        used_model = data.get("model", "unknown")
                        model_name = used_model.split('/')[-1] if '/' in used_model else used_model
                        res_text = f"🎯 **OpenRouter 선택**: {model_name}\n\n{res_text}"
                        
                        # 자동 선택된 AI도 선호도 학습
                        if memory_client:
                            learn_ai_preference_with_feedback(user_id, user_input, model_name)
                    
                    # 세션에 저장
                    if key not in st.session_state.chat_log:
                        st.session_state.chat_log[key] = []
                    
                    st.session_state.chat_log[key].append(("user", user_input.strip()))
                    st.session_state.chat_log[key].append(("assistant", res_text))
                else:
                    st.error(f"❌ {name}: 응답 데이터 오류")
            else:
                st.error(f"❌ {name}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            st.error(f"❌ {name}: 응답 시간 초과")
        except Exception as e:
            st.error(f"❌ {name}: {str(e)[:100]}")
    
    progress_bar.progress(1.0)
    status_text.text("✅ 모든 응답 완료!")
    time.sleep(1)
    progress_bar.empty()
    status_text.empty()
    
    save_logs()
    st.rerun()

# ================== 결과 표시 ==================
if any(st.session_state.chat_log.get(model, []) for model in selected):
    tab1, tab2 = st.tabs(["💬 전체 대화", "📊 응답 비교"])
    
    with tab1:
        # 스크롤 가능한 컨테이너 추가
        st.markdown("""
        <style>
        .chat-container {
            max-height: 70vh;
            overflow-y: auto;
            padding-right: 10px;
        }
        .chat-container::-webkit-scrollbar {
            width: 6px;
        }
        .chat-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
        }
        .chat-container::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
        }
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for key in selected:
            chat = st.session_state.chat_log.get(key, [])
            if chat:
                name, _, _, color, side = models[key]
                st.markdown(f"### 🤖 {name}")
                
                for role, content in chat:
                    bubble_name = "경태" if role == "user" else name
                    bubble_color = "#e8f5e8" if role == "user" else color
                    bubble_side = "left" if role == "user" else side
                    
                    if isinstance(content, list):
                        text_content = next((p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"), str(content))
                    else:
                        text_content = str(content)
                    
                    render_chat_bubble(bubble_name, text_content, bubble_side, bubble_color)
                
                st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        # 질문별 응답 비교
        questions = {}
        
        for model in selected:
            chat = st.session_state.chat_log.get(model, [])
            for i in range(0, len(chat) - 1, 2):
                if (i + 1 < len(chat) and 
                    chat[i][0] == "user" and 
                    chat[i + 1][0] == "assistant"):
                    
                    user_msg = chat[i][1]
                    assistant_msg = chat[i + 1][1]
                    
                    # 텍스트 추출
                    if isinstance(user_msg, list):
                        q_text = next((p.get("text", "") for p in user_msg if isinstance(p, dict) and p.get("type") == "text"), "")
                    else:
                        q_text = str(user_msg)
                    
                    if q_text.strip():
                        if q_text not in questions:
                            questions[q_text] = {}
                        questions[q_text][model] = str(assistant_msg)

        for question, answers in questions.items():
            st.markdown(f"### 📌 **{question}**")
            
            cols = st.columns(len(selected))
            for col, model in zip(cols, selected):
                with col:
                    name = models[model][0]
                    st.markdown(f"**🤖 {name}**")
                    answer = answers.get(model, "❌ 응답 없음")
                    st.markdown(f"""
                        <div style='background: #fafafa; padding: 15px; border-radius: 10px; 
                                    border-left: 4px solid #4CAF50; min-height: 120px;
                                    font-size: 15px; line-height: 1.4; white-space: pre-wrap;'>
                            {answer}
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

# ================== Claude 스타일 사이드바 ==================
with st.sidebar:
    # 1. 채팅 섹션
    st.markdown('<p class="sidebar-header">채팅</p>', unsafe_allow_html=True)
    
    # 새 채팅 버튼
    st.markdown('<div class="sidebar-item new-chat-btn">', unsafe_allow_html=True)
    if st.button("✨ 새 채팅", key="sidebar_new_chat", use_container_width=True):
        # 현재 대화 저장
        if any(st.session_state.chat_log.get(model, []) for model in selected if model in st.session_state.chat_log):
            title = f"대화_{time.strftime('%m/%d_%H:%M')}"
            for model in selected:
                chat = st.session_state.chat_log.get(model, [])
                for role, content in reversed(chat):
                    if role == "user":
                        if isinstance(content, list):
                            text = next((p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"), "")
                        else:
                            text = str(content)
                        if text.strip():
                            title = text.strip()[:25] + ("..." if len(text.strip()) > 25 else "")
                            break
                if "대화_" not in title:
                    break
            
            st.session_state.logs.append((title, copy.deepcopy(st.session_state.chat_log)))
            save_logs()
        
        # 초기화
        st.session_state.chat_log = {key: [] for key in models}
        save_logs()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. AI 학습 현황 섹션
    if memory_client:
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-header">AI 학습 현황</p>', unsafe_allow_html=True)
        
        user_id = get_user_id()
        memory_stats = get_memory_stats_with_cache(user_id)
        personalization_score = min(100, memory_stats["total"] * 5)
        
        # 미니 메트릭 카드들
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-mini">
                <div class="metric-number">{memory_stats["conversation"]}</div>
                <div class="metric-label">대화</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-mini">
                <div class="metric-number">{memory_stats["total"]}</div>
                <div class="metric-label">총 기록</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 진행도 바
        progress_color = "#10b981" if personalization_score >= 70 else "#f59e0b" if personalization_score >= 30 else "#ef4444"
        st.markdown(f"""
        <div style="padding: 0 1rem;">
            <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">
                개인화 {personalization_score}%
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {personalization_score}%; background: {progress_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 피드백 버튼 (간소화)
        if any(st.session_state.chat_log.get(model, []) for model in models):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="sidebar-item">', unsafe_allow_html=True)
                if st.button("👍", key="sidebar_like", use_container_width=True, help="좋은 응답"):
                    learn_user_preferences_with_feedback(user_id, "like", "최근 응답에 만족")
                    st.toast("👍 피드백 저장!", icon="✅")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="sidebar-item">', unsafe_allow_html=True)
                if st.button("👎", key="sidebar_dislike", use_container_width=True, help="아쉬운 응답"):
                    learn_user_preferences_with_feedback(user_id, "dislike", "최근 응답에 불만족")
                    st.toast("👎 피드백 저장!", icon="✅")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # 3. 최근 항목 섹션 (개선됨)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-header">최근 항목</p>', unsafe_allow_html=True)
    
    if st.session_state.logs:
        # 최근 5개 대화 표시 (크기 개선)
        for i, (title, log) in enumerate(reversed(st.session_state.logs[-5:]), 1):
            idx = len(st.session_state.logs) - i
            
            # 대화 항목 - 정렬 개선
            st.markdown('<div class="chat-item">', unsafe_allow_html=True)
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown('<div class="sidebar-item">', unsafe_allow_html=True)
                # 제목 길이 제한
                display_title = title[:20] + "..." if len(title) > 20 else title
                if st.button(f"💬 {display_title}", key=f"load_{i}", use_container_width=True):
                    st.session_state.chat_log = copy.deepcopy(log)
                    save_logs()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                if st.button("🗑", key=f"del_{i}", help="삭제", use_container_width=True):
                    st.session_state.logs.pop(idx)
                    save_logs()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 더보기 (5개 이상일 때)
        if len(st.session_state.logs) > 5:
            with st.expander(f"⋯ {len(st.session_state.logs) - 5}개 더보기", expanded=False):
                for i, (title, log) in enumerate(reversed(st.session_state.logs[:-5]), 6):
                    idx = len(st.session_state.logs) - i
                    
                    st.markdown('<div class="chat-item">', unsafe_allow_html=True)
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        display_title = title[:20] + "..." if len(title) > 20 else title
                        if st.button(f"💬 {display_title}", key=f"load_old_{i}", use_container_width=True):
                            st.session_state.chat_log = copy.deepcopy(log)
                            save_logs()
                            st.rerun()
                    with col2:
                        st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                        if st.button("🗑", key=f"del_old_{i}", use_container_width=True):
                            st.session_state.logs.pop(idx)
                            save_logs()
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding: 1rem; text-align: center; color: #9ca3af; font-size: 13px;">
            저장된 대화가 없습니다
        </div>
        """, unsafe_allow_html=True)
    
    # 4. 설정 섹션 (하단)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-header">설정</p>', unsafe_allow_html=True)
    
    # API 상태 (컴팩트)
    openrouter_status = "status-active" if current_openrouter_key else "status-inactive"
    mem0_status = "status-active" if memory_client else "status-inactive"
    
    st.markdown(f"""
    <div style="padding: 0 1rem; font-size: 12px; color: #6b7280;">
        <div style="margin-bottom: 0.5rem;">
            <span class="status-icon {openrouter_status}"></span>OpenRouter
        </div>
        <div>
            <span class="status-icon {mem0_status}"></span>Mem0 개인화
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 설정 버튼들
    if st.session_state.get("user_openrouter_key") or st.session_state.get("user_mem0_key"):
        st.markdown('<div class="sidebar-item">', unsafe_allow_html=True)
        if st.button("⚙️ API 키 재설정", key="reset_api", use_container_width=True):
            st.session_state.user_openrouter_key = ""
            st.session_state.user_mem0_key = ""
            st.markdown("""
            <script>
            localStorage.removeItem('openrouter_key');
            localStorage.removeItem('mem0_key');
            localStorage.removeItem('keys_saved');
            </script>
            """, unsafe_allow_html=True)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 고급 설정 (메모리가 있을 때만)
    if memory_client:
        st.markdown('<div class="sidebar-item">', unsafe_allow_html=True)
        if st.button("🗑️ 모든 기억 삭제", key="delete_memory", use_container_width=True):
            try:
                memories = get_all_memories(user_id)
                for memory in memories:
                    if memory.get('id'):
                        memory_client.delete(memory.get('id'))
                st.toast("모든 기억을 삭제했어요!", icon="✅")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"삭제 실패: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 하단 정보
    st.markdown("""
    <div style="padding: 1rem; text-align: center; color: #9ca3af; font-size: 11px; border-top: 1px solid #e5e7eb; margin-top: 1rem;">
        AI 비교 비서 v1.0
    </div>
    """, unsafe_allow_html=True)
