import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sympy as sp
import pandas as pd

# --- 1. CONFIG & SESSION ---
st.set_page_config(page_title="Math Web 2026", layout="wide", page_icon="📈")

def reset_all():
    st.session_state.raw_input = "a*x**2, sin(b*x + c)"
    st.session_state.z_input = "sin(a*x) * cos(b*y)"
    st.session_state.v_a = 2.0
    st.session_state.v_b = 1.0
    st.session_state.v_c = 0.0
    st.session_state.x_range = (-10.0, 10.0)

if 'raw_input' not in st.session_state:
    reset_all()

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("💎 Control Panel")
    if st.button("🔄 Reset System", width='stretch'):
        reset_all()
        st.rerun()
    
    st.divider()
    mode = st.radio("Chế độ:", ["📊 2D & Giải tích", "🧊 3D Surface"])
    
    st.subheader("🕹️ Biến số động")
    a = st.slider("Tham số a", -10.0, 10.0, key="v_a")
    b = st.slider("Tham số b", -10.0, 10.0, key="v_b")
    c = st.slider("Tham số c", -10.0, 10.0, key="v_c")
    params = {'a': a, 'b': b, 'c': c}

# --- 3. MAIN INTERFACE ---
st.title("🚀 Omni Math Engine")

x_s, y_s = sp.symbols('x y')

if mode == "📊 2D & Giải tích":
    col_main, col_sub = st.columns([3, 1])
    
    with col_sub:
        st.subheader("Cài đặt")
        eq_in = st.text_area("Hàm f(x) (cách nhau bằng dấu phẩy):", key="raw_input").replace("^", "**")
        op = st.radio("Phân tích:", ["Gốc", "Đạo hàm f'", "Tích phân ∫"])
        xr = st.slider("Phạm vi X:", -100.0, 100.0, key="x_range")
        show_p = st.toggle("Hiện cực trị", value=True)

    with col_main:
        eq_list = [e.strip() for e in eq_in.split(",") if e.strip()]
        x_v = np.linspace(xr[0], xr[1], 1000)
        fig = go.Figure()
        stats = []

        for eq in eq_list:
            try:
                expr = sp.parse_expr(eq).subs(params)
                if op == "Đạo hàm f'": expr = sp.diff(expr, x_s)
                elif op == "Tích phân ∫": expr = sp.integrate(expr, x_s)
                
                f_np = sp.lambdify(x_s, expr, "numpy")
                y_v = f_np(x_v)
                if isinstance(y_v, (int, float, np.float64)): y_v = np.full_like(x_v, y_v)
                
                fig.add_trace(go.Scatter(x=x_v, y=y_v, name=f"f(x)={eq}", line=dict(width=3)))
                stats.append({"Hàm": eq, "Max": np.max(y_v), "Min": np.min(y_v)})

                if show_p and op == "Gốc":
                    try:
                        d1 = sp.diff(expr, x_s)
                        pts = sp.solve(d1, x_s)
                        for p in pts:
                            if p.is_real and xr[0] <= p <= xr[1]:
                                py = float(expr.subs(x_s, float(p)))
                                fig.add_trace(go.Scatter(x=[float(p)], y=[py], mode='markers', marker=dict(size=10, color='yellow'), name="Cực trị"))
                    except: pass
            except Exception as e:
                st.error(f"Lỗi hàm {eq}: {e}")

        fig.update_layout(template="plotly_dark", height=600, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width='stretch')

    st.divider()
    if stats:
        st.subheader("📊 Bảng thống kê")
        st.dataframe(pd.DataFrame(stats), width='stretch')

else: # 3D MODE
    st.subheader("Mô phỏng bề mặt 3D")
    z_in = st.text_input("Hàm z = f(x, y):", key="z_input").replace("^", "**")
    
    x3 = np.linspace(-10, 10, 50)
    y3 = np.linspace(-10, 10, 50)
    X, Y = np.meshgrid(x3, y3)
    
    try:
        e3 = sp.parse_expr(z_in).subs(params)
        f3 = sp.lambdify((x_s, y_s), e3, "numpy")
        Z = f3(X, Y)
        fig3 = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Viridis')])
        fig3.update_layout(template="plotly_dark", height=750)
        st.plotly_chart(fig3, width='stretch')
    except:
        st.info("Nhập hàm số để vẽ 3D (Ví dụ: sin(x)*cos(y) + a)")

st.caption("MathOS Cloud 2026 | Engine: SymPy + Plotly | Optimized for stretch display")
