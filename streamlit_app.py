import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sympy as sp
import pandas as pd

# --- 1. KHỞI TẠO CẤU HÌNH & SESSION STATE ---
st.set_page_config(
    page_title="MathOS Ultra Web", 
    layout="wide", 
    page_icon="🌐"
)

# Hàm Reset (Đưa mọi thứ về trạng thái ban đầu)
def reset_system():
    st.session_state.raw_input = "a*x**2, sin(b*x + c)"
    st.session_state.z_input = "exp(-(x**2 + y**2)/a)"
    st.session_state.val_a = 1.0
    st.session_state.val_b = 1.0
    st.session_state.val_c = 0.0
    # FIX: Đảm bảo x_range luôn là một tuple để không lỗi subscriptable
    st.session_state.x_range = (-10.0, 10.0)

if 'raw_input' not in st.session_state:
    reset_system()

# --- 2. THANH ĐIỀU HƯỚNG (SIDEBAR) ---
with st.sidebar:
    st.title("♾️ MathOS Ultra")
    
    if st.button("🔄 Reset Toàn Bộ", width='stretch'):
        reset_system()
        st.rerun()
    
    st.divider()
    app_mode = st.selectbox("Chọn chế độ làm việc:", ["📈 Đồ thị 2D & Giải tích", "🧊 Mô phỏng 3D Surface"])
    
    st.subheader("🕹️ Điều khiển tham số")
    a = st.slider("Biến số a:", -10.0, 10.0, key="val_a")
    b = st.slider("Biến số b:", -10.0, 10.0, key="val_b")
    c = st.slider("Biến số c:", -10.0, 10.0, key="val_c")
    params = {'a': a, 'b': b, 'c': c}

    st.divider()
    st.subheader("📚 Thư viện nhanh")
    lib = {
        "Mặc định": "a*x**2, sin(b*x + c)",
        "Hàm Sigmoid": "1/(1 + exp(-a*x))",
        "Sóng tắt dần": "exp(-0.1*x) * sin(b*x)",
        "Bậc 3 phức hợp": "a*x**3 + b*x**2 + c"
    }
    selected_lib = st.selectbox("Chọn hàm mẫu:", list(lib.keys()))
    if st.button("Nạp hàm mẫu", width='stretch'):
        st.session_state.raw_input = lib[selected_lib]
        st.rerun()

# --- 3. XỬ LÝ LOGIC TOÁN HỌC ---
x_sym, y_sym = sp.symbols('x y')

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🚀 Omni Math Engine - Web Portal")

if app_mode == "📈 Đồ thị 2D & Giải tích":
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("Cài đặt hàm")
        eq_text = st.text_area("Nhập các hàm f(x) (cách nhau bằng dấu phẩy):", key="raw_input").replace("^", "**")
        calc_mode = st.radio("Phân tích:", ["Gốc", "Đạo hàm f'", "Tích phân ∫"])
        # FIX: Dòng này cực kỳ quan trọng, giá trị mặc định phải là tuple để st.slider tạo ra 2 đầu kéo
        x_lim = st.slider("Phạm vi trục X:", -100.0, 100.0, value=st.session_state.x_range, key="x_range")
        show_points = st.toggle("Hiển thị cực trị", value=True)

    with col1:
        try:
            eq_list = [e.strip() for e in eq_text.split(",") if e.strip()]
            # FIX: x_lim[0] và x_lim[1] bây giờ đã an toàn
            x_vals = np.linspace(x_lim[0], x_lim[1], 1000)
            fig = go.Figure()
            stats_table = []

            for eq in eq_list:
                try:
                    expr = sp.parse_expr(eq).subs(params)
                    if calc_mode == "Đạo hàm f'": expr = sp.diff(expr, x_sym)
                    elif calc_mode == "Tích phân ∫": expr = sp.integrate(expr, x_sym)
                    
                    f_np = sp.lambdify(x_sym, expr, "numpy")
                    y_vals = f_np(x_vals)
                    if isinstance(y_vals, (int, float, np.float64)): y_vals = np.full_like(x_vals, y_vals)
                    
                    stats_table.append({
                        "Hàm số": eq,
                        "Max Y": np.max(y_vals),
                        "Min Y": np.min(y_vals),
                        "Trung bình": np.mean(y_vals)
                    })

                    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, name=f"f(x)={eq}", line=dict(width=3)))
                    
                    if show_points and calc_mode == "Gốc":
                        try:
                            d1 = sp.diff(expr, x_sym)
                            roots = sp.solve(d1, x_sym)
                            for r in roots:
                                if r.is_real and x_lim[0] <= r <= x_lim[1]:
                                    ry = float(expr.subs(x_sym, float(r)))
                                    fig.add_trace(go.Scatter(x=[float(r)], y=[ry], mode='markers', 
                                                           marker=dict(size=10, color='yellow'), name="Cực trị"))
                        except: pass
                except Exception as inner_e:
                    st.error(f"Lỗi cú pháp tại hàm '{eq}'")

            fig.update_layout(template="plotly_dark", height=600, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, width='stretch')
        except Exception as outer_e:
            st.warning("Vui lòng kiểm tra lại định dạng nhập liệu.")

    st.divider()
    st.subheader("📊 Bảng phân tích dữ liệu chuyên sâu")
    if stats_table:
        df = pd.DataFrame(stats_table)
        st.dataframe(df, width='stretch')
        st.download_button("📥 Tải báo cáo CSV", df.to_csv(index=False), "math_report.csv", width='stretch')

else: # --- CHẾ ĐỘ 3D ---
    st.subheader("Mô phỏng bề mặt 3D")
    z_in = st.text_input("Nhập hàm z = f(x, y):", key="z_input").replace("^", "**")
    
    res = 60
    x_3d = np.linspace(-10, 10, res)
    y_3d = np.linspace(-10, 10, res)
    X, Y = np.meshgrid(x_3d, y_3d)
    
    try:
        expr_3d = sp.parse_expr(z_in).subs(params)
        f_3d = sp.lambdify((x_sym, y_sym), expr_3d, "numpy")
        Z = f_3d(X, Y)
        
        fig3d = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Viridis')])
        fig3d.update_layout(template="plotly_dark", height=700, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig3d, width='stretch')
        
        st.info(f"💡 Phân tích 3D: Với a={a}, b={b}, c={c}, hình dáng bề mặt thay đổi dựa trên các hệ số co giãn tương ứng.")
    except:
        st.warning("Vui lòng nhập hàm 3D hợp lệ (Ví dụ: sin(x)*cos(y) + a)")

st.markdown("---")
st.caption("© 2026 MathOS Web Portal | Optimized for High-Performance Computation | Created by an AI-assisted Human 🇻🇳")
