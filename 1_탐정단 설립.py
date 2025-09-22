import streamlit as st
import matplotlib.pyplot as plt
import koreanize_matplotlib
from io import BytesIO
import textwrap

# --- 페이지 설정 ---
st.set_page_config(
    page_title="데이터 탐정단 공식 설립 보고서",
    page_icon="📂",
    layout="wide"
)

# --- 보고서 이미지 생성 함수 (PDF 대체, 최종 오류 해결 버전) ---
def generate_report_image(state, chart_fig):
    """
    입력된 모든 정보와 차트를 포함하는 단일 보고서 이미지를 생성합니다.
    """
    # A4 비율에 가깝게 이미지 크기 설정 (가로 8.27인치, 세로 11.69인치)
    fig = plt.figure(figsize=(8.27, 11.69), dpi=150)
    fig.patch.set_facecolor('white') # 배경색 흰색

    # 전체 제목
    fig.suptitle("📂 데이터 탐정단 공식 설립 보고서", fontsize=22, weight='bold', y=0.97)
    plt.figtext(0.5, 0.93, "[TOP SECRET - 대외비]", ha="center", fontsize=14, color='#be123c', weight='bold')

    # y_pos: 텍스트를 그릴 현재 y 위치 (1.0이 맨 위, 0.0이 맨 아래)
    y_pos = 0.88

    # --- 1. 프로필 ---
    plt.figtext(0.1, y_pos, "1. 우리 탐정 사무소 프로필", fontsize=18, weight='bold', ha='left')
    y_pos -= 0.05
    plt.figtext(0.1, y_pos, f"🕵️‍♂️ 사무소 이름 (Codename): {state.get('agency_name', '입력되지 않음')}", fontsize=12, ha='left')
    y_pos -= 0.04
    plt.figtext(0.1, y_pos, f"🗣️ 우리 팀의 구호 (Slogan): {state.get('agency_slogan', '입력되지 않음')}", fontsize=12, ha='left')
    y_pos -= 0.06

    # --- 2. 팀원 ---
    plt.figtext(0.1, y_pos, "👥 소속 탐정 및 역할", fontsize=18, weight='bold', ha='left')
    y_pos -= 0.05
    for member in state.get('members', []):
        plt.figtext(0.12, y_pos, f"• {member.get('name', '이름 없음')} ({member.get('role', '역할 없음')})", fontsize=12, ha='left')
        y_pos -= 0.03
    y_pos -= 0.03

    # --- 3. 윤리 강령 ---
    plt.figtext(0.1, y_pos, "2. 데이터 탐정 윤리 강령 서약", fontsize=18, weight='bold', ha='left')
    y_pos -= 0.05
    pledge_text = '✔️ 서약함' if state.get('pledged', False) else '❌ 서약하지 않음'
    plt.figtext(0.12, y_pos, f"서약 여부: {pledge_text}", fontsize=12, weight='bold', ha='left')
    y_pos -= 0.06

    # --- 4. 수사 계획 ---
    plt.figtext(0.1, y_pos, "3. 초기 수사 계획", fontsize=18, weight='bold', ha='left')
    y_pos -= 0.02
    
    plans = [
        f"🍚 급식/식사: {state.get('case1', '계획 없음')}",
        f"📚 학습/수업: {state.get('case2', '계획 없음')}",
        f"🛡️ 시설/안전: {state.get('case3', '계획 없음')}"
    ]
    
    for plan in plans:
        # 긴 텍스트가 이미지를 넘어가지 않도록 자동으로 줄바꿈 처리
        wrapped_text = "\n".join(textwrap.wrap(plan, width=75))
        plt.figtext(0.12, y_pos, wrapped_text, fontsize=12, va='top', ha='left')
        y_pos -= (wrapped_text.count('\n') + 1) * 0.02 + 0.02

    # --- 5. 차트 삽입 ---
    plt.figtext(0.5, y_pos, "📊 초기 수사 계획 분포도", ha="center", fontsize=18, weight='bold')
    y_pos -= 0.01
    
    # 차트 이미지를 임시 버퍼에 저장
    chart_buf = BytesIO()
    chart_fig.savefig(chart_buf, format='png', bbox_inches='tight', dpi=150)
    chart_buf.seek(0)

    # 이미지 삽입을 위한 축(axes) 생성. [left, bottom, width, height]
    chart_ax = fig.add_axes([0.15, 0.05, 0.7, 0.3]) 
    img = plt.imread(chart_buf)
    chart_ax.imshow(img)
    chart_ax.axis('off') # 불필요한 축 숨기기

    # 최종 보고서 이미지를 바이트로 변환하여 반환
    img_buf = BytesIO()
    fig.savefig(img_buf, format='png', bbox_inches='tight')
    plt.close(fig)
    plt.close(chart_fig)
    img_buf.seek(0)
    
    return img_buf

# --- 세션 상태 초기화 ---
if 'members' not in st.session_state:
    st.session_state.members = [{'name': '', 'role': '기록 탐정'}]

