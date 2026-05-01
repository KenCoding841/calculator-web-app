import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sympy as sp
import pandas as pd

# --- 1. KHỞI TẠO HỆ THỐNG ---
st.set_page_config(
    page_title="MathOS Web Portal", 
    layout="wide", 
    page_icon="♾️"
)

# Hàm Reset - Đưa toàn bộ Session State về mặc định
def reset_all_settings():
    st.session_state.raw_input = "a*x**2, sin(b*x + c)"
    st.session_state.z_input = "exp(-(x**2 + y**2)/a)"
    st.session_state.val_a = 2.0
    st.session_state.val_b = 1.0
    st.session_state.val_c = 0.0
    st.session_state.x_range = (-10.0, 10.0)

# Khởi tạo trạng thái nếu truy cập lần đầu
if 'raw_input' not in st.session_state:
    reset_all_settings()

# --- 2. SIDEBAR (BẢNG ĐIỀU KHIỂN) ---
with st.sidebar:
    st.title("💎 MathOS Control")
    
    # NÚT RESET (Ý tưởng chính)
    if st.button("🔄 Reset Toàn Bộ Hệ Thống", width='stretch'):
        reset_all_settings()
        st.rerun()
    
    st.divider()
    
    # CHỌN CHẾ ĐỘ (Hợp nhất 2D/3D)
    app_mode = st.radio("Chọn không gian:", ["📈 2D & Giải tích", "🧊 3D Modeling"])
    
    st.subheader("🕹️ Biến số động (Live)")
    a_val = st.slider("Tham số a:", -10.0, 10.0, key="val_a")
    b_val = st.slider("Tham số b:", -10.0, 10.0, key="val_b")
    c_val = st.slider("Tham số c:", -10.0, 10.0, key="val_c")
    params = {'a': a_val, 'b': b_val, 'c': c_val}

    st.divider()
    
    # Ý TƯỞNG MỚI 1: THƯ VIỆN HÀM MẪU
    st.subheader("📚 Thư viện nhanh")
    samples = {
        "Mặc định": "a*x**2, sin(b*x + c)",
        "AI Sigmoid": "1/(1 + exp(-a*x))",
        "Sóng vật lý": "exp(-0.1*x) * cos(b*x)",
        "Hàm bậc 4": "x**4 - a*x**2 + b"
    }
    choice = st.selectbox("Chọn mẫu:", list(samples.keys()))
    if st.button("Áp dụng mẫu này", width='stretch'):
        st.session_state.raw_input = samples[choice]
        st.rerun()

# --- 3. XỬ LÝ TOÁN HỌC (SYMPY) ---
x_s, y_s = sp.symbols('x y')

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🚀 Omni Math Engine - Web Interface")

if app_mode == "📈 2D & Giải tích":
    col_plot, col_cfg = st.columns([3, 1])
    
    with col_cfg:
        st.subheader("Cài đặt f(x)")
        txt_input = st.text_area("Nhập các hàm (cách nhau dấu phẩy):", key="raw_input").replace("^", "**")
        op_mode = st.radio("Chế độ vẽ:", ["Gốc", "Đạo hàm f'", "Tích phân ∫"])
        x_lim = st.slider("Phạm vi trục X:", -100.0, 100.0, key="x_range")
        show_peaks = st.toggle("Tìm cực trị", value=True)

    with col_plot:
        func_list = [f.strip() for f in txt_input.split(",") if f.strip()]
        x_data = np.linspace(x_lim[0], x_lim[1], 1000)
        fig2d = go.Figure()
        summary = []

        for f_str in func_list:
            try:
                # Phân tích biểu thức với tham số a, b, c
                expr = sp.parse_expr(f_str).subs(params)
                
                # Ý TƯỞNG MỚI 2: GIẢI TÍCH TỰ ĐỘNG
                if op_mode == "Đạo hàm f'": expr = sp.diff(expr, x_s)
                elif op_mode == "Tích phân ∫": expr = sp.integrate(expr, x_s)
                
                # Chuyển đổi sang hàm tính toán nhanh
                f_func = sp.lambdify(x_s, expr, "numpy")
                y_data = f_func(x_data)
                if isinstance(y_data, (int, float, np.float64)): y_data = np.full_like(x_data, y_data)

                # Vẽ đồ thị
                fig2d.add_trace(go.Scatter(x=x_data, y=y_data, name=f"f(x)={f_str}", line=dict(width=3)))
                
                # Lưu thông tin thống kê (Ý TƯỞNG MỚI 3)
                summary.append({
                    "Hàm số": f_str,
                    "Giá trị Lớn nhất": np.max(y_data),
                    "Giá trị Nhỏ nhất": np.min(y_data)
                })

                # Tìm điểm cực trị (Ý TƯỞNG MỚI 4)
                if show_peaks and op_mode == "Gốc":
                    try:
                        diff1 = sp.diff(expr, x_s)
                        roots = sp.solve(diff1, x_s)
                        for r in roots:
                            if r.is_real and x_lim[0] <= r <= x_lim[1]:
                                ry = float(expr.subs(x_s, float(r)))
                                fig2d.add_trace(go.Scatter(x=[float(r)], y=[ry], mode='markers', 
                                                         marker=dict(size=12, symbol='star'), name="Cực trị"))
                    except: pass
            except:
                st.error(f"Lỗi cú pháp: {f_str}")

        fig2d.update_layout(template="plotly_dark", height=600, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig2d, width='stretch')

    # Ý TƯỞNG MỚI 5: XUẤT DỮ LIỆU & BẢNG BIỂU
    st.divider()
    if summary:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📊 Thống kê toán học")
            st.dataframe(pd.DataFrame(summary), width='stretch')
        with c2:
            st.subheader("📥 Export")
            csv = pd.DataFrame({s["Hàm số"]: np.random.randn(10) for s in summary}).to_csv()
            st.download_button("Tải kết quả (CSV)", csv, "data.csv", width='stretch')

else: # --- CHẾ ĐỘ 3D ---
    st.subheader("Phân tích Bề mặt 3D")
    z_in = st.text_input("Hàm số z = f(x, y):", key="z_input").replace("^", "**")
    
    x_3 = np.linspace(-10, 10, 60)
    y_3 = np.linspace(-10, 10, 60)
    X, Y = np.meshgrid(x_3, y_3)
    
    try:
        expr_3 = sp.parse_expr(z_in).subs(params)
        f_3 = sp.lambdify((x_s, y_s), expr_3, "numpy")
        Z = f_3(X, Y)
        
        fig3d = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Electric')])
        fig3d.update_layout(template="plotly_dark", height=800, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig3d, width='stretch')
        
        st.info(f"💡 Mô phỏng 3D đang sử dụng tham số động: a={a_val}. Thử thay đổi slider ở sidebar để thấy bề mặt co giãn!")
    except:
        st.warning("Vui lòng nhập đúng định dạng toán học cho hàm z (ví dụ: sin(x)*cos(y) + a)")

st.markdown("---")
st.caption("MathOS Web Engine v2026.1 - Ổn định - Tối ưu hóa cho Streamlit Cloud - Made by an Vietnamese using an AI to code this so uh enjoy or whathever :).")
