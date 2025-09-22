import streamlit as st
import matplotlib.pyplot as plt
import koreanize_matplotlib
from fpdf import FPDF
from io import BytesIO
import base64

# --- 페이지 설정 ---
st.set_page_config(
    page_title="데이터 탐정단 공식 설립 보고서",
    page_icon="📂",
    layout="wide"
)

# --- PDF 생성을 위한 클래스 ---
class PDF(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-15)
        self.set_font('NanumGothic', '', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(state, chart_image):
    pdf = PDF()
    
    # 한글 폰트 추가
    try:
        # koreanize_matplotlib이 캐시한 폰트 경로를 사용하거나 직접 경로를 지정해야 합니다.
        # Streamlit Cloud 배포 시에는 폰트 파일을 함께 업로드해야 합니다.
        # 여기서는 koreanize_matplotlib이 설치한 폰트를 사용하도록 시도합니다.
        import koreanize_matplotlib
        font_path = koreanize_matplotlib.get_font_path()
        pdf.add_font('NanumGothic', '', font_path, uni=True)
        pdf.add_font('NanumGothic', 'B', font_path, uni=True)
    except Exception as e:
        st.error(f"한글 폰트를 로드하는 데 실패했습니다. PDF 생성이 어려울 수 있습니다. 오류: {e}")
        # 대체 폰트 설정 (한글 깨짐)
        pdf.set_font("Arial", size=12)

    pdf.add_page()
    
    # 1. 제목
    pdf.set_font('NanumGothic', 'B', 24)
    pdf.cell(0, 15, '📂 데이터 탐정단 공식 설립 보고서', border=1, ln=True, align='C')
    pdf.set_font('NanumGothic', 'B', 14)
    pdf.set_text_color(190, 18, 60)
    pdf.cell(0, 10, '[TOP SECRET - 대외비]', ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # 2. 프로필
    pdf.set_font('NanumGothic', 'B', 18)
    pdf.cell(0, 10, '1. 우리 탐정 사무소 프로필', ln=True, border='B')
    pdf.ln(5)
    pdf.set_font('NanumGothic', 'B', 12)
    pdf.cell(60, 10, '🕵️‍♂️ 사무소 이름 (Codename)', border=1)
    pdf.set_font('NanumGothic', '', 12)
    pdf.cell(0, 10, state.agency_name, border=1, ln=True)
    pdf.set_font('NanumGothic', 'B', 12)
    pdf.cell(60, 10, '🗣️ 우리 팀의 구호 (Slogan)', border=1)
    pdf.set_font('NanumGothic', '', 12)
    pdf.cell(0, 10, state.agency_slogan, border=1, ln=True)
    pdf.ln(10)

    # 3. 팀원
    pdf.set_font('NanumGothic', 'B', 18)
    pdf.cell(0, 10, '👥 소속 탐정 및 역할', ln=True, border='B')
    pdf.ln(5)
    pdf.set_font('NanumGothic', 'B', 12)
    pdf.cell(95, 10, '이름', border=1, align='C')
    pdf.cell(95, 10, '역할', border=1, align='C', ln=True)
    pdf.set_font('NanumGothic', '', 12)
    for member in state.members:
        pdf.cell(95, 10, member['name'], border=1)
        pdf.cell(95, 10, member['role'], border=1, ln=True)
    pdf.ln(10)
    
    # 4. 윤리 강령
    pdf.set_font('NanumGothic', 'B', 18)
    pdf.cell(0, 10, '2. 데이터 탐정 윤리 강령 서약', ln=True, border='B')
    pdf.ln(5)
    pdf.set_font('NanumGothic', '', 12)
    pdf.multi_cell(0, 8, "제1조: 우리는 개인의 사생활을 캐지 않으며, 친구의 비밀을 존중한다.\n제2조: 우리는 오직 모두를 위한 해결책을 찾기 위해, 주인이 누군지 알 수 없는 '익명의 데이터'만을 다룬다.")
    pdf.set_font('NanumGothic', 'B', 12)
    pledge_text = '✔️ 서약함' if state.pledged else '❌ 서약하지 않음'
    pdf.cell(0, 10, f'서약 여부: {pledge_text}', ln=True)
    pdf.ln(10)

    # 5. 수사 계획
    pdf.set_font('NanumGothic', 'B', 18)
    pdf.cell(0, 10, '3. 초기 수사 계획', ln=True, border='B')
    pdf.ln(5)
    pdf.set_font('NanumGothic', 'B', 12)
    pdf.cell(60, 10, '영역', border=1, align='C')
    pdf.cell(0, 10, '계획 내용', border=1, align='C', ln=True)
    pdf.set_font('NanumGothic', '', 12)
    pdf.cell(60, 10, '🍚 급식/식사', border=1)
    pdf.multi_cell(0, 10, state.case1, border=1)
    pdf.cell(60, 10, '📚 학습/수업', border=1)
    pdf.multi_cell(0, 10, state.case2, border=1)
    pdf.cell(60, 10, '🛡️ 시설/안전', border=1)
    pdf.multi_cell(0, 10, state.case3, border=1)
    pdf.ln(10)
    
    # 6. 차트 이미지
    pdf.set_font('NanumGothic', 'B', 18)
    pdf.cell(0, 10, '📊 초기 수사 계획 분포도', ln=True, border='B', align='C')
    pdf.ln(5)
    pdf.image(chart_image, x = 10, w=pdf.w - 20)

    # PDF를 바이트로 반환
    return pdf.output(dest='S').encode('latin-1')

# --- 세션 상태 초기화 ---
if 'members' not in st.session_state:
    st.session_state.members = [{'name': '', 'role': '기록 탐정'}]

# --- UI 그리기 ---
st.title("📂 데이터 탐정단 공식 설립 보고서")
st.markdown("<p class='top-secret' style='text-align:center; color: #be123c; font-weight:700;'>[TOP SECRET - 대외비]</p>", unsafe_allow_html=True)
st.markdown("---")


# --- 1. 프로필 섹션 ---
with st.container():
    st.header("1. 우리 탐정 사무소 프로필")
    st.session_state.agency_name = st.text_input("🕵️‍♂️ 사무소 이름 (Codename)", placeholder="우리 팀의 멋진 코드네임을 여기에!")
    st.session_state.agency_slogan = st.text_input("🗣️ 우리 팀의 구호 (Slogan)", placeholder="우리 팀의 각오가 담긴 구호를 여기에!")


# --- 2. 팀원 섹션 ---
with st.container():
    st.header("👥 소속 탐정 및 역할")
    
    for i, member in enumerate(st.session_state.members):
        cols = st.columns([3, 3, 1])
        st.session_state.members[i]['name'] = cols[0].text_input(f"탐정 이름 {i+1}", value=member['name'], key=f"name_{i}")
        st.session_state.members[i]['role'] = cols[1].selectbox(f"역할 {i+1}", ['기록 탐정', '발표 탐정', '자료 탐정', '시간 탐정'], index=['기록 탐정', '발표 탐정', '자료 탐정', '시간 탐정'].index(member['role']), key=f"role_{i}")
        
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


# --- 3. 윤리 강령 섹션 ---
with st.container():
    st.header("2. 데이터 탐정 윤리 강령 서약")
    st.info("""
    **제1조:** 우리는 개인의 사생활을 캐지 않으며, 친구의 비밀을 존중한다.  
    **제2조:** 우리는 오직 모두를 위한 해결책을 찾기 위해, 주인이 누군지 알 수 없는 '익명의 데이터'만을 다룬다.
    """)
    st.session_state.pledged = st.checkbox("위 강령을 준수하며, 오직 진실과 우리 학교의 발전을 위해 데이터를 사용할 것을 서약합니다.")

# --- 4. 수사 계획 및 차트 섹션 ---
st.markdown("---")
st.header("3. 초기 수사 계획")

col1, col2 = st.columns(2)

with col1:
    st.subheader("사건 계획 수립")
    st.markdown("우리 학교를 1% 더 좋게 만들기 위해, 어떤 사건들을 수사할지 계획해 봅시다.")
    st.session_state.case1 = st.text_area("🍚 급식/식사 영역", placeholder="예: 급식 줄이 너무 길다")
    st.session_state.case2 = st.text_area("📚 학습/수업 영역", placeholder="예: 도서관에 신간이 부족하다")
    st.session_state.case3 = st.text_area("🛡️ 시설/안전 영역", placeholder="예: 복도에서 뛰는 학생이 많아 위험하다")

with col2:
    st.subheader("📊 초기 수사 계획 분포도")
    st.markdown("우리의 수사 계획이 각 영역에 어떻게 분포되어 있는지 한눈에 확인해 보세요!")

    # 차트 데이터 생성
    labels = ['급식/식사', '학습/수업', '시설/안전']
    sizes = [
        1 if len(st.session_state.case1.strip()) > 0 else 0,
        1 if len(st.session_state.case2.strip()) > 0 else 0,
        1 if len(st.session_state.case3.strip()) > 0 else 0,
    ]
    colors = ['rgba(22, 163, 74, 0.7)', 'rgba(2, 132, 199, 0.7)', 'rgba(185, 28, 28, 0.7)']
    
    # Matplotlib으로 도넛 차트 그리기
    fig, ax = plt.subplots()
    
    if sum(sizes) > 0:
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops=dict(width=0.4))
    else:
        ax.pie([1], labels=['계획 없음'], colors=['#e5e7eb'])

    ax.axis('equal')  # 원형 유지
    
    # 차트를 이미지로 변환
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    st.image(buf)


# --- PDF 다운로드 버튼 ---
st.markdown("---")
st.header("보고서 저장")

# PDF 생성
pdf_bytes = generate_pdf(st.session_state, buf)

# 다운로드 버튼
st.download_button(
    label="📂 Google Docs로 저장하기 (PDF)",
    data=pdf_bytes,
    file_name=f"{st.session_state.agency_name}_설립보고서.pdf" if st.session_state.agency_name else "탐정단_설립보고서.pdf",
    mime="application/pdf",
)
st.caption("버튼을 눌러 지금까지 작성한 내용을 PDF 파일로 다운로드하세요. 이 파일을 구글 드라이브에 올리거나 내용을 복사하여 구글 독스에서 사용할 수 있습니다.")