# --- UI 그리기 ---
st.title("📂 데이터 탐정단 공식 설립 보고서")
st.markdown("<p style='text-align:center; color: #be123c; font-weight:700;'>[TOP SECRET - 대외비]</p>", unsafe_allow_html=True)
st.markdown("---")

with st.container():
    st.header("1. 우리 탐정 사무소 프로필")
    st.session_state.agency_name = st.text_input("🕵️‍♂️ 사무소 이름 (Codename)", st.session_state.get('agency_name', ''), placeholder="우리 팀의 멋진 코드네임을 여기에!")
    st.session_state.agency_slogan = st.text_input("🗣️ 우리 팀의 구호 (Slogan)", st.session_state.get('agency_slogan', ''), placeholder="우리 팀의 각오가 담긴 구호를 여기에!")

with st.container():
    st.header("👥 소속 탐정 및 역할")
    
    for i, member in enumerate(st.session_state.members):
        cols = st.columns([3, 3, 1])
        member['name'] = cols[0].text_input(f"탐정 이름 {i+1}", value=member['name'], key=f"name_{i}")
        member['role'] = cols[1].selectbox(f"역할 {i+1}", ['기록 탐정', '발표 탐정', '자료 탐정', '시간 탐정'], index=['기록 탐정', '발표 탐정', '자료 탐정', '시간 탐정'].index(member['role']), key=f"role_{i}")
        
        if cols[2].button("삭제", key=f"del_{i}"):
            if len(st.session_state.members) > 1:
                st.session_state.members.pop(i)
                st.rerun()
            else:
                st.warning("최소 1명의 탐정은 필요합니다.")

    if st.button("+ 탐정 추가하기"):
        if len(st.session_state.members) < 5:
            st.session_state.members.append({'name': '', 'role': '기록 탐정'})
            st.rerun()
        else:
            st.warning("최대 5명의 탐정까지 추가할 수 있습니다.")

with st.container():
    st.header("2. 데이터 탐정 윤리 강령 서약")
    st.info("""
    **제1조:** 우리는 개인의 사생활을 캐지 않으며, 친구의 비밀을 존중한다.  
    **제2조:** 우리는 오직 모두를 위한 해결책을 찾기 위해, 주인이 누군지 알 수 없는 '익명의 데이터'만을 다룬다.
    """)
    st.session_state.pledged = st.checkbox("위 강령을 준수하며, 오직 진실과 우리 학교의 발전을 위해 데이터를 사용할 것을 서약합니다.", value=st.session_state.get('pledged', False))

st.markdown("---")
st.header("3. 초기 수사 계획")

col1, col2 = st.columns(2)

with col1:
    st.subheader("사건 계획 수립")
    st.markdown("우리 학교를 1% 더 좋게 만들기 위해, 어떤 사건들을 수사할지 계획해 봅시다.")
    st.session_state.case1 = st.text_area("🍚 급식/식사 영역", st.session_state.get('case1', ''), placeholder="예: 급식 줄이 너무 길다")
    st.session_state.case2 = st.text_area("📚 학습/수업 영역", st.session_state.get('case2', ''), placeholder="예: 도서관에 신간이 부족하다")
    st.session_state.case3 = st.text_area("🛡️ 시설/안전 영역", st.session_state.get('case3', ''), placeholder="예: 복도에서 뛰는 학생이 많아 위험하다")

# 차트 생성을 별도의 fig 객체로 관리
chart_fig, ax = plt.subplots(figsize=(5, 5))
labels = ['급식/식사', '학습/수업', '시설/안전']
sizes = [
    1 if len(st.session_state.case1.strip()) > 0 else 0,
    1 if len(st.session_state.case2.strip()) > 0 else 0,
    1 if len(st.session_state.case3.strip()) > 0 else 0,
]
colors = [(22/255, 163/255, 74/255, 0.7), (2/255, 132/255, 199/255, 0.7), (185/255, 28/255, 28/255, 0.7)]

if sum(sizes) > 0:
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops=dict(width=0.4))
else:
    ax.pie([1], labels=['계획 없음'], colors=['#e5e7eb'])
ax.axis('equal')

with col2:
    st.subheader("📊 초기 수사 계획 분포도")
    st.markdown("우리의 수사 계획이 각 영역에 어떻게 분포되어 있는지 한눈에 확인해 보세요!")
    st.pyplot(chart_fig)


st.markdown("---")
st.header("보고서 저장")

# --- 보고서 이미지 다운로드 버튼 ---
if st.button("보고서 이미지로 저장"):
    with st.spinner('보고서 이미지를 생성 중입니다...'):
        image_bytes = generate_report_image(st.session_state, chart_fig)
        
        if image_bytes:
            file_name = f"{st.session_state.agency_name}_설립보고서.png" if st.session_state.agency_name else "탐정단_설립보고서.png"
            st.download_button(
                label="🖼️ 보고서 이미지 다운로드",
                data=image_bytes,
                file_name=file_name,
                mime="image/png"
            )

